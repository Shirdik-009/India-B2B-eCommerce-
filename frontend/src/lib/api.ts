const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export type ApiError = { detail: string | { msg: string; loc: string[] }[] };

async function request<T>(
  path: string,
  options: RequestInit & { token?: string } = {}
): Promise<T> {
  const { token, ...init } = options;
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(init.headers as Record<string, string>),
  };
  if (token) (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${API_URL}${path}`, { ...init, headers });
  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    const msg = Array.isArray(data.detail)
      ? data.detail.map((d: { msg: string }) => d.msg).join(', ')
      : typeof data.detail === 'string'
        ? data.detail
        : 'Request failed';
    throw new Error(msg);
  }
  return data as T;
}

export const api = {
  get: <T>(path: string, token?: string) =>
    request<T>(path, { method: 'GET', token }),
  post: <T>(path: string, body: unknown, token?: string) =>
    request<T>(path, { method: 'POST', body: JSON.stringify(body), token }),
  put: <T>(path: string, body: unknown = {}, token?: string) =>
    request<T>(path, { method: 'PUT', body: JSON.stringify(body), token }),
  patch: <T>(path: string, body: unknown, token?: string) =>
    request<T>(path, { method: 'PATCH', body: JSON.stringify(body), token }),
  delete: (path: string, token?: string) =>
    request(path, { method: 'DELETE', token }),
};

export type User = {
  id: number;
  email: string;
  full_name: string;
  phone: string | null;
  company_name: string | null;
  is_verified: boolean;
  role: string;
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
  user: User;
};

export type Product = {
  id: number;
  title: string;
  slug: string;
  description: string | null;
  price: string;
  min_order_quantity: number;
  unit: string;
  category_id: number | null;
  seller_id: number;
  is_active: boolean;
  created_at: string;
  images: { id: number; url: string; alt: string | null; sort_order: number }[];
  seller_name: string | null;
};

export type ProductListResponse = {
  total: number;
  page: number;
  page_size: number;
  items: Product[];
};

export type Category = {
  id: number;
  name: string;
  slug: string;
  description: string | null;
  parent_id: number | null;
  sort_order: number;
};

export type CartItem = {
  id: number;
  product_id: number;
  quantity: number;
  product_title: string | null;
  product_price: string | null;
  subtotal: string | null;
};

export type OrderItem = {
  id: number;
  product_id: number;
  product_title: string | null;
  quantity: number;
  unit_price: string;
  subtotal: string;
};

export type Order = {
  id: number;
  buyer_id: number;
  status: string;
  total_amount: string;
  shipping_address: string;
  notes: string | null;
  created_at: string;
  items: OrderItem[];
  display_number?: number;
};

export type OrderListResponse = {
  total: number;
  page: number;
  page_size: number;
  orders: Order[];
};

export type SellerOrderItem = {
  id: number;
  product_id: number;
  product_title: string | null;
  quantity: number;
  unit_price: string;
  subtotal: string;
};

export type SellerOrder = {
  id: number;
  buyer_id: number;
  buyer_name: string | null;
  status: string;
  created_at: string;
  shipping_address: string;
  items: SellerOrderItem[];
  seller_subtotal: string;
};

export type Message = {
  id: number;
  conversation_id: number;
  sender_id: number;
  sender_name: string | null;
  body: string;
  is_read: boolean;
  created_at: string;
};

export type Conversation = {
  id: number;
  buyer_id: number;
  seller_id: number;
  product_id: number | null;
  created_at: string;
  updated_at: string;
  buyer_name: string | null;
  seller_name: string | null;
  product_title: string | null;
  last_message: string | null;
  last_message_at: string | null;
  unread_count: number;
  other_party_online?: boolean;
};
