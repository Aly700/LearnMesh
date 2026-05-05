import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";

import { ContentSummary, LearningPath, ProgressListItem, User } from "../../lib/types";
import { renderWithProviders } from "../../test/render";

vi.mock("../../lib/api", () => ({
  fetchCatalog: vi.fn(),
  fetchLearningPaths: vi.fn(),
  fetchMyProgressList: vi.fn(),
}));

const mockUser = vi.hoisted(() => ({ value: null as User | null }));

vi.mock("../../lib/auth", () => ({
  useAuth: () => ({
    user: mockUser.value,
    token: null,
    loading: false,
    login: vi.fn(),
    register: vi.fn(),
    logout: vi.fn(),
  }),
}));

import { HomePage } from "../HomePage";
import {
  fetchCatalog,
  fetchLearningPaths,
  fetchMyProgressList,
} from "../../lib/api";

const sampleCatalog: ContentSummary[] = [
  {
    id: 1,
    slug: "intro-fastapi",
    title: "Intro to FastAPI",
    description: "Build typed Python APIs.",
    content_type: "course",
    difficulty: "beginner",
    estimated_minutes: 45,
    tags: ["python", "fastapi"],
    status: "published",
    author: "Ada Backend",
    created_at: "2026-04-01T00:00:00Z",
    updated_at: "2026-04-01T00:00:00Z",
  },
  {
    id: 2,
    slug: "k8s-tutorial",
    title: "Kubernetes Tutorial",
    description: "Cluster basics in 30 minutes.",
    content_type: "tutorial",
    difficulty: "intermediate",
    estimated_minutes: 30,
    tags: ["kubernetes"],
    status: "published",
    author: "Bob Devops",
    created_at: "2026-04-02T00:00:00Z",
    updated_at: "2026-04-02T00:00:00Z",
  },
  {
    id: 3,
    slug: "react-lab",
    title: "React Lab",
    description: "Hands-on React state.",
    content_type: "lab",
    difficulty: "beginner",
    estimated_minutes: 25,
    tags: ["react"],
    status: "published",
    author: "Cara Frontend",
    created_at: "2026-04-03T00:00:00Z",
    updated_at: "2026-04-03T00:00:00Z",
  },
];

const samplePath: LearningPath = {
  id: 11,
  slug: "fullstack-foundations",
  title: "Fullstack Foundations",
  description: "From API to UI.",
  step_count: 2,
  estimated_minutes_total: 75,
  ordered_content: [
    {
      id: 101,
      content_type: "course",
      content_id: 1,
      content_slug: "intro-fastapi",
      content_title: "Intro to FastAPI",
      position: 1,
      description: "Build typed Python APIs.",
      difficulty: "beginner",
      estimated_minutes: 45,
      tags: ["python"],
      status: "published",
      author: "Ada Backend",
    },
    {
      id: 102,
      content_type: "lab",
      content_id: 3,
      content_slug: "react-lab",
      content_title: "React Lab",
      position: 2,
      description: "Hands-on React state.",
      difficulty: "beginner",
      estimated_minutes: 25,
      tags: ["react"],
      status: "published",
      author: "Cara Frontend",
    },
  ],
  created_at: "2026-04-04T00:00:00Z",
  updated_at: "2026-04-04T00:00:00Z",
};

describe("HomePage Phase 5A", () => {
  beforeEach(() => {
    vi.mocked(fetchCatalog).mockResolvedValue(sampleCatalog);
    vi.mocked(fetchLearningPaths).mockResolvedValue([samplePath]);
    vi.mocked(fetchMyProgressList).mockResolvedValue([]);
    mockUser.value = null;
  });

  it("renders the showcase hero with the connection-not-memorization headline", async () => {
    renderWithProviders(<HomePage />);

    expect(screen.getByText(/Learn through/i)).toBeInTheDocument();
    expect(screen.getByText("connection")).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: /Explore the catalog/i }),
    ).toHaveAttribute("href", "/explore");
    expect(
      screen.getByRole("link", { name: /Browse learning paths/i }),
    ).toHaveAttribute("href", "/learning-paths");
  });

  it("renders all three feature cards", async () => {
    renderWithProviders(<HomePage />);

    expect(
      screen.getByRole("heading", { name: "Connected knowledge" }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: "Guided learning paths" }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: "Progress that follows you" }),
    ).toBeInTheDocument();
  });

  it("shows the recommended dashboard preview for anonymous visitors", async () => {
    renderWithProviders(<HomePage />);

    expect(
      await screen.findByText("What your dashboard looks like"),
    ).toBeInTheDocument();
    expect(screen.getAllByText("Recommended").length).toBeGreaterThan(0);
    expect(fetchMyProgressList).not.toHaveBeenCalled();
  });

  it("shows the in-progress dashboard preview for signed-in users", async () => {
    mockUser.value = {
      id: 99,
      email: "user@example.com",
      created_at: "2026-04-01T00:00:00Z",
    };
    const inProgressItem: ProgressListItem = {
      content_type: "course",
      content_id: 1,
      status: "in_progress",
      updated_at: "2026-05-01T00:00:00Z",
      content: sampleCatalog[0],
    };
    vi.mocked(fetchMyProgressList).mockResolvedValueOnce([inProgressItem]);

    renderWithProviders(<HomePage />);

    expect(
      await screen.findByText("Your dashboard"),
    ).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getAllByText("In progress").length).toBeGreaterThan(0);
    });
    expect(fetchMyProgressList).toHaveBeenCalled();
  });

  it("renders the path-progress strip when a learning path exists", async () => {
    renderWithProviders(<HomePage />);

    await waitFor(() => {
      expect(screen.getByText("Path progress")).toBeInTheDocument();
    });
    expect(
      screen.getAllByText("Fullstack Foundations").length,
    ).toBeGreaterThan(0);
  });
});
