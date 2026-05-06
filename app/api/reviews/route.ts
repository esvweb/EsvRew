import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import sql from '@/lib/db';

export async function GET(req: NextRequest) {
  const session = await getServerSession(authOptions);
  if (!session) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

  const { searchParams } = req.nextUrl;
  const status = searchParams.get('status') || '';
  const rating = searchParams.get('rating') || '';
  const search = searchParams.get('search') || '';
  const page = Math.max(1, Number(searchParams.get('page') || '1'));
  const limit = Math.min(100, Math.max(1, Number(searchParams.get('limit') || '50')));
  const offset = (page - 1) * limit;

  let reviews: Record<string, unknown>[];
  let totalCount: number;

  const statusFilter = status === 'online' || status === 'deleted' ? status : null;
  const ratingFilter = rating && !isNaN(Number(rating)) ? Number(rating) : null;
  const searchFilter = search ? `%${search}%` : null;

  if (statusFilter && ratingFilter && searchFilter) {
    reviews = await sql`SELECT * FROM reviews WHERE status = ${statusFilter} AND rating = ${ratingFilter} AND (reviewer_name ILIKE ${searchFilter} OR review_text ILIKE ${searchFilter}) ORDER BY first_seen_date DESC LIMIT ${limit} OFFSET ${offset}`;
    const r = await sql`SELECT COUNT(*) as c FROM reviews WHERE status = ${statusFilter} AND rating = ${ratingFilter} AND (reviewer_name ILIKE ${searchFilter} OR review_text ILIKE ${searchFilter})`;
    totalCount = Number(r[0].c);
  } else if (statusFilter && ratingFilter) {
    reviews = await sql`SELECT * FROM reviews WHERE status = ${statusFilter} AND rating = ${ratingFilter} ORDER BY first_seen_date DESC LIMIT ${limit} OFFSET ${offset}`;
    const r = await sql`SELECT COUNT(*) as c FROM reviews WHERE status = ${statusFilter} AND rating = ${ratingFilter}`;
    totalCount = Number(r[0].c);
  } else if (statusFilter && searchFilter) {
    reviews = await sql`SELECT * FROM reviews WHERE status = ${statusFilter} AND (reviewer_name ILIKE ${searchFilter} OR review_text ILIKE ${searchFilter}) ORDER BY first_seen_date DESC LIMIT ${limit} OFFSET ${offset}`;
    const r = await sql`SELECT COUNT(*) as c FROM reviews WHERE status = ${statusFilter} AND (reviewer_name ILIKE ${searchFilter} OR review_text ILIKE ${searchFilter})`;
    totalCount = Number(r[0].c);
  } else if (ratingFilter && searchFilter) {
    reviews = await sql`SELECT * FROM reviews WHERE rating = ${ratingFilter} AND (reviewer_name ILIKE ${searchFilter} OR review_text ILIKE ${searchFilter}) ORDER BY first_seen_date DESC LIMIT ${limit} OFFSET ${offset}`;
    const r = await sql`SELECT COUNT(*) as c FROM reviews WHERE rating = ${ratingFilter} AND (reviewer_name ILIKE ${searchFilter} OR review_text ILIKE ${searchFilter})`;
    totalCount = Number(r[0].c);
  } else if (statusFilter) {
    reviews = await sql`SELECT * FROM reviews WHERE status = ${statusFilter} ORDER BY first_seen_date DESC LIMIT ${limit} OFFSET ${offset}`;
    const r = await sql`SELECT COUNT(*) as c FROM reviews WHERE status = ${statusFilter}`;
    totalCount = Number(r[0].c);
  } else if (ratingFilter) {
    reviews = await sql`SELECT * FROM reviews WHERE rating = ${ratingFilter} ORDER BY first_seen_date DESC LIMIT ${limit} OFFSET ${offset}`;
    const r = await sql`SELECT COUNT(*) as c FROM reviews WHERE rating = ${ratingFilter}`;
    totalCount = Number(r[0].c);
  } else if (searchFilter) {
    reviews = await sql`SELECT * FROM reviews WHERE reviewer_name ILIKE ${searchFilter} OR review_text ILIKE ${searchFilter} ORDER BY first_seen_date DESC LIMIT ${limit} OFFSET ${offset}`;
    const r = await sql`SELECT COUNT(*) as c FROM reviews WHERE reviewer_name ILIKE ${searchFilter} OR review_text ILIKE ${searchFilter}`;
    totalCount = Number(r[0].c);
  } else {
    reviews = await sql`SELECT * FROM reviews ORDER BY first_seen_date DESC LIMIT ${limit} OFFSET ${offset}`;
    const r = await sql`SELECT COUNT(*) as c FROM reviews`;
    totalCount = Number(r[0].c);
  }

  const onlineCount = await sql`SELECT COUNT(*) as c FROM reviews WHERE status = 'online'`;
  const deletedCount = await sql`SELECT COUNT(*) as c FROM reviews WHERE status = 'deleted'`;

  return NextResponse.json({
    reviews,
    total: totalCount,
    online_count: Number(onlineCount[0].c),
    deleted_count: Number(deletedCount[0].c),
    pages: Math.ceil(totalCount / limit),
  });
}
