'use client';

import { useAuth } from '@/lib/auth';
import Link from 'next/link';

export default function ProfilePage() {
  const { user } = useAuth();

  if (!user) {
    return (
      <div className="text-center">
        <p className="text-slate-600">Sign in to view your profile.</p>
        <Link href="/login" className="mt-4 inline-block text-primary-600 hover:underline">
          Sign in
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-lg space-y-6">
      <h1 className="text-2xl font-bold text-slate-900">Profile</h1>
      <div className="card p-6">
        <dl className="space-y-3">
          <div>
            <dt className="text-sm font-medium text-slate-500">Name</dt>
            <dd className="text-slate-900">{user.full_name}</dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-slate-500">Email</dt>
            <dd className="text-slate-900">{user.email}</dd>
          </div>
          {user.phone && (
            <div>
              <dt className="text-sm font-medium text-slate-500">Phone</dt>
              <dd className="text-slate-900">{user.phone}</dd>
            </div>
          )}
          {user.company_name && (
            <div>
              <dt className="text-sm font-medium text-slate-500">Company</dt>
              <dd className="text-slate-900">{user.company_name}</dd>
            </div>
          )}
          <div>
            <dt className="text-sm font-medium text-slate-500">Role</dt>
            <dd className="text-slate-900 capitalize">{user.role}</dd>
          </div>
        </dl>
        {(user.role === 'seller' || user.role === 'admin') && (
          <Link href="/seller/products" className="mt-6 inline-block text-primary-600 hover:underline">
            Manage my products →
          </Link>
        )}
      </div>
    </div>
  );
}
