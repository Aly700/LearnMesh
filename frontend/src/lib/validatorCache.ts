interface CacheEntry {
  etag: string;
  data: unknown;
}

const cache = new Map<string, CacheEntry>();

export function getValidatorEntry(url: string): CacheEntry | undefined {
  return cache.get(url);
}

export function setValidatorEntry(url: string, etag: string, data: unknown): void {
  cache.set(url, { etag, data });
}

export function clearValidatorCache(): void {
  cache.clear();
}
