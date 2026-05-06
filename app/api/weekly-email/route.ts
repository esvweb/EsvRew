import { NextRequest, NextResponse } from 'next/server';
import sql from '@/lib/db';
import { sendWeeklySummary } from '@/lib/email';

export const dynamic = 'force-dynamic';

export async function POST(req: NextRequest) {
  const auth = req.headers.get('authorization');
  if (auth !== `Bearer ${process.env.SCRAPER_SECRET}`) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const today = new Date();
  const weekEnd = new Date(today);
  weekEnd.setDate(today.getDate() - 1);
  const weekStart = new Date(weekEnd);
  weekStart.setDate(weekEnd.getDate() - 6);

  const weekStartStr = weekStart.toISOString().split('T')[0];
  const weekEndStr = weekEnd.toISOString().split('T')[0];

  const newReviews = await sql`
    SELECT COUNT(*) as c FROM reviews
    WHERE first_seen_date >= ${weekStartStr} AND first_seen_date <= ${weekEndStr}
  `;

  const deletedReviews = await sql`
    SELECT COUNT(*) as c FROM reviews
    WHERE deleted_date >= ${weekStartStr} AND deleted_date <= ${weekEndStr}
  `;

  const startSnapshot = await sql`
    SELECT total_count FROM daily_snapshots WHERE snapshot_date = ${weekStartStr}
  `;
  const endSnapshot = await sql`
    SELECT total_count FROM daily_snapshots
    WHERE snapshot_date <= ${weekEndStr}
    ORDER BY snapshot_date DESC LIMIT 1
  `;

  const totalBefore = startSnapshot.length > 0 ? startSnapshot[0].total_count : 0;
  const totalAfter = endSnapshot.length > 0 ? endSnapshot[0].total_count : 0;

  const stats = {
    weekStart: weekStart.toLocaleDateString('tr-TR', { day: '2-digit', month: 'long', year: 'numeric' }),
    weekEnd: weekEnd.toLocaleDateString('tr-TR', { day: '2-digit', month: 'long', year: 'numeric' }),
    newReviews: Number(newReviews[0].c),
    deletedReviews: Number(deletedReviews[0].c),
    totalBefore,
    totalAfter,
  };

  await sendWeeklySummary(stats);

  await sql`
    INSERT INTO weekly_email_log (week_start, week_end, new_reviews, deleted_reviews, total_before, total_after)
    VALUES (${weekStartStr}, ${weekEndStr}, ${stats.newReviews}, ${stats.deletedReviews}, ${totalBefore}, ${totalAfter})
  `;

  return NextResponse.json({ success: true, stats });
}
