import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import { neon } from '@neondatabase/serverless';

export const dynamic = 'force-dynamic';

type Row = Record<string, unknown>;

// eslint-disable-next-line @typescript-eslint/no-explicit-any
async function query(db: any, text: string, params: (string | number)[]): Promise<Row[]> {
  const result = await db.query(text, params);
  return (result.rows ?? result) as Row[];
}

export async function GET(req: NextRequest) {
  const session = await getServerSession(authOptions);
  if (!session) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const db = neon(process.env.DATABASE_URL!) as any;
  const { searchParams } = req.nextUrl;
  const status = searchParams.get('status') || '';
  const rating = searchParams.get('rating') || '';
  const search = searchParams.get('search') || '';
  const platform = searchParams.get('platform') || '';
  const dateFrom = searchParams.get('date_from') || '';
  const dateTo = searchParams.get('date_to') || '';
  const page = Math.max(1, Number(searchParams.get('page') || '1'));
  const limit = Math.min(100, Math.max(1, Number(searchParams.get('limit') || '50')));
  const offset = (page - 1) * limit;

  const conditions: string[] = [];
  const params: (string | number)[] = [];
  let idx = 1;

  if (status === 'online' || status === 'deleted') {
    conditions.push(`status = $${idx++}`);
    params.push(status);
  }
  // Date range: filter by first_seen_date (new reviews) OR deleted_date in range
  if (dateFrom) {
    conditions.push(`(first_seen_date >= $${idx} OR (deleted_date IS NOT NULL AND deleted_date >= $${idx}))`);
    params.push(dateFrom);
    idx++;
  }
  if (dateTo) {
    conditions.push(`(first_seen_date <= $${idx} OR (deleted_date IS NOT NULL AND deleted_date <= $${idx}))`);
    params.push(dateTo);
    idx++;
  }
  if (rating && !isNaN(Number(rating))) {
    conditions.push(`rating = $${idx++}`);
    params.push(Number(rating));
  }
  if (search) {
    conditions.push(`(reviewer_name ILIKE $${idx} OR review_text ILIKE $${idx})`);
    params.push(`%${search}%`);
    idx++;
  }
  if (platform === 'google' || platform === 'trustpilot') {
    conditions.push(`platform = $${idx++}`);
    params.push(platform);
  }

  const where = conditions.length > 0 ? `WHERE ${conditions.join(' AND ')}` : '';

  const countRows = await query(db, `SELECT COUNT(*) as c FROM reviews ${where}`, params);
  const total = Number(countRows[0]?.c ?? 0);

  const reviews = await query(
    db,
    `SELECT * FROM reviews ${where} ORDER BY first_seen_date DESC LIMIT $${idx} OFFSET $${idx + 1}`,
    [...params, limit, offset]
  );

  const pf = platform === 'google' || platform === 'trustpilot' ? platform : null;
  const pfWhere = pf ? `AND platform = $1` : '';

  const onlineRows = await query(db, `SELECT COUNT(*) as c FROM reviews WHERE status = 'online' ${pfWhere}`, pf ? [pf] : []);
  const deletedRows = await query(db, `SELECT COUNT(*) as c FROM reviews WHERE status = 'deleted' ${pfWhere}`, pf ? [pf] : []);

  return NextResponse.json({
    reviews,
    total,
    online_count: Number(onlineRows[0]?.c ?? 0),
    deleted_count: Number(deletedRows[0]?.c ?? 0),
    pages: Math.ceil(total / limit),
  });
}
