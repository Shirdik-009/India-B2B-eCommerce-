'use client';

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { api, type ProductListResponse } from '@/lib/api';

export default function ProductsPage() {
  const searchParams = useSearchParams();
  const categoryId = searchParams.get('category_id');
  const [data, setData] = useState<ProductListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [q, setQ] = useState('');
  const [search, setSearch] = useState('');

  useEffect(() => {
    let cancelled = false;
    const params = new URLSearchParams();
    params.set('page', String(page));
    params.set('page_size', '12');
    if (search) params.set('q', search);
    if (categoryId) params.set('category_id', categoryId);
    async function fetchProducts() {
      try {
        const res = await api.get<ProductListResponse>(`/api/products?${params}`);
        if (!cancelled) setData(res);
      } catch {
        if (!cancelled) setData({ total: 0, page: 1, page_size: 12, items: [] });
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    setLoading(true);
    fetchProducts();
    return () => { cancelled = true; };
  }, [page, search, categoryId]);

  const totalPages = data ? Math.ceil(data.total / data.page_size) : 0;

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <h1 className="text-2xl font-bold text-slate-900">Products</h1>
        <form
          className="flex gap-2"
          onSubmit={(e) => {
            e.preventDefault();
            setSearch(q);
            setPage(1);
          }}
        >
          <input
            type="search"
            placeholder="Search products..."
            value={q}
            onChange={(e) => setQ(e.target.value)}
            className="input max-w-xs"
          />
          <button type="submit" className="btn-primary">
            Search
          </button>
        </form>
      </div>

      {loading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="card h-64 animate-pulse rounded-xl bg-slate-100" />
          ))}
        </div>
      ) : data && data.items.length > 0 ? (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {data.items.map((p) => (
              <Link key={p.id} href={`/products/${p.id}`} className="card block overflow-hidden transition-shadow hover:shadow-md">
                <div className="aspect-square bg-slate-100">
                  {p.images?.[0]?.url ? (
                    <img
                      src={p.images[0].url}
                      alt={p.images[0].alt || p.title}
                      className="h-full w-full object-cover"
                    />
                  ) : (
                    <div className="flex h-full items-center justify-center text-slate-400">No image</div>
                  )}
                </div>
                <div className="p-4">
                  <h2 className="font-medium text-slate-900 line-clamp-2">{p.title}</h2>
                  <p className="mt-1 text-lg font-semibold text-primary-600">
                    ₹{Number(p.price).toLocaleString('en-IN')}
                  </p>
                  <p className="text-xs text-slate-500">
                    Min order: {p.min_order_quantity} {p.unit}
                    {p.seller_name && ` · ${p.seller_name}`}
                  </p>
                </div>
              </Link>
            ))}
          </div>
          {totalPages > 1 && (
            <div className="flex justify-center gap-2">
              <button
                type="button"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1}
                className="btn-secondary"
              >
                Previous
              </button>
              <span className="flex items-center px-4 text-sm text-slate-600">
                Page {page} of {totalPages}
              </span>
              <button
                type="button"
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page >= totalPages}
                className="btn-secondary"
              >
                Next
              </button>
            </div>
          )}
        </>
      ) : (
        <div className="rounded-xl border border-slate-200 bg-slate-50 p-12 text-center text-slate-600">
          No products found. Try a different search or check back later.
        </div>
      )}
    </div>
  );
}
