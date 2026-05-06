'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { signOut } from 'next-auth/react';

interface Props {
  email: string;
  role: string;
}

export default function Sidebar({ email, role }: Props) {
  const pathname = usePathname();

  const links = [
    { href: '/dashboard', label: 'Dashboard', icon: '📊' },
    ...(role === 'superadmin'
      ? [{ href: '/dashboard/users', label: 'Kullanıcılar', icon: '👥' }]
      : []),
  ];

  return (
    <aside className="fixed left-0 top-0 bottom-0 w-64 bg-white border-r border-gray-200 flex flex-col">
      <div className="p-6 border-b border-gray-100">
        <h1 className="font-bold text-gray-900 text-lg leading-tight">Esvita</h1>
        <p className="text-xs text-gray-500 mt-0.5">Review Monitor</p>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        {links.map(link => (
          <Link
            key={link.href}
            href={link.href}
            className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
              pathname === link.href
                ? 'bg-blue-50 text-blue-700'
                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
            }`}
          >
            <span>{link.icon}</span>
            {link.label}
          </Link>
        ))}
      </nav>

      <div className="p-4 border-t border-gray-100">
        <div className="mb-3">
          <p className="text-xs text-gray-500 truncate">{email}</p>
          <p className="text-xs font-medium text-gray-700 mt-0.5">
            {role === 'superadmin' ? (
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-700">
                Superadmin
              </span>
            ) : (
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-600">
                Görüntüleyici
              </span>
            )}
          </p>
        </div>
        <button
          onClick={() => signOut({ callbackUrl: '/login' })}
          className="w-full text-left text-sm text-gray-500 hover:text-red-600 transition-colors px-1"
        >
          Çıkış Yap
        </button>
      </div>
    </aside>
  );
}
