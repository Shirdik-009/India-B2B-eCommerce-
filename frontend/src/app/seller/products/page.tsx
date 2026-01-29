'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { api, type Product } from '@/lib/api';
import { useAuth } from '@/lib/auth';

export default function SellerProductsPage() {
  const { token, user } = useAuth();
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) {
      setLoading(false);
      return;
    }
    api
      .get<{ total: number; page: number; page_size: number; items: Product[] }>(
        '/api/products?page=1&page_size=100&my=1',
        token
      )
      .then((res) => setProducts(res.items || []))
      .catch(() => setProducts([]))
      .finally(() => setLoading(false));
  }, [token]);

  if (!user) {
    return (
      <div className="text-center">
        <p className="text-slate-600">Sign in to manage products.</p>
        <Link href="/login" className="mt-4 inline-block text-primary-600 hover:underline">
          Sign in
        </Link>
      </div>
    );
  }

  if (user.role !== 'seller' && user.role !== 'admin') {
    return (
      <div className="text-center">
        <p className="text-slate-600">Seller access required.</p>
        <Link href="/profile" className="mt-4 inline-block text-primary-600 hover:underline">
          Back to profile
        </Link>
      </div>
    );
  }

  if (loading) {
    return <div className="animate-pulse rounded-xl bg-slate-100 p-12 text-center">Loading...</div>;
  }

  const myProducts = products.filter((p) => p.seller_id === user.id);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-900">My products</h1>
        <Link href="/seller/products/new" className="btn-primary">
          Add product
        </Link>
      </div>
      {myProducts.length === 0 ? (
        <div className="card p-12 text-center text-slate-600">
          No products yet. <Link href="/seller/products/new" className="text-primary-600 hover:underline">Add your first product</Link>.
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {myProducts.map((p) => (
            <div key={p.id} className="card overflow-hidden">
              <div className="aspect-square bg-slate-100">
                {p.images?.[0]?.url ? (
                  <img src={p.images[0].url} alt="" className="h-full w-full object-cover" />
                ) : (
                  <div className="flex h-full items-center justify-center text-slate-400">No image</div>
                )}
              </div>
              <div className="p-4">
                <h2 className="font-medium text-slate-900 line-clamp-2">{p.title}</h2>
                <p className="mt-1 text-primary-600">₹{Number(p.price).toLocaleString('en-IN')}</p>
                <div className="mt-2 flex gap-2">
                  <Link href={`/products/${p.id}`} className="btn-secondary text-sm">
                    View
                  </Link>
                  <Link href={`/seller/products/${p.id}/edit`} className="btn-secondary text-sm">
                    Edit
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
