import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  fetchSyndicatedContentDetail,
  fetchSyndicatedContentFeed,
} from "../api";
import {
  clearValidatorCache,
  getValidatorEntry,
  setValidatorEntry,
} from "../validatorCache";

const FEED_URL_NO_QS = "/api/v1/syndication/feed";
const FEED_URL_FILTERED_PAGE_2 =
  "/api/v1/syndication/feed?content_type=course&limit=50&offset=50";
const FEED_URL_FILTERED_PAGE_1 =
  "/api/v1/syndication/feed?content_type=course&limit=50";
const DETAIL_URL = "/api/v1/syndication/content/course/intro-to-python";

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
  content_type: "course" as const,
  slug: "intro-to-python",
  title: "Intro to Python",
  description: "A guided introduction to Python.",
  difficulty: "beginner" as const,
  estimated_minutes: 30,
  tags: ["python"],
  author: "Jane Doe",
  created_at: "2026-05-01T00:00:00Z",
  updated_at: "2026-05-01T00:00:00Z",
  body_markdown: "# Intro\n\nHello world.",
};

describe("fetchSyndicatedContentFeed URL composition", () => {
  beforeEach(() => {
    clearValidatorCache();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("omits the query string when no args are passed", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(FEED_BODY, '"feed-etag"'));
    vi.stubGlobal("fetch", fetchMock);

    await fetchSyndicatedContentFeed();

    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock.mock.calls[0][0]).toBe(FEED_URL_NO_QS);
  });

  it("emits content_type, limit, and offset when offset > 0", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(FEED_BODY, '"feed-etag"'));
    vi.stubGlobal("fetch", fetchMock);

    await fetchSyndicatedContentFeed("course", 50, 50);

    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock.mock.calls[0][0]).toBe(FEED_URL_FILTERED_PAGE_2);
  });

  it("omits offset when it is 0 so page-1 cache keys line up", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(FEED_BODY, '"feed-etag"'));
    vi.stubGlobal("fetch", fetchMock);

    await fetchSyndicatedContentFeed("course", 50, 0);

    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock.mock.calls[0][0]).toBe(FEED_URL_FILTERED_PAGE_1);
  });
});

describe("fetchSyndicatedContentDetail URL composition", () => {
  beforeEach(() => {
    clearValidatorCache();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("hits the (content_type, slug)-keyed detail URL and returns body_markdown", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(DETAIL_BODY, '"detail-etag"'));
    vi.stubGlobal("fetch", fetchMock);

    const result = await fetchSyndicatedContentDetail(
      "course",
      "intro-to-python",
    );

    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock.mock.calls[0][0]).toBe(DETAIL_URL);
    expect(result.slug).toBe("intro-to-python");
    expect(result.body_markdown).toBe("# Intro\n\nHello world.");
  });
});

describe("syndicated content wrappers opt into the validator cache", () => {
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

    const result = await fetchSyndicatedContentFeed();

    expect(fetchMock).toHaveBeenCalledTimes(1);
    const sentHeaders = new Headers(fetchMock.mock.calls[0][1].headers);
    expect(sentHeaders.get("If-None-Match")).toBe('"feed-etag"');
    expect(result).toBe(FEED_BODY);
  });

  it("detail wrapper stores ETag from a fresh 200 against its (content_type, slug) URL", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(DETAIL_BODY, '"detail-etag"'));
    vi.stubGlobal("fetch", fetchMock);

    await fetchSyndicatedContentDetail("course", "intro-to-python");

    const entry = getValidatorEntry(DETAIL_URL);
    expect(entry).toBeDefined();
    expect(entry?.etag).toBe('"detail-etag"');
    expect(entry?.data).toEqual(DETAIL_BODY);
  });
});
