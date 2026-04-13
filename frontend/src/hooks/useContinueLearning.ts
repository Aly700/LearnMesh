import { useEffect, useState } from "react";

import { fetchMyProgressList } from "../lib/api";
import { useAuth } from "../lib/auth";
import { ProgressListItem } from "../lib/types";

interface UseContinueLearningResult {
  items: ProgressListItem[];
  loading: boolean;
  error: string | null;
}

export function useContinueLearning(): UseContinueLearningResult {
  const { user } = useAuth();
  const [items, setItems] = useState<ProgressListItem[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user) {
      setItems([]);
      setLoading(false);
      setError(null);
      return;
    }

    let cancelled = false;
    setLoading(true);
    setError(null);

    fetchMyProgressList()
      .then((next) => {
        if (cancelled) return;
        setItems(next);
        setLoading(false);
      })
      .catch((err: Error) => {
        if (cancelled) return;
        setError(err.message || "Unable to load progress.");
        setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [user]);

  return { items, loading, error };
}
