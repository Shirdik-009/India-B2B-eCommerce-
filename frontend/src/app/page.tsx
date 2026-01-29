'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useAuth } from '@/lib/auth';
import { api, type Category, type Product, type ProductListResponse } from '@/lib/api';

export default function HomePage() {
  const { user, loading: authLoading } = useAuth();
  const [categories, setCategories] = useState<Category[]>([]);
  const [productsByCategory, setProductsByCategory] = useState<Record<number, Product[]>>({});
  const [featuredProducts, setFeaturedProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get<Category[]>('/api/categories')
      .then((cats) => {
        setCategories(cats);
        return cats;
      })
      .catch(() => []);

    api
      .get<ProductListResponse>('/api/products?page_size=12')
      .then((res) => setFeaturedProducts(res.items || []))
      .catch(() => []);

    setLoading(false);
  }, []);

  useEffect(() => {
    if (categories.length === 0) return;
    const limit = 4;
    categories.slice(0, 6).forEach((cat) => {
      api
        .get<ProductListResponse>(`/api/products?category_id=${cat.id}&page_size=${limit}`)
        .then((res) => {
          setProductsByCategory((prev) => ({ ...prev, [cat.id]: res.items?.slice(0, limit) || [] }));
        })
        .catch(() => {});
    });
  }, [categories]);

  if (authLoading) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-primary-500 border-t-transparent" />
      </div>
    );
  }

  if (user) {
    return (
      <div className="space-y-10">
        <section className="rounded-2xl bg-gradient-to-br from-primary-500 to-primary-700 px-6 py-10 text-white sm:px-8">
          <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Welcome, {user.full_name}
          </h1>
          <p className="mt-2 max-w-xl text-primary-100">
            Browse products by category or discover featured listings.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link
              href="/products"
              className="rounded-lg bg-white px-5 py-2.5 text-sm font-medium text-primary-700 hover:bg-primary-50"
            >
              All products
            </Link>
            <Link
              href="/orders"
              className="rounded-lg border-2 border-white px-5 py-2.5 text-sm font-medium hover:bg-white/10"
            >
              My orders
            </Link>
            {(user.role === 'seller' || user.role === 'admin') && (
              <Link
                href="/seller/orders"
                className="rounded-lg border-2 border-white px-5 py-2.5 text-sm font-medium hover:bg-white/10"
              >
                Orders received
              </Link>
            )}
          </div>
        </section>

        {categories.length > 0 && (
          <section>
            <h2 className="text-xl font-semibold text-slate-900">Shop by category</h2>
            <div className="mt-4 flex flex-wrap gap-2">
              {categories.map((cat) => (
                <Link
                  key={cat.id}
                  href={`/products?category_id=${cat.id}`}
                  className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:border-primary-400 hover:bg-primary-50 hover:text-primary-700"
                >
                  {cat.name}
                </Link>
              ))}
            </div>
          </section>
        )}

        <section>
          <h2 className="text-xl font-semibold text-slate-900">Featured products</h2>
          {loading ? (
            <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="h-48 animate-pulse rounded-xl bg-slate-100" />
              ))}
            </div>
          ) : featuredProducts.length > 0 ? (
            <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {featuredProducts.slice(0, 8).map((p) => (
                <Link
                  key={p.id}
                  href={`/products/${p.id}`}
                  className="card block overflow-hidden transition-shadow hover:shadow-md"
                >
                  <div className="aspect-square bg-slate-100">
                    {p.images?.[0]?.url ? (
                      <img
                        src={p.images[0].url}
                        alt={p.images[0].alt || p.title}
                        className="h-full w-full object-cover"
                      />
                    ) : (
                      <div className="flex h-full items-center justify-center text-slate-400">
                        No image
                      </div>
                    )}
                  </div>
                  <div className="p-3">
                    <h3 className="line-clamp-2 text-sm font-medium text-slate-900">{p.title}</h3>
                    <p className="mt-1 font-semibold text-primary-600">
                      ₹{Number(p.price).toLocaleString('en-IN')}
                    </p>
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <p className="mt-4 text-slate-500">No products yet.</p>
          )}
          <Link
            href="/products"
            className="mt-4 inline-block text-sm font-medium text-primary-600 hover:text-primary-700"
          >
            View all products →
          </Link>
        </section>

        {categories.slice(0, 3).map(
          (cat) =>
            productsByCategory[cat.id]?.length > 0 && (
              <section key={cat.id}>
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-semibold text-slate-900">{cat.name}</h2>
                  <Link
                    href={`/products?category_id=${cat.id}`}
                    className="text-sm font-medium text-primary-600 hover:text-primary-700"
                  >
                    See all
                  </Link>
                </div>
                <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                  {productsByCategory[cat.id].map((p) => (
                    <Link
                      key={p.id}
                      href={`/products/${p.id}`}
                      className="card block overflow-hidden transition-shadow hover:shadow-md"
                    >
                      <div className="aspect-square bg-slate-100">
                        {p.images?.[0]?.url ? (
                          <img
                            src={p.images[0].url}
                            alt=""
                            className="h-full w-full object-cover"
                          />
                        ) : (
                          <div className="flex h-full items-center justify-center text-slate-400">
                            No image
                          </div>
                        )}
                      </div>
                      <div className="p-3">
                        <h3 className="line-clamp-2 text-sm font-medium text-slate-900">
                          {p.title}
                        </h3>
                        <p className="mt-1 font-semibold text-primary-600">
                          ₹{Number(p.price).toLocaleString('en-IN')}
                        </p>
                      </div>
                    </Link>
                  ))}
                </div>
              </section>
            )
        )}
      </div>
    );
  }

  return (
    <div className="space-y-16">
      <section className="rounded-2xl bg-gradient-to-br from-primary-500 to-primary-700 px-8 py-16 text-white">
        <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">
          India&apos;s B2B Marketplace
        </h1>
        <p className="mt-4 max-w-2xl text-lg text-primary-100">
          Source products from verified suppliers. Connect with manufacturers and wholesalers across
          India. Grow your business with trusted trade.
        </p>
        <div className="mt-8 flex gap-4">
          <Link
            href="/products"
            className="btn rounded-lg bg-white px-6 py-3 text-primary-700 hover:bg-primary-50"
          >
            Browse Products
          </Link>
          <Link
            href="/register"
            className="btn rounded-lg border-2 border-white px-6 py-3 hover:bg-white/10"
          >
            Register as Supplier
          </Link>
        </div>
      </section>

      <section>
        <h2 className="text-2xl font-semibold text-slate-900">Why India B2B?</h2>
        <div className="mt-6 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {[
            {
              title: 'Verified Suppliers',
              desc: 'Connect with verified manufacturers and wholesalers across India.',
            },
            {
              title: 'Bulk Pricing',
              desc: 'Competitive MOQ and wholesale prices for your business.',
            },
            {
              title: 'Secure Trade',
              desc: 'Safe transactions and dispute resolution support.',
            },
          ].map(({ title, desc }) => (
            <div key={title} className="card p-6">
              <h3 className="font-semibold text-slate-900">{title}</h3>
              <p className="mt-2 text-sm text-slate-600">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-2xl border border-slate-200 bg-slate-50 px-8 py-12">
        <h2 className="text-2xl font-semibold text-slate-900">Ready to start?</h2>
        <p className="mt-2 text-slate-600">
          Join thousands of buyers and suppliers already trading on India B2B.
        </p>
        <div className="mt-6 flex gap-4">
          <Link href="/register" className="btn-primary">
            Create free account
          </Link>
          <Link href="/login" className="btn-secondary">
            Sign in
          </Link>
        </div>
      </section>
    </div>
  );
}
