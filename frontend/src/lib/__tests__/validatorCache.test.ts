import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { searchContent } from "../api";
import {
  clearValidatorCache,
  getValidatorEntry,
  setValidatorEntry,
} from "../validatorCache";

const SEARCH_URL = "/api/v1/search?q=python";

function jsonResponse(body: unknown, etag: string | null, status = 200): Response {
  const headers = new Headers({ "Content-Type": "application/json" });
  if (etag !== null) {
    headers.set("ETag", etag);
  }
  return new Response(JSON.stringify(body), { status, headers });
}

function emptyResponse(status: number): Response {
  return new Response(null, { status });
}

describe("validatorCache module", () => {
  beforeEach(() => {
    clearValidatorCache();
  });

  it("set / get / clear round-trips an entry by URL", () => {
    expect(getValidatorEntry("/x")).toBeUndefined();
    setValidatorEntry("/x", '"abc"', { hello: "world" });
    expect(getValidatorEntry("/x")).toEqual({ etag: '"abc"', data: { hello: "world" } });
    clearValidatorCache();
    expect(getValidatorEntry("/x")).toBeUndefined();
  });
});

describe("fetchJson with useValidatorCache", () => {
  beforeEach(() => {
    clearValidatorCache();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("first 200 stores the ETag and parsed body", async () => {
    const fetchMock = vi.fn().mockResolvedValueOnce(
      jsonResponse({ query: "python", total: 0, limit: 20, offset: 0, has_more: false, results: [] }, '"abc"'),
    );
    vi.stubGlobal("fetch", fetchMock);

    const result = await searchContent("python");

    expect(fetchMock).toHaveBeenCalledTimes(1);
    const sentHeaders = new Headers(fetchMock.mock.calls[0][1].headers);
    expect(sentHeaders.get("If-None-Match")).toBeNull();

    expect(result.query).toBe("python");
    const entry = getValidatorEntry(SEARCH_URL);
    expect(entry).toBeDefined();
    expect(entry?.etag).toBe('"abc"');
    expect(entry?.data).toEqual(result);
  });

  it("second same-URL request sends If-None-Match and reuses cached body on 304", async () => {
    const cachedBody = {
      query: "python",
      total: 0,
      limit: 20,
      offset: 0,
      has_more: false,
      results: [],
    };
    setValidatorEntry(SEARCH_URL, '"abc"', cachedBody);

    const fetchMock = vi.fn().mockResolvedValueOnce(emptyResponse(304));
    vi.stubGlobal("fetch", fetchMock);

    const result = await searchContent("python");

    expect(fetchMock).toHaveBeenCalledTimes(1);
    const sentHeaders = new Headers(fetchMock.mock.calls[0][1].headers);
    expect(sentHeaders.get("If-None-Match")).toBe('"abc"');

    expect(result).toBe(cachedBody);
  });

  it("later 200 with a different ETag replaces the cache entry", async () => {
    setValidatorEntry(SEARCH_URL, '"abc"', { stale: true });

    const freshBody = {
      query: "python",
      total: 1,
      limit: 20,
      offset: 0,
      has_more: false,
      results: [],
    };
    const fetchMock = vi.fn().mockResolvedValueOnce(jsonResponse(freshBody, '"def"'));
    vi.stubGlobal("fetch", fetchMock);

    const result = await searchContent("python");

    expect(result).toEqual(freshBody);
    const entry = getValidatorEntry(SEARCH_URL);
    expect(entry?.etag).toBe('"def"');
    expect(entry?.data).toEqual(freshBody);
  });

  it("a 500 response does not poison or overwrite an existing cache entry", async () => {
    const cachedBody = { query: "python", total: 0, limit: 20, offset: 0, has_more: false, results: [] };
    setValidatorEntry(SEARCH_URL, '"abc"', cachedBody);

    const fetchMock = vi.fn().mockResolvedValueOnce(
      new Response(JSON.stringify({ detail: "boom" }), {
        status: 500,
        headers: { "Content-Type": "application/json", ETag: '"different"' },
      }),
    );
    vi.stubGlobal("fetch", fetchMock);

    await expect(searchContent("python")).rejects.toMatchObject({ status: 500 });

    const entry = getValidatorEntry(SEARCH_URL);
    expect(entry?.etag).toBe('"abc"');
    expect(entry?.data).toBe(cachedBody);
  });
});
