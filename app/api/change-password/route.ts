import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import sql from '@/lib/db';
import bcrypt from 'bcryptjs';

export const dynamic = 'force-dynamic';
import { z } from 'zod';

const Schema = z.object({
  password: z.string().min(8),
});

export async function POST(req: NextRequest) {
  const session = await getServerSession(authOptions);
  if (!session) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

  const body = await req.json();
  const parsed = Schema.safeParse(body);
  if (!parsed.success) {
    return NextResponse.json({ error: 'Şifre en az 8 karakter olmalıdır.' }, { status: 400 });
  }

  const hash = await bcrypt.hash(parsed.data.password, 10);
  await sql`
    UPDATE users SET password_hash = ${hash}, must_change_password = false
    WHERE email = ${session.user.email!}
  `;

  return NextResponse.json({ success: true });
}
