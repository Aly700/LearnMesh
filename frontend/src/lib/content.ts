import {
  BrowseFilters,
  ContentSummary,
  ContentType,
  LearningPathStep,
  ResourceKind,
} from "./types";

const resourceByType: Record<ContentType, ResourceKind> = {
  course: "courses",
  tutorial: "tutorials",
  lab: "labs",
};

export function formatLabel(value: string): string {
  return value
    .split(/[-_]/g)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export function getContentHref(
  item: Pick<ContentSummary, "content_type" | "slug">,
): string {
  return `/${resourceByType[item.content_type]}/${item.slug}`;
}

export function getLearningStepHref(step: LearningPathStep): string {
  return `/${resourceByType[step.content_type]}/${step.content_slug}`;
}

export function parseTagsParam(raw: string | null): string[] {
  if (!raw) {
    return [];
  }

  return raw
    .split(",")
    .map((tag) => tag.trim())
    .filter(Boolean);
}

export function uniqueTags(
  items: Array<{ tags: string[] }>,
  selectedTags: string[] = [],
): string[] {
  return Array.from(
    new Set([...selectedTags, ...items.flatMap((item) => item.tags)]),
  ).sort((left, right) => left.localeCompare(right));
}

export function defaultBrowseFilters(): BrowseFilters {
  return {
    difficulty: "all",
    status: "all",
    content_type: "all",
    tags: [],
  };
}
