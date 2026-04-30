import {
  ContentDetail,
  ContentProgress,
  ContentSummary,
  ContentType,
  Difficulty,
  LearningPath,
  ProgressListItem,
  ProgressUpsertPayload,
  ResourceKind,
  SearchResponse,
  Status,
  TokenResponse,
  User,
} from "./types";
import {
  getValidatorEntry,
  setValidatorEntry,
} from "./validatorCache";

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "/api/v1").replace(
  /\/$/,
  "",
);

let authToken: string | null = null;

export function setAuthToken(token: string | null): void {
  authToken = token;
}

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

interface ApiFilters {
  difficulty?: Difficulty;
  status?: Status;
  tags?: string[];
  content_type?: ContentType;
}

type FetchJsonInit = RequestInit & { useValidatorCache?: boolean };

async function fetchJson<T>(path: string, init?: FetchJsonInit): Promise<T> {
  const { useValidatorCache, ...requestInit } = init ?? {};
  const url = `${API_BASE_URL}${path}`;

  const headers = new Headers(requestInit.headers);
  if (authToken) {
    headers.set("Authorization", `Bearer ${authToken}`);
  }
  if (requestInit.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const cachedEntry = useValidatorCache ? getValidatorEntry(url) : undefined;
  if (cachedEntry) {
    headers.set("If-None-Match", cachedEntry.etag);
  }

  const response = await fetch(url, {
    ...requestInit,
    headers,
  });

  if (useValidatorCache && response.status === 304 && cachedEntry) {
    return cachedEntry.data as T;
  }

  if (!response.ok) {
    let detail = `Request failed with status ${response.status}`;
    try {
      const payload = await response.json();
      if (payload && typeof payload.detail === "string") {
        detail = payload.detail;
      }
    } catch {
      // ignore non-JSON error bodies
    }
    throw new ApiError(response.status, detail);
  }

  const parsed = (await response.json()) as T;

  if (useValidatorCache) {
    const etag = response.headers.get("etag");
    if (etag) {
      setValidatorEntry(url, etag, parsed);
    }
  }

  return parsed;
}

function buildQuery(filters?: ApiFilters): string {
  if (!filters) {
    return "";
  }

  const params = new URLSearchParams();

  if (filters.difficulty) {
    params.set("difficulty", filters.difficulty);
  }

  if (filters.status) {
    params.set("status", filters.status);
  }

  if (filters.content_type) {
    params.set("content_type", filters.content_type);
  }

  if (filters.tags && filters.tags.length > 0) {
    params.set("tags", filters.tags.join(","));
  }

  const query = params.toString();
  return query ? `?${query}` : "";
}

export function fetchCollection(
  resource: ResourceKind,
  filters?: ApiFilters,
): Promise<ContentSummary[]> {
  return fetchJson<ContentSummary[]>(`/${resource}${buildQuery(filters)}`);
}

export function fetchCatalog(filters?: ApiFilters): Promise<ContentSummary[]> {
  return fetchJson<ContentSummary[]>(`/catalog${buildQuery(filters)}`);
}

export function fetchContentDetail(
  resource: ResourceKind,
  slug: string,
): Promise<ContentDetail> {
  return fetchJson<ContentDetail>(`/${resource}/slug/${slug}`);
}

export function fetchLearningPaths(): Promise<LearningPath[]> {
  return fetchJson<LearningPath[]>("/learning-paths");
}

export function fetchLearningPathDetail(slug: string): Promise<LearningPath> {
  return fetchJson<LearningPath>(`/learning-paths/slug/${slug}`);
}

export function registerUser(
  email: string,
  password: string,
): Promise<TokenResponse> {
  return fetchJson<TokenResponse>("/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function loginUser(
  email: string,
  password: string,
): Promise<TokenResponse> {
  return fetchJson<TokenResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function fetchCurrentUser(): Promise<User> {
  return fetchJson<User>("/auth/me");
}

export function fetchMyProgress(
  contentType: ContentType,
  contentId: number,
): Promise<ContentProgress | null> {
  const params = new URLSearchParams({
    content_type: contentType,
    content_id: String(contentId),
  });
  return fetchJson<ContentProgress | null>(`/me/progress?${params.toString()}`);
}

export function updateMyProgress(
  payload: ProgressUpsertPayload,
): Promise<ContentProgress | null> {
  return fetchJson<ContentProgress | null>("/me/progress", {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function fetchMyProgressList(): Promise<ProgressListItem[]> {
  return fetchJson<ProgressListItem[]>("/me/progress/list");
}

export function fetchMyProgressIndex(): Promise<ContentProgress[]> {
  return fetchJson<ContentProgress[]>("/me/progress/index");
}

export function searchContent(
  query: string,
  contentType?: ContentType,
  limit?: number,
  offset?: number,
): Promise<SearchResponse> {
  const params = new URLSearchParams({ q: query });
  if (contentType) {
    params.set("content_type", contentType);
  }
  if (limit !== undefined) {
    params.set("limit", String(limit));
  }
  if (offset !== undefined && offset > 0) {
    params.set("offset", String(offset));
  }
  return fetchJson<SearchResponse>(`/search?${params.toString()}`, {
    useValidatorCache: true,
  });
}
