import { useEffect, useState } from "react";

import { fetchCollection } from "../lib/api";
import {
  ContentSummary,
  Difficulty,
  ResourceKind,
  Status,
} from "../lib/types";

interface CollectionFilters {
  difficulty?: Difficulty;
  status?: Status;
  tags?: string[];
}

interface CollectionState {
  data: ContentSummary[];
  loading: boolean;
  error: string | null;
}

export function useCollection(
  resource: ResourceKind,
  filters: CollectionFilters = {},
): CollectionState {
  const [state, setState] = useState<CollectionState>({
    data: [],
    loading: true,
    error: null,
  });

  useEffect(() => {
    let isActive = true;

    setState({ data: [], loading: true, error: null });

    fetchCollection(resource, filters)
      .then((data) => {
        if (isActive) {
          setState({ data, loading: false, error: null });
        }
      })
      .catch((error: Error) => {
        if (isActive) {
          setState({
            data: [],
            loading: false,
            error: error.message || "Unable to load this collection.",
          });
        }
      });

    return () => {
      isActive = false;
    };
  }, [filters.difficulty, filters.status, resource, filters.tags?.join(",")]);

  return state;
}
