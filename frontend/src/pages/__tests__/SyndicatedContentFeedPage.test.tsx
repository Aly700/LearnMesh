import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import {
  SyndicatedContentFeedResponse,
  SyndicatedContentSummary,
} from "../../lib/types";
import { renderWithProviders } from "../../test/render";

vi.mock("../../lib/api", () => ({
  fetchSyndicatedContentFeed: vi.fn(),
}));

import { SyndicatedContentFeedPage } from "../SyndicatedContentFeedPage";
import { fetchSyndicatedContentFeed } from "../../lib/api";

const baseItem: SyndicatedContentSummary = {
  content_type: "course",
  slug: "intro-to-python",
  title: "Intro to Python",
  description: "A guided introduction to Python.",
  difficulty: "beginner",
  estimated_minutes: 30,
  tags: ["python"],
  author: "Jane Doe",
  created_at: "2026-05-01T00:00:00Z",
  updated_at: "2026-05-01T00:00:00Z",
};

function makeResponse(
  meta: Partial<SyndicatedContentFeedResponse["meta"]> = {},
  items: SyndicatedContentSummary[] = [baseItem],
): SyndicatedContentFeedResponse {
  return {
    meta: {
      total: 3,
      generated_at: "2026-05-01T00:00:00Z",
      limit: 20,
      offset: 0,
      has_more: false,
      ...meta,
    },
    items,
  };
}

describe("SyndicatedContentFeedPage pagination", () => {
  beforeEach(() => {
    vi.mocked(fetchSyndicatedContentFeed).mockReset();
  });

  it("fetches page 1 with no URL params and disables Prev", async () => {
    vi.mocked(fetchSyndicatedContentFeed).mockResolvedValueOnce(makeResponse());

    renderWithProviders(<SyndicatedContentFeedPage />, {
      initialEntries: ["/syndication/content"],
    });

    await waitFor(() => {
      expect(fetchSyndicatedContentFeed).toHaveBeenCalledWith(
        undefined,
        undefined,
        0,
      );
    });

    expect(await screen.findByText(/Page 1 of 1/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Previous" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Next" })).toBeDisabled();
  });

  it("paginates via the URL offset query param", async () => {
    vi.mocked(fetchSyndicatedContentFeed).mockResolvedValueOnce(
      makeResponse({ total: 50, limit: 20, offset: 20, has_more: true }),
    );

    renderWithProviders(<SyndicatedContentFeedPage />, {
      initialEntries: ["/syndication/content?offset=20"],
    });

    await waitFor(() => {
      expect(fetchSyndicatedContentFeed).toHaveBeenCalledWith(
        undefined,
        undefined,
        20,
      );
    });
    expect(await screen.findByText(/Page 2 of 3/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Previous" })).toBeEnabled();
    expect(screen.getByRole("button", { name: "Next" })).toBeEnabled();
  });

  it("preserves content_type filter from URL", async () => {
    vi.mocked(fetchSyndicatedContentFeed).mockResolvedValueOnce(makeResponse());

    renderWithProviders(<SyndicatedContentFeedPage />, {
      initialEntries: ["/syndication/content?content_type=course"],
    });

    await waitFor(() => {
      expect(fetchSyndicatedContentFeed).toHaveBeenCalledWith(
        "course",
        undefined,
        0,
      );
    });
  });

  it("ignores invalid content_type in URL and falls back to undefined", async () => {
    vi.mocked(fetchSyndicatedContentFeed).mockResolvedValueOnce(makeResponse());

    renderWithProviders(<SyndicatedContentFeedPage />, {
      initialEntries: ["/syndication/content?content_type=garbage"],
    });

    await waitFor(() => {
      expect(fetchSyndicatedContentFeed).toHaveBeenCalledWith(
        undefined,
        undefined,
        0,
      );
    });
  });

  it("clicking Next increments offset and re-fetches", async () => {
    vi.mocked(fetchSyndicatedContentFeed)
      .mockResolvedValueOnce(
        makeResponse({ total: 50, limit: 20, offset: 0, has_more: true }),
      )
      .mockResolvedValueOnce(
        makeResponse({ total: 50, limit: 20, offset: 20, has_more: true }),
      );

    const user = userEvent.setup();
    renderWithProviders(<SyndicatedContentFeedPage />, {
      initialEntries: ["/syndication/content"],
    });

    await screen.findByText(/Page 1 of 3/);

    await user.click(screen.getByRole("button", { name: "Next" }));

    await waitFor(() => {
      expect(fetchSyndicatedContentFeed).toHaveBeenLastCalledWith(
        undefined,
        undefined,
        20,
      );
    });
    expect(await screen.findByText(/Page 2 of 3/)).toBeInTheDocument();
  });

  it("clicking Prev at page 2 returns to page 1 and removes offset from the URL", async () => {
    vi.mocked(fetchSyndicatedContentFeed)
      .mockResolvedValueOnce(
        makeResponse({ total: 50, limit: 20, offset: 20, has_more: true }),
      )
      .mockResolvedValueOnce(
        makeResponse({ total: 50, limit: 20, offset: 0, has_more: true }),
      );

    const user = userEvent.setup();
    renderWithProviders(<SyndicatedContentFeedPage />, {
      initialEntries: ["/syndication/content?offset=20"],
    });

    await screen.findByText(/Page 2 of 3/);

    await user.click(screen.getByRole("button", { name: "Previous" }));

    await waitFor(() => {
      expect(fetchSyndicatedContentFeed).toHaveBeenLastCalledWith(
        undefined,
        undefined,
        0,
      );
    });
    expect(await screen.findByText(/Page 1 of 3/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Previous" })).toBeDisabled();
  });
});
