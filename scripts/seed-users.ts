import { neon } from '@neondatabase/serverless';
import bcrypt from 'bcryptjs';
import * as dotenv from 'dotenv';
import { resolve } from 'path';

dotenv.config({ path: resolve(__dirname, '../.env.local') });

const sql = neon(process.env.DATABASE_URL!);

async function seed() {
  await sql`DROP TABLE IF EXISTS users CASCADE`;
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

  const users = [
    { email: 'alper.yildirim@esvitaclinic.com', password: 'esvita1234', role: 'viewer' },
    { email: 'metin.sarac@esvitaclinic.com', password: 'esvita1234', role: 'viewer' },
    { email: 'selman@esvitaclinic.com', password: 'esvita1234', role: 'viewer' },
    { email: 'ahmet.esen@esvitaclinic.com', password: 'esvita1234', role: 'viewer' },
    { email: 'info@esvitaclinic.com', password: 'esvita1234', role: 'superadmin' },
  ];

  for (const user of users) {
    const hash = await bcrypt.hash(user.password, 10);
    await sql`
      INSERT INTO users (email, password_hash, role, must_change_password)
      VALUES (${user.email}, ${hash}, ${user.role}, true)
      ON CONFLICT (email) DO NOTHING
    `;
    console.log(`Seeded: ${user.email}`);
  }

  console.log('Seed complete.');
  process.exit(0);
}

seed().catch(err => {
  console.error('Seed failed:', err);
  process.exit(1);
});
