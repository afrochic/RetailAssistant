export const dynamic = 'force-dynamic';
// Explicit public allowlist: never serialize process.env or provider credentials.
export function GET() {
  const raw = process.env.API_BASE_URL || process.env.NEXT_PUBLIC_API_BASE_URL || '';
  try {
    const url = new URL(raw);
    const local = ['localhost', '127.0.0.1'].includes(url.hostname);
    if (url.username || url.password || (url.protocol !== 'https:' && !(local && url.protocol === 'http:'))) throw new Error('Invalid API origin');
    return Response.json({ apiBaseUrl: url.origin }, { headers: { 'Cache-Control': 'no-store' } });
  } catch {
    return Response.json({ apiBaseUrl: '', error: 'API_BASE_URL must be a public HTTPS API origin (HTTP localhost is allowed locally).' }, { status: 503, headers: { 'Cache-Control': 'no-store' } });
  }
}
