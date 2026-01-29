import type { Metadata } from 'next';
import './globals.css';
import { Header } from '@/components/Header';
import { AuthProvider } from '@/lib/auth';

export const metadata: Metadata = {
  title: 'India B2B Marketplace | Wholesale & Suppliers',
  description: 'India\'s B2B marketplace - source products, connect with suppliers, grow your business.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen font-sans antialiased">
        <AuthProvider>
          <Header />
          <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
            {children}
          </main>
        </AuthProvider>
      </body>
    </html>
  );
}
