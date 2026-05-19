import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';
import sql from '@/lib/db';
import { sendDeleteAlert, sendModificationAlert } from '@/lib/email';

export const dynamic = 'force-dynamic';

const ReviewSchema = z.object({
  review_id: z.string(),
  reviewer_name: z.string().optional(),
  rating: z.number().int().min(1).max(5),
  review_text: z.string().optional(),
});

const BodySchema = z.object({
  reviews: z.array(ReviewSchema),
  snapshot_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
  platform: z.enum(['google', 'trustpilot']).default('google'),
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

  const { reviews, snapshot_date, platform } = parsed.data;
  const today = snapshot_date;

  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);
  const yesterdayStr = yesterday.toISOString().split('T')[0];

  const yesterdaySnapshot = await sql`
    SELECT review_ids FROM daily_snapshots
    WHERE snapshot_date = ${yesterdayStr} AND platform = ${platform}
  `;

  const todayIds = reviews.map(r => r.review_id);
  const yesterdayIds: string[] = yesterdaySnapshot.length > 0 ? yesterdaySnapshot[0].review_ids : [];

  const newIds = todayIds.filter(id => !yesterdayIds.includes(id));

  const suspiciouslyLow = yesterdayIds.length > 20 && todayIds.length < yesterdayIds.length * 0.7;
  const deletedIds = suspiciouslyLow ? [] : yesterdayIds.filter(id => !todayIds.includes(id));
  if (suspiciouslyLow) {
    console.warn(`Skipping deletion check [${platform}]: today=${todayIds.length}, yesterday=${yesterdayIds.length}`);
  }

  const modifiedReviews: { reviewer_name: string; rating: number; review_text: string; old_rating: number; old_text: string }[] = [];

  for (const review of reviews) {
    if (newIds.includes(review.review_id)) {
      // New review — insert
      await sql`
        INSERT INTO reviews (review_id, reviewer_name, rating, review_text, first_seen_date, last_seen_date, status, platform)
        VALUES (${review.review_id}, ${review.reviewer_name ?? null}, ${review.rating}, ${review.review_text ?? null}, ${today}, ${today}, 'online', ${platform})
        ON CONFLICT (review_id) DO UPDATE SET last_seen_date = ${today}, status = 'online'
      `;
    } else {
      // Existing review — check for modifications
      const existing = await sql`
        SELECT rating, review_text FROM reviews WHERE review_id = ${review.review_id}
      `;

      if (existing.length > 0) {
        const old = existing[0];
        const textChanged = review.review_text && old.review_text && review.review_text !== old.review_text;
        const ratingChanged = review.rating !== old.rating;

        if (textChanged || ratingChanged) {
          // Record modification: save original values on first modification only
          await sql`
            UPDATE reviews SET
              last_seen_date = ${today},
              status = 'online',
              deleted_date = NULL,
              rating = ${review.rating},
              review_text = ${review.review_text ?? null},
              modified_date = ${today},
              original_text = COALESCE(original_text, ${old.review_text}),
              original_rating = COALESCE(original_rating, ${old.rating})
            WHERE review_id = ${review.review_id}
          `;

          modifiedReviews.push({
            reviewer_name: review.reviewer_name || 'Anonim',
            rating: review.rating,
            review_text: review.review_text || '',
            old_rating: Number(old.rating),
            old_text: old.review_text || '',
          });
        } else {
          // No change — just update last_seen_date
          await sql`
            UPDATE reviews SET last_seen_date = ${today}, status = 'online', deleted_date = NULL
            WHERE review_id = ${review.review_id}
          `;
        }
      }
    }
  }

  for (const id of deletedIds) {
    await sql`
      UPDATE reviews SET status = 'deleted', deleted_date = ${today}
      WHERE review_id = ${id}
    `;
  }

  await sql`
    INSERT INTO daily_snapshots (snapshot_date, review_ids, total_count, platform)
    VALUES (${today}, ${todayIds}, ${todayIds.length}, ${platform})
    ON CONFLICT (snapshot_date, platform) DO UPDATE
    SET review_ids = ${todayIds}, total_count = ${todayIds.length}
  `;

  // Send deletion alert
  if (deletedIds.length > 0) {
    const deletedRows = await sql`
      SELECT reviewer_name, rating, review_text FROM reviews WHERE review_id = ANY(${deletedIds})
    `;
    const onlineCount = await sql`SELECT COUNT(*) as c FROM reviews WHERE status = 'online' AND platform = ${platform}`;
    const deletedCount = await sql`SELECT COUNT(*) as c FROM reviews WHERE status = 'deleted' AND platform = ${platform}`;
    try {
      await sendDeleteAlert(
        deletedRows as { reviewer_name: string; rating: number; review_text: string }[],
        Number(onlineCount[0].c),
        Number(deletedCount[0].c),
        platform
      );
    } catch (e) { console.error('Delete email failed:', e); }
  }

  // Send modification alert
  if (modifiedReviews.length > 0) {
    try {
      await sendModificationAlert(modifiedReviews, platform);
    } catch (e) { console.error('Modification email failed:', e); }
  }

  return NextResponse.json({
    new: newIds.length,
    deleted: deletedIds.length,
    modified: modifiedReviews.length,
    total: todayIds.length,
    platform,
  });
}
