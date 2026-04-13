export type ResourceKind = "courses" | "tutorials" | "labs";
export type ContentType = "course" | "tutorial" | "lab";
export type Difficulty = "beginner" | "intermediate" | "advanced";
export type Status = "draft" | "published" | "archived";

export interface ContentSummary {
  id: number;
  slug: string;
  title: string;
  description: string;
  content_type: ContentType;
  difficulty: Difficulty;
  estimated_minutes: number;
  tags: string[];
  status: Status;
  author: string;
  created_at: string;
  updated_at: string;
}

export interface ContentDetail extends ContentSummary {
  body_markdown: string;
}

export interface LearningPathStep {
  id: number;
  content_type: ContentType;
  content_id: number;
  content_slug: string;
  content_title: string;
  position: number;
  description: string;
  difficulty: Difficulty;
  estimated_minutes: number;
  tags: string[];
  status: Status;
  author: string;
}

export interface LearningPath {
  id: number;
  slug: string;
  title: string;
  description: string;
  step_count: number;
  estimated_minutes_total: number;
  ordered_content: LearningPathStep[];
  created_at: string;
  updated_at: string;
}

export interface BrowseFilters {
  difficulty: Difficulty | "all";
  status: Status | "all";
  content_type: ContentType | "all";
  tags: string[];
}

export interface User {
  id: number;
  email: string;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export type ProgressStatus = "not_started" | "in_progress" | "completed";

export interface ContentProgress {
  content_type: ContentType;
  content_id: number;
  status: ProgressStatus;
  updated_at: string;
}

export interface ProgressUpsertPayload {
  content_type: ContentType;
  content_id: number;
  status: ProgressStatus;
}

export interface ProgressListItem {
  content_type: ContentType;
  content_id: number;
  status: ProgressStatus;
  updated_at: string;
  content: ContentSummary;
}
