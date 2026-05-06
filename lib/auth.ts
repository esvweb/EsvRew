import { NextAuthOptions } from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';
import bcrypt from 'bcryptjs';
import sql from './db';

export const authOptions: NextAuthOptions = {
  providers: [
    CredentialsProvider({
      name: 'credentials',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) return null;

        const rows = await sql`
          SELECT id, email, password_hash, role, must_change_password
          FROM users WHERE email = ${credentials.email}
        `;

        if (rows.length === 0) return null;

        const user = rows[0];
        const valid = await bcrypt.compare(credentials.password, user.password_hash);
        if (!valid) return null;

        return {
          id: String(user.id),
          email: user.email,
          role: user.role,
          mustChangePassword: user.must_change_password,
        };
      },
    }),
  ],
  session: { strategy: 'jwt' },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.role = (user as { role: string }).role;
        token.mustChangePassword = (user as { mustChangePassword: boolean }).mustChangePassword;
      }
      // Re-read mustChangePassword from DB on every token refresh
      // so password change takes effect without re-login
      if (token.email) {
        try {
          const rows = await sql`
            SELECT must_change_password, role FROM users WHERE email = ${token.email as string}
          `;
          if (rows.length > 0) {
            token.mustChangePassword = rows[0].must_change_password;
            token.role = rows[0].role;
          }
        } catch {
          // keep existing token values on DB error
        }
      }
      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        (session.user as { role: string }).role = token.role as string;
        (session.user as { mustChangePassword: boolean }).mustChangePassword = token.mustChangePassword as boolean;
      }
      return session;
    },
  },
  pages: {
    signIn: '/login',
  },
};
