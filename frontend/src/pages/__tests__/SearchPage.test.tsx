import { describe, expect, it, vi } from "vitest";
import { screen, waitFor } from "@testing-library/react";

import { SearchPage } from "../SearchPage";
import { ContentSummary, SearchResponse } from "../../lib/types";
import { renderWithProviders } from "../../test/render";

vi.mock("../../lib/api", () => ({
  searchContent: vi.fn(),
}));

import { searchContent } from "../../lib/api";

const baseSummary: ContentSummary = {
  id: 7,
  slug: "kubernetes-intro",
  title: "Kubernetes Intro",
  description: "A short intro to orchestration using Kubernetes.",
  content_type: "tutorial",
  difficulty: "intermediate",
  estimated_minutes: 30,
  tags: ["kubernetes", "devops"],
  status: "published",
  author: "Bob Devops",
  created_at: "2026-04-01T00:00:00Z",
  updated_at: "2026-04-12T00:00:00Z",
};

describe("SearchPage", () => {
  it("shows the empty-query prompt when no q is in the URL", () => {
    renderWithProviders(<SearchPage />, { initialEntries: ["/search"] });
    expect(screen.getByText(/Start typing to search/i)).toBeInTheDocument();
    expect(searchContent).not.toHaveBeenCalled();
  });

  it("renders results from a populated q query", async () => {
    const response: SearchResponse = {
      query: "kubernetes",
      total: 1,
      limit: 20,
      offset: 0,
      has_more: false,
      results: [{ ...baseSummary, score: 12.5, matched_fields: ["title", "tags"] }],
    };
    vi.mocked(searchContent).mockResolvedValueOnce(response);

    renderWithProviders(<SearchPage />, {
      initialEntries: ["/search?q=kubernetes"],
    });

    await waitFor(() => {
      expect(searchContent).toHaveBeenCalledWith("kubernetes", undefined, undefined, 0);
    });
    expect(
      await screen.findByRole("heading", { name: /Showing 1 of 1 result for "kubernetes"/i }),
    ).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Kubernetes Intro" })).toBeInTheDocument();
    expect(screen.getByText(/score 12\.5/)).toBeInTheDocument();
  });

  it("paginates via the URL offset query param", async () => {
    const response: SearchResponse = {
      query: "kubernetes",
      total: 50,
      limit: 20,
      offset: 20,
      has_more: true,
      results: [
        { ...baseSummary, id: 1, score: 9.0, matched_fields: ["title"] },
        { ...baseSummary, id: 2, score: 8.5, matched_fields: ["tags"] },
        { ...baseSummary, id: 3, score: 8.0, matched_fields: ["description"] },
      ],
    };
    vi.mocked(searchContent).mockResolvedValueOnce(response);

    renderWithProviders(<SearchPage />, {
      initialEntries: ["/search?q=kubernetes&offset=20"],
    });

    await waitFor(() => {
      expect(searchContent).toHaveBeenCalledWith("kubernetes", undefined, undefined, 20);
    });
    expect(await screen.findByText(/Page 2 of 3/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Previous" })).toBeEnabled();
    expect(screen.getByRole("button", { name: "Next" })).toBeEnabled();
  });
});
