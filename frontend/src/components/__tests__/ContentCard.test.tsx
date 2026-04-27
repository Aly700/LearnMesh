import { describe, expect, it } from "vitest";
import { screen } from "@testing-library/react";

import { ContentCard } from "../ContentCard";
import { ContentSummary } from "../../lib/types";
import {
  emptyProgressIndex,
  progressIndexFromMap,
  renderWithProviders,
} from "../../test/render";

const sampleItem: ContentSummary = {
  id: 42,
  slug: "docker-fundamentals",
  title: "Docker Fundamentals",
  description: "Learn containerization basics with Docker and Compose.",
  content_type: "course",
  difficulty: "beginner",
  estimated_minutes: 60,
  tags: ["docker", "containers"],
  status: "published",
  author: "Alice Example",
  created_at: "2026-04-01T00:00:00Z",
  updated_at: "2026-04-12T00:00:00Z",
};

describe("ContentCard", () => {
  it("renders title, meta, and tags", () => {
    renderWithProviders(<ContentCard item={sampleItem} />, {
      progressIndex: emptyProgressIndex,
    });

    expect(screen.getByRole("heading", { name: "Docker Fundamentals" })).toBeInTheDocument();
    expect(screen.getByText("Alice Example")).toBeInTheDocument();
    expect(screen.getByText("60 min")).toBeInTheDocument();
    expect(screen.getByText("Docker")).toBeInTheDocument();
    // No progress entry → no progress badge
    expect(screen.queryByText("In progress")).not.toBeInTheDocument();
    expect(screen.queryByText("Completed")).not.toBeInTheDocument();
  });

  it("renders the progress badge when the index returns a status", () => {
    renderWithProviders(<ContentCard item={sampleItem} />, {
      progressIndex: progressIndexFromMap({ "course:42": "in_progress" }),
    });

    expect(screen.getByText("In progress")).toBeInTheDocument();
  });
});
