'use client';

import { useEffect, useState, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { api, type Message, type Conversation } from '@/lib/api';
import { useAuth } from '@/lib/auth';

export default function ChatThreadPage() {
  const params = useParams();
  const router = useRouter();
  const id = Number(params.id);
  const { token, user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [body, setBody] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!token || Number.isNaN(id)) {
      setLoading(false);
      return;
    }
    function loadConversation() {
      api
        .get<Conversation>(`/api/chat/conversations/${id}`, token)
        .then(setConversation)
        .catch(() => setConversation(null));
    }
    loadConversation();
    const t = setInterval(loadConversation, 30_000);
    return () => clearInterval(t);
  }, [token, id]);

  useEffect(() => {
    if (!token || Number.isNaN(id)) return;
    api
      .get<Message[]>(`/api/chat/conversations/${id}/messages`, token)
      .then(setMessages)
      .catch(() => setMessages([]))
      .finally(() => setLoading(false));
  }, [token, id]);

  useEffect(() => {
    if (!token) return;
    function heartbeat() {
      api.put('/api/chat/presence', {}, token).catch(() => {});
    }
    heartbeat();
    const t = setInterval(heartbeat, 30_000);
    return () => clearInterval(t);
  }, [token]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  async function sendMessage(e: React.FormEvent) {
    e.preventDefault();
    const text = body.trim();
    if (!text || sending || !token) return;
    setSending(true);
    try {
      const msg = await api.post<Message>(
        `/api/chat/conversations/${id}/messages`,
        { body: text },
        token
      );
      setMessages((prev) => [...prev, msg]);
      setBody('');
    } catch {
      // ignore
    } finally {
      setSending(false);
    }
  }

  if (!user) {
    router.push('/login');
    return null;
  }

  const otherName =
    conversation && (user.id === conversation.buyer_id ? conversation.seller_name : conversation.buyer_name);

  return (
    <div className="mx-auto flex max-w-2xl flex-col">
      <div className="border-b border-slate-200 bg-white px-4 py-3">
        <Link href="/chat" className="text-sm text-primary-600 hover:underline">
          ← Back to Chat
        </Link>
        <h1 className="mt-1 flex items-center gap-2 font-semibold text-slate-900">
          <span
            className="h-2.5 w-2.5 shrink-0 rounded-full"
            title={conversation?.other_party_online ? 'Online' : 'Offline'}
            style={{
              backgroundColor: conversation?.other_party_online ? '#22c55e' : '#94a3b8',
            }}
          />
          {otherName ?? 'Chat'}
          {conversation?.product_title && (
            <span className="ml-2 text-sm font-normal text-slate-500">
              Re: {conversation.product_title}
            </span>
          )}
        </h1>
      </div>

      <div className="flex flex-1 flex-col overflow-hidden bg-slate-50">
        {loading ? (
          <div className="flex flex-1 items-center justify-center p-8">Loading...</div>
        ) : (
          <div className="flex-1 space-y-3 overflow-y-auto p-4">
            {messages.map((m) => {
              const isMe = m.sender_id === user.id;
              return (
                <div
                  key={m.id}
                  className={`flex ${isMe ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] rounded-lg px-4 py-2 ${
                      isMe ? 'bg-primary-600 text-white' : 'bg-white text-slate-900 shadow'
                    }`}
                  >
                    {!isMe && (
                      <p className="text-xs font-medium text-slate-500">{m.sender_name}</p>
                    )}
                    <p className="whitespace-pre-wrap break-words">{m.body}</p>
                    <p className={`mt-1 text-xs ${isMe ? 'text-primary-100' : 'text-slate-400'}`}>
                      {new Date(m.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
              );
            })}
            <div ref={bottomRef} />
          </div>
        )}

        <form onSubmit={sendMessage} className="border-t border-slate-200 bg-white p-4">
          <div className="flex gap-2">
            <input
              type="text"
              value={body}
              onChange={(e) => setBody(e.target.value)}
              placeholder="Type a message..."
              className="input flex-1"
              maxLength={5000}
            />
            <button type="submit" disabled={sending || !body.trim()} className="btn-primary">
              {sending ? 'Sending...' : 'Send'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
