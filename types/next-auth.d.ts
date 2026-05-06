import NextAuth from 'next-auth';

declare module 'next-auth' {
  interface User {
    role: string;
    mustChangePassword: boolean;
  }
  interface Session {
    user: {
      name?: string | null;
      email?: string | null;
      image?: string | null;
      role: string;
      mustChangePassword: boolean;
    };
  }
}

declare module 'next-auth/jwt' {
  interface JWT {
    role: string;
    mustChangePassword: boolean;
  }
}
