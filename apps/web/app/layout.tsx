import type { Metadata } from 'next';
import './globals.css';
export const metadata: Metadata = {
  title: 'RetailAssist — A little clarity for your everyday',
  description: 'Anonymous, catalogue-grounded Client X product discovery. An independent student project, not medical advice.',
  robots: { index: false, follow: false },
};
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
