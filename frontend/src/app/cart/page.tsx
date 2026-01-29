'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { api, type CartItem } from '@/lib/api';
import { useAuth } from '@/lib/auth';

export default function CartPage() {
  const router = useRouter();
  const { token, user } = useAuth();
  const [items, setItems] = useState<CartItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [checkingOut, setCheckingOut] = useState(false);

  useEffect(() => {
    if (!token) {
      setLoading(false);
      return;
    }
    api
      .get<CartItem[]>('/api/cart', token)
      .then(setItems)
      .catch(() => setItems([]))
      .finally(() => setLoading(false));
  }, [token]);

  async function removeItem(itemId: number) {
    if (!token) return;
    try {
      await api.delete(`/api/cart/${itemId}`, token);
      setItems((prev) => prev.filter((i) => i.id !== itemId));
    } catch {
      // ignore
    }
  }

  async function checkout() {
    if (!token || !user || items.length === 0) return;
    setCheckingOut(true);
    try {
      const orderItems = items.map((i) => ({
        product_id: i.product_id,
        quantity: i.quantity,
        unit_price: i.product_price ? Number(i.product_price) : 0,
      }));
      await api.post(
        '/api/orders',
        {
          items: orderItems,
          shipping_address: 'Please update in profile',
          notes: null,
        },
        token
      );
      router.push('/orders');
    } catch {
      setCheckingOut(false);
    }
  }

  const total = items.reduce((sum, i) => sum + (i.subtotal ? Number(i.subtotal) : 0), 0);

  if (!user) {
    return (
      <div className="text-center">
        <p className="text-slate-600">Sign in to view your cart.</p>
        <Link href="/login" className="mt-4 inline-block text-primary-600 hover:underline">
          Sign in
        </Link>
      </div>
    );
  }

  if (loading) {
    return <div className="animate-pulse rounded-xl bg-slate-100 p-12 text-center">Loading cart...</div>;
  }

  if (items.length === 0) {
    return (
      <div className="text-center">
        <p className="text-slate-600">Your cart is empty.</p>
        <Link href="/products" className="mt-4 inline-block text-primary-600 hover:underline">
          Browse products
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-900">Your cart</h1>
      <div className="card overflow-hidden">
        <ul className="divide-y divide-slate-200">
          {items.map((item) => (
            <li key={item.id} className="flex items-center justify-between gap-4 p-4">
              <div>
                <Link href={`/products/${item.product_id}`} className="font-medium text-slate-900 hover:text-primary-600">
                  {item.product_title}
                </Link>
                <p className="text-sm text-slate-500">
                  Qty: {item.quantity} · ₹{item.subtotal ? Number(item.subtotal).toLocaleString('en-IN') : '—'}
                </p>
              </div>
              <button
                type="button"
                onClick={() => removeItem(item.id)}
                className="text-sm text-red-600 hover:text-red-700"
              >
                Remove
              </button>
            </li>
          ))}
        </ul>
        <div className="flex items-center justify-between border-t border-slate-200 bg-slate-50 px-4 py-4">
          <p className="text-lg font-semibold text-slate-900">
            Total: ₹{total.toLocaleString('en-IN')}
          </p>
          <button
            type="button"
            onClick={checkout}
            disabled={checkingOut}
            className="btn-primary"
          >
            {checkingOut ? 'Placing order...' : 'Proceed to checkout'}
          </button>
        </div>
      </div>
    </div>
  );
}
