'use client';

import { useEffect, useState, useRef } from 'react';
import Link from 'next/link';
import { api, type Conversation } from '@/lib/api';
import { useAuth } from '@/lib/auth';

const PRESENCE_INTERVAL_MS = 30_000;

export default function ChatInboxPage() {
  const { token, user } = useAuth();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const refreshRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (!token) {
      setLoading(false);
      return;
    }
    function load() {
      api
        .get<Conversation[]>('/api/chat/conversations', token)
        .then(setConversations)
        .catch(() => setConversations([]))
        .finally(() => setLoading(false));
    }
    load();
    refreshRef.current = setInterval(load, PRESENCE_INTERVAL_MS);
    return () => {
      if (refreshRef.current) clearInterval(refreshRef.current);
    };
  }, [token]);

  useEffect(() => {
    if (!token) return;
    function heartbeat() {
      api.put('/api/chat/presence', {}, token).catch(() => {});
    }
    heartbeat();
    const t = setInterval(heartbeat, PRESENCE_INTERVAL_MS);
    return () => clearInterval(t);
  }, [token]);

  if (!user) {
    return (
      <div className="text-center">
        <p className="text-slate-600">Sign in to view your chats.</p>
        <Link href="/login" className="mt-4 inline-block text-primary-600 hover:underline">
          Sign in
        </Link>
      </div>
    );
  }

  if (loading) {
    return <div className="animate-pulse rounded-xl bg-slate-100 p-12 text-center">Loading...</div>;
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-900">Chat</h1>
      <p className="text-slate-600">Enquire with sellers or reply to buyers.</p>
      {conversations.length === 0 ? (
        <div className="card p-12 text-center text-slate-600">
          No conversations yet. Open a product and use &quot;Contact seller&quot; to start a chat.
        </div>
      ) : (
        <ul className="divide-y divide-slate-200 rounded-xl border border-slate-200 bg-white">
          {conversations.map((c) => {
            const otherName = user.id === c.buyer_id ? c.seller_name : c.buyer_name;
            return (
              <li key={c.id}>
                <Link
                  href={`/chat/${c.id}`}
                  className="flex items-center justify-between gap-4 px-4 py-4 hover:bg-slate-50"
                >
                  <div className="flex min-w-0 flex-1 items-center gap-2">
                    <span
                      className="h-2.5 w-2.5 shrink-0 rounded-full"
                      title={c.other_party_online ? 'Online' : 'Offline'}
                      style={{
                        backgroundColor: c.other_party_online ? '#22c55e' : '#94a3b8',
                      }}
                    />
                    <div className="min-w-0 flex-1">
                      <p className="font-medium text-slate-900">{otherName ?? 'User'}</p>
                    {c.product_title && (
                      <p className="truncate text-sm text-slate-500">Re: {c.product_title}</p>
                    )}
                    {c.last_message && (
                      <p className="mt-1 truncate text-sm text-slate-600">{c.last_message}</p>
                    )}
                    </div>
                  </div>
                  <div className="shrink-0 text-right">
                    {c.last_message_at && (
                      <p className="text-xs text-slate-500">
                        {new Date(c.last_message_at).toLocaleDateString()}
                      </p>
                    )}
                    {c.unread_count > 0 && (
                      <span className="mt-1 inline-block rounded-full bg-primary-600 px-2 py-0.5 text-xs text-white">
                        {c.unread_count}
                      </span>
                    )}
                  </div>
                </Link>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
