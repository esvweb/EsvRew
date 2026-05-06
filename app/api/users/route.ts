import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import sql from '@/lib/db';
import bcrypt from 'bcryptjs';
import { z } from 'zod';

async function requireSuperAdmin(req: NextRequest) {
  const session = await getServerSession(authOptions);
  if (!session) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  if ((session.user as { role: string }).role !== 'superadmin') {
    return NextResponse.json({ error: 'Forbidden' }, { status: 403 });
  }
  return null;
}

export async function GET(req: NextRequest) {
  const err = await requireSuperAdmin(req);
  if (err) return err;

  const users = await sql`
    SELECT id, email, role, must_change_password, created_at FROM users ORDER BY created_at
  `;
  return NextResponse.json({ users });
}

const CreateSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
  role: z.enum(['viewer', 'superadmin']),
});

export async function POST(req: NextRequest) {
  const err = await requireSuperAdmin(req);
  if (err) return err;

  const body = await req.json();
  const parsed = CreateSchema.safeParse(body);
  if (!parsed.success) {
    return NextResponse.json({ error: 'Invalid input', details: parsed.error }, { status: 400 });
  }

  const { email, password, role } = parsed.data;
  const hash = await bcrypt.hash(password, 10);

  try {
    const res = await sql`
      INSERT INTO users (email, password_hash, role, must_change_password)
      VALUES (${email}, ${hash}, ${role}, true)
      RETURNING id, email, role, must_change_password, created_at
    `;
    return NextResponse.json({ user: res[0] }, { status: 201 });
  } catch (e: unknown) {
    if (e instanceof Error && e.message.includes('unique')) {
      return NextResponse.json({ error: 'Email already exists' }, { status: 409 });
    }
    throw e;
  }
}
