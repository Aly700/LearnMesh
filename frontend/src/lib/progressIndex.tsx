import {
  ReactNode,
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import { fetchMyProgressIndex } from "./api";
import { useAuth } from "./auth";
import { ContentType, ProgressStatus } from "./types";

type ProgressMap = Map<string, ProgressStatus>;

export interface ProgressIndexContextValue {
  statusFor: (
    contentType: ContentType | undefined,
    contentId: number | undefined,
  ) => ProgressStatus | undefined;
  refresh: () => Promise<void>;
  loading: boolean;
  error: string | null;
}

export const ProgressIndexContext = createContext<ProgressIndexContextValue | undefined>(
  undefined,
);

function keyFor(contentType: ContentType, contentId: number): string {
  return `${contentType}:${contentId}`;
}

interface ProgressIndexProviderProps {
  children: ReactNode;
}

export const ProgressIndexProvider = ({ children }: ProgressIndexProviderProps) => {
  const { user } = useAuth();
  const [map, setMap] = useState<ProgressMap>(() => new Map());
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const requestIdRef = useRef(0);

  const loadIndex = useCallback(async () => {
    const requestId = ++requestIdRef.current;
    setLoading(true);
    setError(null);
    try {
      const rows = await fetchMyProgressIndex();
      if (requestId !== requestIdRef.current) return;
      const next: ProgressMap = new Map();
      for (const row of rows) {
        next.set(keyFor(row.content_type, row.content_id), row.status);
      }
      setMap(next);
    } catch (err) {
      if (requestId !== requestIdRef.current) return;
      const message = err instanceof Error ? err.message : "Unable to load progress.";
      setError(message);
      setMap(new Map());
    } finally {
      if (requestId === requestIdRef.current) {
        setLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    if (!user) {
      requestIdRef.current++;
      setMap(new Map());
      setLoading(false);
      setError(null);
      return;
    }
    void loadIndex();
  }, [user, loadIndex]);

  const statusFor = useCallback(
    (contentType: ContentType | undefined, contentId: number | undefined) => {
      if (!contentType || !contentId) return undefined;
      return map.get(keyFor(contentType, contentId));
    },
    [map],
  );

  const value = useMemo<ProgressIndexContextValue>(
    () => ({ statusFor, refresh: loadIndex, loading, error }),
    [statusFor, loadIndex, loading, error],
  );

  return (
    <ProgressIndexContext.Provider value={value}>
      {children}
    </ProgressIndexContext.Provider>
  );
};

export function useProgressIndex(): ProgressIndexContextValue {
  const ctx = useContext(ProgressIndexContext);
  if (ctx === undefined) {
    throw new Error("useProgressIndex must be used within a ProgressIndexProvider");
  }
  return ctx;
}
