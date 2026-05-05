import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { SyndicatedLearningPathDetailPage } from "../SyndicatedLearningPathDetailPage";
import { SyndicatedLearningPathDetail } from "../../lib/types";
import { clearValidatorCache } from "../../lib/validatorCache";

const DETAIL_BODY: SyndicatedLearningPathDetail = {
  slug: "python-fundamentals",
  title: "Python Fundamentals",
  description: "A guided introduction to Python.",
  step_count: 2,
  estimated_minutes_total: 60,
  created_at: "2026-05-01T00:00:00Z",
  updated_at: "2026-05-01T00:00:00Z",
  steps: [
    {
      position: 1,
      content_type: "course",
      slug: "intro-to-python",
      title: "Intro to Python",
    },
    {
      position: 2,
      content_type: "tutorial",
      slug: "first-script",
      title: "First Script",
    },
  ],
};

function jsonResponse(body: unknown, etag: string): Response {
  return new Response(JSON.stringify(body), {
    status: 200,
    headers: { "Content-Type": "application/json", ETag: etag },
  });
}

describe("SyndicatedLearningPathDetailPage step rows", () => {
  beforeEach(() => {
    clearValidatorCache();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("links each step title and slug to its public content detail page", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValueOnce(jsonResponse(DETAIL_BODY, '"detail-etag"')),
    );

    render(
      <MemoryRouter
        initialEntries={["/syndication/learning-paths/python-fundamentals"]}
      >
        <Routes>
          <Route
            path="/syndication/learning-paths/:slug"
            element={<SyndicatedLearningPathDetailPage />}
          />
        </Routes>
      </MemoryRouter>,
    );

    const introTitle = await screen.findByRole("link", {
      name: "Intro to Python",
    });
    expect(introTitle).toHaveAttribute(
      "href",
      "/syndication/content/course/intro-to-python",
    );

    const firstTitle = screen.getByRole("link", { name: "First Script" });
    expect(firstTitle).toHaveAttribute(
      "href",
      "/syndication/content/tutorial/first-script",
    );

    const introSlug = screen.getByRole("link", { name: "intro-to-python" });
    expect(introSlug).toHaveAttribute(
      "href",
      "/syndication/content/course/intro-to-python",
    );

    const firstSlug = screen.getByRole("link", { name: "first-script" });
    expect(firstSlug).toHaveAttribute(
      "href",
      "/syndication/content/tutorial/first-script",
    );
  });
});
