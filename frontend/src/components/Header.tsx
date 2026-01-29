'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/lib/auth';
import clsx from 'clsx';

const nav = [
  { href: '/', label: 'Home' },
  { href: '/products', label: 'Products' },
  { href: '/cart', label: 'Cart' },
  { href: '/orders', label: 'My Orders' },
  { href: '/chat', label: 'Chat' },
];

export function Header() {
  const pathname = usePathname();
  const { user, loading, logout } = useAuth();

  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Link href="/" className="text-xl font-bold text-primary-600">
          India B2B
        </Link>
        <nav className="flex items-center gap-6">
          {nav.map(({ href, label }) => (
            <Link
              key={href}
              href={href}
              className={clsx(
                'text-sm font-medium transition-colors',
                pathname === href ? 'text-primary-600' : 'text-slate-600 hover:text-slate-900'
              )}
            >
              {label}
            </Link>
          ))}
          {!loading && (
            <>
              {user ? (
                <>
                  <Link
                    href="/profile"
                    className={clsx(
                      'text-sm font-medium',
                      pathname === '/profile' ? 'text-primary-600' : 'text-slate-600 hover:text-slate-900'
                    )}
                  >
                    Profile
                  </Link>
                  {(user.role === 'seller' || user.role === 'admin') && (
                    <>
                      <Link
                        href="/seller/orders"
                        className={clsx(
                          'text-sm font-medium',
                          pathname === '/seller/orders' ? 'text-primary-600' : 'text-slate-600 hover:text-slate-900'
                        )}
                      >
                        Orders received
                      </Link>
                      <Link
                        href="/seller/products"
                        className={clsx(
                          'text-sm font-medium',
                          pathname === '/seller/products' ? 'text-primary-600' : 'text-slate-600 hover:text-slate-900'
                        )}
                      >
                        My Products
                      </Link>
                    </>
                  )}
                  <button
                    type="button"
                    onClick={logout}
                    className="text-sm font-medium text-slate-600 hover:text-slate-900"
                  >
                    Logout
                  </button>
                </>
              ) : (
                <>
                  <Link href="/login" className="btn-secondary">
                    Sign in
                  </Link>
                  <Link href="/register" className="btn-primary">
                    Join Free
                  </Link>
                </>
              )}
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
