'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { api } from '@/lib/api';
import { useAuth } from '@/lib/auth';

export default function NewProductPage() {
  const router = useRouter();
  const { token, user } = useAuth();
  const [form, setForm] = useState({
    title: '',
    description: '',
    price: '',
    min_order_quantity: 1,
    unit: 'piece',
    category_id: null as number | null,
    image_urls: [] as string[],
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  if (!user || (user.role !== 'seller' && user.role !== 'admin')) {
    return (
      <div className="text-center">
        <p className="text-slate-600">Seller access required.</p>
        <Link href="/profile" className="mt-4 inline-block text-primary-600 hover:underline">
          Back
        </Link>
      </div>
    );
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const price = Number(form.price);
      if (Number.isNaN(price) || price < 0) throw new Error('Invalid price');
      await api.post(
        '/api/products',
        {
          title: form.title,
          description: form.description || null,
          price: form.price,
          min_order_quantity: form.min_order_quantity,
          unit: form.unit,
          category_id: form.category_id,
          image_urls: form.image_urls,
        },
        token!
      );
      router.push('/seller/products');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create product');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-lg">
      <h1 className="text-2xl font-bold text-slate-900">Add product</h1>
      <form onSubmit={handleSubmit} className="mt-6 space-y-4">
        {error && (
          <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
        )}
        <div>
          <label className="block text-sm font-medium text-slate-700">Title *</label>
          <input
            type="text"
            required
            value={form.title}
            onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
            className="input mt-1"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700">Description</label>
          <textarea
            rows={4}
            value={form.description}
            onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
            className="input mt-1"
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700">Price (₹) *</label>
            <input
              type="number"
              step="0.01"
              min="0"
              required
              value={form.price}
              onChange={(e) => setForm((f) => ({ ...f, price: e.target.value }))}
              className="input mt-1"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700">Min order qty</label>
            <input
              type="number"
              min="1"
              value={form.min_order_quantity}
              onChange={(e) => setForm((f) => ({ ...f, min_order_quantity: Number(e.target.value) || 1 }))}
              className="input mt-1"
            />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700">Unit</label>
          <input
            type="text"
            value={form.unit}
            onChange={(e) => setForm((f) => ({ ...f, unit: e.target.value }))}
            className="input mt-1"
            placeholder="piece, kg, box, etc."
          />
        </div>
        <div className="flex gap-4">
          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? 'Creating...' : 'Create product'}
          </button>
          <Link href="/seller/products" className="btn-secondary">
            Cancel
          </Link>
        </div>
      </form>
    </div>
  );
}
