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

  const platforms = ['google', 'trustpilot'] as const;
  const platformStats: Record<string, {
    newReviews: { reviewer_name: string; rating: number; review_text: string }[];
    deletedReviews: { reviewer_name: string; rating: number; review_text: string }[];
    totalBefore: number;
    totalAfter: number;
  }> = {};

  for (const platform of platforms) {
    const newRows = await sql`
      SELECT reviewer_name, rating, review_text
      FROM reviews
      WHERE platform = ${platform}
        AND first_seen_date >= ${weekStartStr}
        AND first_seen_date <= ${weekEndStr}
      ORDER BY first_seen_date DESC
    `;

    const deletedRows = await sql`
      SELECT reviewer_name, rating, review_text
      FROM reviews
      WHERE platform = ${platform}
        AND status = 'deleted'
        AND deleted_date >= ${weekStartStr}
        AND deleted_date <= ${weekEndStr}
      ORDER BY deleted_date DESC
    `;

    const startSnap = await sql`
      SELECT total_count FROM daily_snapshots
      WHERE platform = ${platform} AND snapshot_date <= ${weekStartStr}
      ORDER BY snapshot_date DESC LIMIT 1
    `;
    const endSnap = await sql`
      SELECT total_count FROM daily_snapshots
      WHERE platform = ${platform} AND snapshot_date <= ${weekEndStr}
      ORDER BY snapshot_date DESC LIMIT 1
    `;

    platformStats[platform] = {
      newReviews: newRows as { reviewer_name: string; rating: number; review_text: string }[],
      deletedReviews: deletedRows as { reviewer_name: string; rating: number; review_text: string }[],
      totalBefore: startSnap.length > 0 ? Number(startSnap[0].total_count) : 0,
      totalAfter: endSnap.length > 0 ? Number(endSnap[0].total_count) : 0,
    };
  }

  await sendWeeklySummary({
    weekStart: weekStart.toLocaleDateString('tr-TR', { day: '2-digit', month: 'long', year: 'numeric' }),
    weekEnd: weekEnd.toLocaleDateString('tr-TR', { day: '2-digit', month: 'long', year: 'numeric' }),
    google: platformStats['google'],
    trustpilot: platformStats['trustpilot'],
  });

  await sql`
    INSERT INTO weekly_email_log (
      week_start, week_end,
      new_reviews, deleted_reviews,
      total_before, total_after
    ) VALUES (
      ${weekStartStr}, ${weekEndStr},
      ${platformStats['google'].newReviews.length + platformStats['trustpilot'].newReviews.length},
      ${platformStats['google'].deletedReviews.length + platformStats['trustpilot'].deletedReviews.length},
      ${platformStats['google'].totalBefore + platformStats['trustpilot'].totalBefore},
      ${platformStats['google'].totalAfter + platformStats['trustpilot'].totalAfter}
    )
  `;

  return NextResponse.json({ success: true });
}
