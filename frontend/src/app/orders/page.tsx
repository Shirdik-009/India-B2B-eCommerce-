'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { api, type OrderListResponse } from '@/lib/api';
import { useAuth } from '@/lib/auth';

export default function OrdersPage() {
  const { token, user } = useAuth();
  const [data, setData] = useState<OrderListResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) {
      setLoading(false);
      return;
    }
    api
      .get<OrderListResponse>('/api/orders?page=1&page_size=50', token)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [token]);

  const orders = data?.orders ?? [];

  if (!user) {
    return (
      <div className="text-center">
        <p className="text-slate-600">Sign in to view your orders.</p>
        <Link href="/login" className="mt-4 inline-block text-primary-600 hover:underline">
          Sign in
        </Link>
      </div>
    );
  }

  if (loading) {
    return <div className="animate-pulse rounded-xl bg-slate-100 p-12 text-center">Loading orders...</div>;
  }

  if (orders.length === 0) {
    return (
      <div className="text-center">
        <p className="text-slate-600">You have no orders yet.</p>
        <Link href="/products" className="mt-4 inline-block text-primary-600 hover:underline">
          Browse products
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-900">My orders</h1>
      <div className="space-y-4">
        {orders.map((order) => (
          <div key={order.id} className="card overflow-hidden">
            <div className="flex items-center justify-between border-b border-slate-200 bg-slate-50 px-4 py-3">
              <span className="font-medium text-slate-900">
                Order #{order.display_number ?? order.id}
              </span>
              <span className="rounded-full bg-primary-100 px-2 py-1 text-xs font-medium text-primary-800">
                {order.status}
              </span>
            </div>
            <ul className="divide-y divide-slate-200 px-4">
              {order.items.map((item) => (
                <li key={item.id} className="py-2 text-sm text-slate-700">
                  {item.product_title} × {item.quantity} — ₹{Number(item.subtotal).toLocaleString('en-IN')}
                </li>
              ))}
            </ul>
            <div className="flex justify-between border-t border-slate-200 px-4 py-3 text-sm">
              <span className="text-slate-500">
                {new Date(order.created_at).toLocaleDateString('en-IN')}
              </span>
              <span className="font-semibold text-slate-900">
                Total: ₹{Number(order.total_amount).toLocaleString('en-IN')}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
