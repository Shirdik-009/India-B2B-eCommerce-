'use client';

import React, { createContext, useCallback, useContext, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { api, type User, type TokenResponse } from './api';

const TOKEN_KEY = 'marketplace_token';
const USER_KEY = 'marketplace_user';

type AuthState = {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: {
    email: string;
    password: string;
    full_name: string;
    phone?: string;
    company_name?: string;
    role?: string;
  }) => Promise<void>;
  logout: () => void;
  setUser: (u: User | null) => void;
};

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUserState] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const t = typeof window !== 'undefined' ? localStorage.getItem(TOKEN_KEY) : null;
    const u = typeof window !== 'undefined' ? localStorage.getItem(USER_KEY) : null;
    if (t && u) {
      setToken(t);
      try {
        setUserState(JSON.parse(u));
      } catch {
        setToken(null);
        localStorage.removeItem(USER_KEY);
        localStorage.removeItem(TOKEN_KEY);
      }
    }
    setLoading(false);
  }, []);

  const setUser = useCallback((u: User | null) => {
    setUserState(u);
    if (typeof window !== 'undefined') {
      if (u) localStorage.setItem(USER_KEY, JSON.stringify(u));
      else localStorage.removeItem(USER_KEY);
    }
  }, []);

  const login = useCallback(
    async (email: string, password: string) => {
      const data = await api.post<TokenResponse>('/api/auth/login', { email, password });
      setToken(data.access_token);
      setUser(data.user);
      if (typeof window !== 'undefined') localStorage.setItem(TOKEN_KEY, data.access_token);
      router.push('/');
    },
    [router, setUser]
  );

  const register = useCallback(
    async (data: {
      email: string;
      password: string;
      full_name: string;
      phone?: string;
      company_name?: string;
      role?: string;
    }) => {
      const res = await api.post<TokenResponse>('/api/auth/register', {
        ...data,
        role: data.role || 'buyer',
      });
      setToken(res.access_token);
      setUser(res.user);
      if (typeof window !== 'undefined') localStorage.setItem(TOKEN_KEY, res.access_token);
      router.push('/');
    },
    [router, setUser]
  );

  const logout = useCallback(() => {
    setToken(null);
    setUserState(null);
    if (typeof window !== 'undefined') {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
    }
    router.push('/');
  }, [router]);

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        login,
        register,
        logout,
        setUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
