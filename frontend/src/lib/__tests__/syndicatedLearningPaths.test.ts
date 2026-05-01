import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  fetchSyndicatedLearningPathDetail,
  fetchSyndicatedLearningPaths,
} from "../api";
import {
  clearValidatorCache,
  getValidatorEntry,
  setValidatorEntry,
} from "../validatorCache";

const FEED_URL_NO_QS = "/api/v1/syndication/learning-paths";
const FEED_URL_PAGE_2 = "/api/v1/syndication/learning-paths?limit=50&offset=50";
const DETAIL_URL = "/api/v1/syndication/learning-paths/python-fundamentals";

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

const FEED_BODY = {
  meta: {
    total: 0,
    generated_at: "2026-05-01T00:00:00Z",
    limit: 50,
    offset: 0,
    has_more: false,
  },
  items: [],
};

const DETAIL_BODY = {
  slug: "python-fundamentals",
  title: "Python Fundamentals",
  description: "A guided path through Python basics.",
  step_count: 1,
  estimated_minutes_total: 30,
  created_at: "2026-05-01T00:00:00Z",
  updated_at: "2026-05-01T00:00:00Z",
  steps: [
    {
      position: 1,
      content_type: "course" as const,
      slug: "intro-to-python",
      title: "Intro to Python",
    },
  ],
};

describe("fetchSyndicatedLearningPaths URL composition", () => {
  beforeEach(() => {
    clearValidatorCache();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("omits the query string when no pagination args are passed", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(FEED_BODY, '"feed-etag"'));
    vi.stubGlobal("fetch", fetchMock);

    await fetchSyndicatedLearningPaths();

    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock.mock.calls[0][0]).toBe(FEED_URL_NO_QS);
  });

  it("emits limit and offset when both are passed and offset > 0", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(FEED_BODY, '"feed-etag"'));
    vi.stubGlobal("fetch", fetchMock);

    await fetchSyndicatedLearningPaths(50, 50);

    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock.mock.calls[0][0]).toBe(FEED_URL_PAGE_2);
  });

  it("omits offset when it is 0 so page-1 cache keys line up", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(FEED_BODY, '"feed-etag"'));
    vi.stubGlobal("fetch", fetchMock);

    await fetchSyndicatedLearningPaths(50, 0);

    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock.mock.calls[0][0]).toBe(
      "/api/v1/syndication/learning-paths?limit=50",
    );
  });
});

describe("fetchSyndicatedLearningPathDetail URL composition", () => {
  beforeEach(() => {
    clearValidatorCache();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("hits the slug-keyed detail URL", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(DETAIL_BODY, '"detail-etag"'));
    vi.stubGlobal("fetch", fetchMock);

    const result = await fetchSyndicatedLearningPathDetail(
      "python-fundamentals",
    );

    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock.mock.calls[0][0]).toBe(DETAIL_URL);
    expect(result.slug).toBe("python-fundamentals");
  });
});

describe("syndicated learning-path wrappers opt into the validator cache", () => {
  beforeEach(() => {
    clearValidatorCache();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("feed wrapper attaches If-None-Match and reuses cached body on 304", async () => {
    setValidatorEntry(FEED_URL_NO_QS, '"feed-etag"', FEED_BODY);

    const fetchMock = vi.fn().mockResolvedValueOnce(emptyResponse(304));
    vi.stubGlobal("fetch", fetchMock);

    const result = await fetchSyndicatedLearningPaths();

    expect(fetchMock).toHaveBeenCalledTimes(1);
    const sentHeaders = new Headers(fetchMock.mock.calls[0][1].headers);
    expect(sentHeaders.get("If-None-Match")).toBe('"feed-etag"');
    expect(result).toBe(FEED_BODY);
  });

  it("detail wrapper stores ETag from a fresh 200 against its slug-keyed URL", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(DETAIL_BODY, '"detail-etag"'));
    vi.stubGlobal("fetch", fetchMock);

    await fetchSyndicatedLearningPathDetail("python-fundamentals");

    const entry = getValidatorEntry(DETAIL_URL);
    expect(entry).toBeDefined();
    expect(entry?.etag).toBe('"detail-etag"');
    expect(entry?.data).toEqual(DETAIL_BODY);
  });
});
