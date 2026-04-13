import {
  ReactNode,
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  ApiError,
  fetchCurrentUser,
  loginUser,
  registerUser,
  setAuthToken,
} from "./api";
import { User } from "./types";

const TOKEN_STORAGE_KEY = "learnmesh.auth.token";

interface AuthContextValue {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

function readStoredToken(): string | null {
  try {
    return window.localStorage.getItem(TOKEN_STORAGE_KEY);
  } catch {
    return null;
  }
}

function writeStoredToken(token: string | null): void {
  try {
    if (token) {
      window.localStorage.setItem(TOKEN_STORAGE_KEY, token);
    } else {
      window.localStorage.removeItem(TOKEN_STORAGE_KEY);
    }
  } catch {
    // ignore storage failures
  }
}

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const [token, setTokenState] = useState<string | null>(() => {
    const stored = readStoredToken();
    setAuthToken(stored);
    return stored;
  });
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(() => Boolean(readStoredToken()));

  useEffect(() => {
    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }

    let cancelled = false;
    setLoading(true);

    fetchCurrentUser()
      .then((nextUser) => {
        if (cancelled) return;
        setUser(nextUser);
        setLoading(false);
      })
      .catch((err) => {
        if (cancelled) return;
        if (err instanceof ApiError && err.status === 401) {
          writeStoredToken(null);
          setAuthToken(null);
          setTokenState(null);
          setUser(null);
        }
        setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [token]);

  const applySession = useCallback((nextToken: string, nextUser: User) => {
    writeStoredToken(nextToken);
    setAuthToken(nextToken);
    setTokenState(nextToken);
    setUser(nextUser);
    setLoading(false);
  }, []);

  const login = useCallback(
    async (email: string, password: string) => {
      const result = await loginUser(email, password);
      applySession(result.access_token, result.user);
    },
    [applySession],
  );

  const register = useCallback(
    async (email: string, password: string) => {
      const result = await registerUser(email, password);
      applySession(result.access_token, result.user);
    },
    [applySession],
  );

  const logout = useCallback(() => {
    writeStoredToken(null);
    setAuthToken(null);
    setTokenState(null);
    setUser(null);
    setLoading(false);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({ user, token, loading, login, register, logout }),
    [user, token, loading, login, register, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (ctx === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return ctx;
}
