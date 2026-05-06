import { neon } from '@neondatabase/serverless';

const sql = neon(process.env.DATABASE_URL!);

export async function initDb() {
  await sql`
    CREATE TABLE IF NOT EXISTS users (
      id SERIAL PRIMARY KEY,
      email TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      role TEXT DEFAULT 'viewer' CHECK (role IN ('viewer', 'superadmin')),
      must_change_password BOOLEAN DEFAULT true,
      created_at TIMESTAMPTZ DEFAULT NOW()
    )
  `;

  await sql`
    CREATE TABLE IF NOT EXISTS reviews (
      id SERIAL PRIMARY KEY,
      review_id TEXT UNIQUE NOT NULL,
      reviewer_name TEXT,
      rating INTEGER,
      review_text TEXT,
      first_seen_date DATE NOT NULL,
      last_seen_date DATE,
      status TEXT DEFAULT 'online' CHECK (status IN ('online', 'deleted')),
      deleted_date DATE
    )
  `;

  await sql`
    CREATE TABLE IF NOT EXISTS daily_snapshots (
      id SERIAL PRIMARY KEY,
      snapshot_date DATE NOT NULL UNIQUE,
      review_ids TEXT[] NOT NULL,
      total_count INTEGER,
      created_at TIMESTAMPTZ DEFAULT NOW()
    )
  `;

  await sql`
    CREATE TABLE IF NOT EXISTS weekly_email_log (
      id SERIAL PRIMARY KEY,
      sent_at TIMESTAMPTZ DEFAULT NOW(),
      week_start DATE,
      week_end DATE,
      new_reviews INTEGER,
      deleted_reviews INTEGER,
      total_before INTEGER,
      total_after INTEGER
    )
  `;
}

export { sql };
export default sql;
