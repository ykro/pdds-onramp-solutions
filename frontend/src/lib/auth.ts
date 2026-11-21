export interface AuthUser {
  id: string;
  email: string;
  name?: string;
}

interface AuthSession {
  token: string;
  user: AuthUser;
}

const STORAGE_KEY = 'tiendita_auth_session';

let memorySession: AuthSession | null = null;

function readStoredSession(): AuthSession | null {
  if (memorySession) {
    return memorySession;
  }
  if (typeof window === 'undefined' || !window.sessionStorage) {
    return null;
  }
  try {
    const raw = window.sessionStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return null;
    }
    const parsed = JSON.parse(raw) as AuthSession;
    if (parsed && typeof parsed.token === 'string' && parsed.user?.email) {
      memorySession = parsed;
      return memorySession;
    }
  } catch {
    return null;
  }
  return null;
}

function writeSession(session: AuthSession | null): void {
  memorySession = session;
  if (typeof window === 'undefined' || !window.sessionStorage) {
    return;
  }
  try {
    if (session) {
      window.sessionStorage.setItem(STORAGE_KEY, JSON.stringify(session));
    } else {
      window.sessionStorage.removeItem(STORAGE_KEY);
    }
  } catch {
    // Ignore storage quota or privacy-mode errors; memorySession holds state.
  }
}

function getNeonAuthUrl(): string {
  const configured = import.meta.env.VITE_NEON_AUTH_URL;
  return typeof configured === 'string' ? configured.trim().replace(/\/+$/, '') : '';
}

export function getToken(): string | null {
  return readStoredSession()?.token ?? null;
}

export function getCurrentUser(): AuthUser | null {
  return readStoredSession()?.user ?? null;
}

export async function signIn(email: string, password: string): Promise<AuthUser> {
  const cleanEmail = email.trim().toLowerCase();
  if (!cleanEmail || !cleanEmail.includes('@')) {
    throw new Error('Ingresa un correo válido.');
  }
  if (!password || password.trim().length === 0) {
    throw new Error('Ingresa una contraseña.');
  }

  const neonAuthUrl = getNeonAuthUrl();
  if (neonAuthUrl) {
    const response = await fetch(`${neonAuthUrl}/sign-in/email`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email: cleanEmail, password }),
    });

    if (!response.ok) {
      throw new Error('Credenciales inválidas.');
    }

    const data = (await response.json()) as {
      token?: string;
      access_token?: string;
      session?: { token?: string };
      user?: { id?: string; email?: string; name?: string };
    };

    const token = data.token ?? data.access_token ?? data.session?.token;
    if (!token) {
      throw new Error('Neon Auth no devolvió un token de sesión.');
    }

    const user: AuthUser = {
      id: data.user?.id ?? cleanEmail,
      email: data.user?.email ?? cleanEmail,
      name: data.user?.name,
    };

    writeSession({ token, user });
    return user;
  }

  const localUser: AuthUser = {
    id: `local-${cleanEmail}`,
    email: cleanEmail,
    name: cleanEmail.split('@')[0],
  };

  writeSession({
    token: `dev-token:${cleanEmail}`,
    user: localUser,
  });

  return localUser;
}

export async function signOut(): Promise<void> {
  const neonAuthUrl = getNeonAuthUrl();
  const currentToken = getToken();

  writeSession(null);

  if (neonAuthUrl && currentToken) {
    try {
      await fetch(`${neonAuthUrl}/sign-out`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${currentToken}`,
        },
      });
    } catch {
      // Local session is already cleared.
    }
  }
}
