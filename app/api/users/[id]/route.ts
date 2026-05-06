import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import sql from '@/lib/db';
import bcrypt from 'bcryptjs';
import { z } from 'zod';

export const dynamic = 'force-dynamic';

async function requireSuperAdmin() {
  const session = await getServerSession(authOptions);
  if (!session) return { error: NextResponse.json({ error: 'Unauthorized' }, { status: 401 }), session: null };
  if ((session.user as { role: string }).role !== 'superadmin') {
    return { error: NextResponse.json({ error: 'Forbidden' }, { status: 403 }), session: null };
  }
  return { error: null, session };
}

const PatchSchema = z.object({
  role: z.enum(['viewer', 'superadmin']).optional(),
  password: z.string().min(8).optional(),
});

export async function PATCH(
  req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { error } = await requireSuperAdmin();
  if (error) return error;

  const { id } = await params;
  const body = await req.json();
  const parsed = PatchSchema.safeParse(body);
  if (!parsed.success) {
    return NextResponse.json({ error: 'Invalid input' }, { status: 400 });
  }

  const { role, password } = parsed.data;

  if (role) {
    await sql`UPDATE users SET role = ${role} WHERE id = ${Number(id)}`;
  }
  if (password) {
    const hash = await bcrypt.hash(password, 10);
    await sql`
      UPDATE users SET password_hash = ${hash}, must_change_password = true
      WHERE id = ${Number(id)}
    `;
  }

  const updated = await sql`
    SELECT id, email, role, must_change_password, created_at FROM users WHERE id = ${Number(id)}
  `;
  return NextResponse.json({ user: updated[0] });
}

export async function DELETE(
  req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { error, session } = await requireSuperAdmin();
  if (error) return error;

  const { id } = await params;

  const selfRows = await sql`SELECT id FROM users WHERE email = ${session!.user.email!}`;
  if (selfRows.length > 0 && String(selfRows[0].id) === id) {
    return NextResponse.json({ error: 'Cannot delete own account' }, { status: 400 });
  }

  await sql`DELETE FROM users WHERE id = ${Number(id)}`;
  return NextResponse.json({ success: true });
}
