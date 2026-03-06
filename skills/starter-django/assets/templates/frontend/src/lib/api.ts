/**
 * API client for communicating with the Django backend.
 *
 * During development, Vite's dev server proxies /api/* requests to Django,
 * so we don't need to specify the full backend URL.
 *
 * In production, nginx proxies /api/* to the Django service.
 *
 * For authenticated requests, use `authFetch` which automatically
 * attaches the Clerk Bearer token.
 */

export async function apiFetch<T = unknown>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const res = await fetch(endpoint, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }

  return res.json() as Promise<T>;
}

/**
 * Create an authenticated fetch using a Clerk token getter.
 *
 * Usage in a component:
 * ```
 * const { getToken } = useAuth();
 * const data = await authFetch(getToken, '/api/auth/me/');
 * ```
 */
export async function authFetch<T = unknown>(
  getToken: () => Promise<string | null>,
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = await getToken();

  return apiFetch<T>(endpoint, {
    ...options,
    headers: {
      ...options.headers,
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });
}
