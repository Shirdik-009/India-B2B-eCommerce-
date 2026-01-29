'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { api, type Product } from '@/lib/api';
import { useAuth } from '@/lib/auth';

export default function ProductDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = Number(params.id);
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [quantity, setQuantity] = useState(1);
  const [adding, setAdding] = useState(false);
  const [contacting, setContacting] = useState(false);
  const { token, user } = useAuth();

  useEffect(() => {
    if (Number.isNaN(id)) {
      setLoading(false);
      return;
    }
    let cancelled = false;
    api
      .get<Product>(`/api/products/${id}`)
      .then((p) => {
        if (!cancelled) {
          setProduct(p);
          setQuantity(p.min_order_quantity);
        }
      })
      .catch(() => {
        if (!cancelled) setProduct(null);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, [id]);

  async function contactSeller() {
    if (!token || !user) {
      router.push('/login');
      return;
    }
    if (user.id === product!.seller_id) {
      router.push('/chat');
      return;
    }
    setContacting(true);
    try {
      const conv = await api.post<{ id: number }>(
        '/api/chat/conversations',
        { seller_id: product!.seller_id, product_id: product!.id },
        token
      );
      router.push(`/chat/${conv.id}`);
    } catch {
      setContacting(false);
    }
  }

  async function addToCart() {
    if (!token || !user) {
      router.push('/login');
      return;
    }
    setAdding(true);
    try {
      await api.post(`/api/cart`, { product_id: id, quantity }, token);
      router.push('/cart');
    } catch {
      setAdding(false);
    }
  }

  if (loading) {
    return (
      <div className="mx-auto max-w-4xl animate-pulse">
        <div className="grid gap-8 lg:grid-cols-2">
          <div className="aspect-square rounded-xl bg-slate-200" />
          <div className="h-64 rounded-xl bg-slate-100" />
        </div>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="text-center">
        <p className="text-slate-600">Product not found.</p>
        <Link href="/products" className="mt-4 inline-block text-primary-600 hover:underline">
          Back to products
        </Link>
      </div>
    );
  }

  const minQty = product.min_order_quantity;

  return (
    <div className="mx-auto max-w-4xl">
      <div className="grid gap-8 lg:grid-cols-2">
        <div className="aspect-square overflow-hidden rounded-xl bg-slate-100">
          {product.images?.[0]?.url ? (
            <img
              src={product.images[0].url}
              alt={product.images[0].alt || product.title}
              className="h-full w-full object-cover"
            />
          ) : (
            <div className="flex h-full items-center justify-center text-slate-400">No image</div>
          )}
        </div>
        <div>
          <h1 className="text-2xl font-bold text-slate-900">{product.title}</h1>
          <p className="mt-2 text-2xl font-semibold text-primary-600">
            ₹{Number(product.price).toLocaleString('en-IN')} / {product.unit}
          </p>
          <p className="mt-1 text-sm text-slate-500">
            Min order: {minQty} {product.unit}
            {product.seller_name && ` · Seller: ${product.seller_name}`}
          </p>
          {product.description && (
            <div className="mt-6 text-slate-700">
              <h2 className="font-medium text-slate-900">Description</h2>
              <p className="mt-2 whitespace-pre-wrap">{product.description}</p>
            </div>
          )}
          <div className="mt-8 flex flex-wrap items-center gap-4">
            {user?.id === product.seller_id ? (
              <>
                <p className="text-slate-600">This is your product. You cannot order your own listing.</p>
                <Link href="/chat" className="btn-secondary">
                  View your chats
                </Link>
              </>
            ) : (
              <>
                <label className="flex items-center gap-2">
                  <span className="text-sm font-medium text-slate-700">Quantity:</span>
                  <input
                    type="number"
                    min={minQty}
                    value={quantity}
                    onChange={(e) => setQuantity(Math.max(minQty, Number(e.target.value) || minQty))}
                    className="input w-24"
                  />
                </label>
                <button
                  type="button"
                  onClick={addToCart}
                  disabled={adding}
                  className="btn-primary"
                >
                  {adding ? 'Adding...' : 'Add to cart'}
                </button>
                <button
                  type="button"
                  onClick={contactSeller}
                  disabled={contacting}
                  className="btn-secondary"
                >
                  {contacting ? 'Opening...' : 'Contact seller'}
                </button>
                {!token && (
                  <Link href="/login" className="btn-secondary">
                    Sign in to add to cart
                  </Link>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
