'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useAuth } from '@/lib/auth';

export default function RegisterPage() {
  const [form, setForm] = useState({
    email: '',
    password: '',
    full_name: '',
    phone: '',
    company_name: '',
    role: 'buyer',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await register({
        email: form.email,
        password: form.password,
        full_name: form.full_name,
        phone: form.phone || undefined,
        company_name: form.company_name || undefined,
        role: form.role,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-md">
      <h1 className="text-2xl font-bold text-slate-900">Create account</h1>
      <p className="mt-1 text-slate-600">Join India B2B as buyer or supplier</p>
      <form onSubmit={handleSubmit} className="mt-8 space-y-6">
        {error && (
          <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}
        <div>
          <label className="block text-sm font-medium text-slate-700">I want to</label>
          <div className="mt-2 flex gap-4">
            <label className="flex items-center gap-2">
              <input
                type="radio"
                name="role"
                value="buyer"
                checked={form.role === 'buyer'}
                onChange={(e) => setForm((f) => ({ ...f, role: e.target.value }))}
                className="h-4 w-4 text-primary-600"
              />
              Buy
            </label>
            <label className="flex items-center gap-2">
              <input
                type="radio"
                name="role"
                value="seller"
                checked={form.role === 'seller'}
                onChange={(e) => setForm((f) => ({ ...f, role: e.target.value }))}
                className="h-4 w-4 text-primary-600"
              />
              Sell / Supply
            </label>
          </div>
        </div>
        <div>
          <label htmlFor="full_name" className="block text-sm font-medium text-slate-700">
            Full name *
          </label>
          <input
            id="full_name"
            type="text"
            required
            value={form.full_name}
            onChange={(e) => setForm((f) => ({ ...f, full_name: e.target.value }))}
            className="input mt-1"
            placeholder="Your name"
          />
        </div>
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-slate-700">
            Email *
          </label>
          <input
            id="email"
            type="email"
            required
            value={form.email}
            onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
            className="input mt-1"
            placeholder="you@company.com"
          />
        </div>
        <div>
          <label htmlFor="password" className="block text-sm font-medium text-slate-700">
            Password * (min 8 characters)
          </label>
          <input
            id="password"
            type="password"
            required
            minLength={8}
            value={form.password}
            onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))}
            className="input mt-1"
          />
        </div>
        <div>
          <label htmlFor="phone" className="block text-sm font-medium text-slate-700">
            Phone
          </label>
          <input
            id="phone"
            type="tel"
            value={form.phone}
            onChange={(e) => setForm((f) => ({ ...f, phone: e.target.value }))}
            className="input mt-1"
            placeholder="+91 ..."
          />
        </div>
        <div>
          <label htmlFor="company_name" className="block text-sm font-medium text-slate-700">
            Company name
          </label>
          <input
            id="company_name"
            type="text"
            value={form.company_name}
            onChange={(e) => setForm((f) => ({ ...f, company_name: e.target.value }))}
            className="input mt-1"
            placeholder="Your business name"
          />
        </div>
        <button type="submit" disabled={loading} className="btn-primary w-full">
          {loading ? 'Creating account...' : 'Create account'}
        </button>
        <p className="text-center text-sm text-slate-600">
          Already have an account?{' '}
          <Link href="/login" className="font-medium text-primary-600 hover:text-primary-700">
            Sign in
          </Link>
        </p>
      </form>
    </div>
  );
}
