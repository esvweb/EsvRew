import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';
import sql from '@/lib/db';
import { sendDeleteAlert } from '@/lib/email';

const ReviewSchema = z.object({
  review_id: z.string(),
  reviewer_name: z.string().optional(),
  rating: z.number().int().min(1).max(5),
  review_text: z.string().optional(),
});

const BodySchema = z.object({
  reviews: z.array(ReviewSchema),
  snapshot_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
});

export async function POST(req: NextRequest) {
  const auth = req.headers.get('authorization');
  if (auth !== `Bearer ${process.env.SCRAPER_SECRET}`) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const body = await req.json();
  const parsed = BodySchema.safeParse(body);
  if (!parsed.success) {
    return NextResponse.json({ error: 'Invalid body', details: parsed.error }, { status: 400 });
  }

  const { reviews, snapshot_date } = parsed.data;
  const today = snapshot_date;

  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);
  const yesterdayStr = yesterday.toISOString().split('T')[0];

  const yesterdaySnapshot = await sql`
    SELECT review_ids FROM daily_snapshots WHERE snapshot_date = ${yesterdayStr}
  `;

  const todayIds = reviews.map(r => r.review_id);
  const yesterdayIds: string[] = yesterdaySnapshot.length > 0 ? yesterdaySnapshot[0].review_ids : [];

  const newIds = todayIds.filter(id => !yesterdayIds.includes(id));
  const deletedIds = yesterdayIds.filter(id => !todayIds.includes(id));

  for (const review of reviews) {
    if (newIds.includes(review.review_id)) {
      await sql`
        INSERT INTO reviews (review_id, reviewer_name, rating, review_text, first_seen_date, last_seen_date, status)
        VALUES (${review.review_id}, ${review.reviewer_name ?? null}, ${review.rating}, ${review.review_text ?? null}, ${today}, ${today}, 'online')
        ON CONFLICT (review_id) DO UPDATE SET last_seen_date = ${today}, status = 'online'
      `;
    } else {
      await sql`
        UPDATE reviews SET last_seen_date = ${today} WHERE review_id = ${review.review_id}
      `;
    }
  }

  for (const id of deletedIds) {
    await sql`
      UPDATE reviews SET status = 'deleted', deleted_date = ${today}
      WHERE review_id = ${id}
    `;
  }

  await sql`
    INSERT INTO daily_snapshots (snapshot_date, review_ids, total_count)
    VALUES (${today}, ${todayIds}, ${todayIds.length})
    ON CONFLICT (snapshot_date) DO UPDATE SET review_ids = ${todayIds}, total_count = ${todayIds.length}
  `;

  if (deletedIds.length > 0) {
    const deletedRows = await sql`
      SELECT reviewer_name, rating, review_text FROM reviews WHERE review_id = ANY(${deletedIds})
    `;
    const onlineCount = await sql`SELECT COUNT(*) as c FROM reviews WHERE status = 'online'`;
    const deletedCount = await sql`SELECT COUNT(*) as c FROM reviews WHERE status = 'deleted'`;

    try {
      await sendDeleteAlert(
        deletedRows as { reviewer_name: string; rating: number; review_text: string }[],
        Number(onlineCount[0].c),
        Number(deletedCount[0].c)
      );
    } catch (e) {
      console.error('Email send failed:', e);
    }
  }

  return NextResponse.json({
    new: newIds.length,
    deleted: deletedIds.length,
    total: todayIds.length,
  });
}
