import { useCallback, useEffect, useState } from "react";

import { fetchMyProgress, updateMyProgress } from "../lib/api";
import { useAuth } from "../lib/auth";
import { useProgressIndex } from "../lib/progressIndex";
import { ContentType, ProgressStatus } from "../lib/types";

interface UseContentProgressResult {
  status: ProgressStatus;
  loading: boolean;
  updating: boolean;
  error: string | null;
  setStatus: (next: ProgressStatus) => Promise<void>;
}

export function useContentProgress(
  contentType: ContentType | undefined,
  contentId: number | undefined,
): UseContentProgressResult {
  const { user } = useAuth();
  const progressIndex = useProgressIndex();
  const [status, setStatusState] = useState<ProgressStatus>("not_started");
  const [loading, setLoading] = useState<boolean>(false);
  const [updating, setUpdating] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user || !contentType || !contentId) {
      setStatusState("not_started");
      setLoading(false);
      setError(null);
      return;
    }

    let cancelled = false;
    setLoading(true);
    setError(null);

    fetchMyProgress(contentType, contentId)
      .then((record) => {
        if (cancelled) return;
        setStatusState(record?.status ?? "not_started");
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
  }, [user, contentType, contentId]);

  const setStatus = useCallback(
    async (next: ProgressStatus) => {
      if (!user || !contentType || !contentId) {
        return;
      }
      setUpdating(true);
      setError(null);
      try {
        const record = await updateMyProgress({
          content_type: contentType,
          content_id: contentId,
          status: next,
        });
        setStatusState(record?.status ?? "not_started");
        void progressIndex.refresh();
      } catch (err) {
        const message = err instanceof Error ? err.message : "Unable to update progress.";
        setError(message);
      } finally {
        setUpdating(false);
      }
    },
    [user, contentType, contentId, progressIndex],
  );

  return { status, loading, updating, error, setStatus };
}
