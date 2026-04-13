import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { ContentCard } from "../components/ContentCard";
import { EmptyState } from "../components/EmptyState";
import { FilterToolbar } from "../components/FilterToolbar";
import { LoadingState } from "../components/LoadingState";
import { defaultBrowseFilters, parseTagsParam, uniqueTags } from "../lib/content";
import { fetchCatalog } from "../lib/api";
import { BrowseFilters, ContentSummary, ContentType, Difficulty, Status } from "../lib/types";

export const ExplorePage = () => {
  const [items, setItems] = useState<ContentSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchParams, setSearchParams] = useSearchParams();

  const filters: BrowseFilters = {
    ...defaultBrowseFilters(),
    difficulty:
      (searchParams.get("difficulty") as Difficulty | "all") || "all",
    status: (searchParams.get("status") as Status | "all") || "all",
    content_type:
      (searchParams.get("content_type") as ContentType | "all") || "all",
    tags: parseTagsParam(searchParams.get("tags")),
  };

  useEffect(() => {
    let isActive = true;

    setLoading(true);
    setError(null);

    fetchCatalog({
      difficulty: filters.difficulty === "all" ? undefined : filters.difficulty,
      status: filters.status === "all" ? undefined : filters.status,
      content_type:
        filters.content_type === "all" ? undefined : filters.content_type,
      tags: filters.tags.length > 0 ? filters.tags : undefined,
    })
      .then((data) => {
        if (isActive) {
          setItems(data);
          setLoading(false);
        }
      })
      .catch((currentError: Error) => {
        if (isActive) {
          setError(currentError.message || "Unable to load the catalog.");
          setLoading(false);
        }
      });

    return () => {
      isActive = false;
    };
  }, [
    filters.content_type,
    filters.difficulty,
    filters.status,
    filters.tags.join(","),
  ]);

  const availableTags = uniqueTags(items, filters.tags);

  function updateParam(key: string, value: string) {
    const next = new URLSearchParams(searchParams);

    if (!value || value === "all") {
      next.delete(key);
    } else {
      next.set(key, value);
    }

    setSearchParams(next);
  }

  function updateTags(nextTags: string[]) {
    const next = new URLSearchParams(searchParams);

    if (nextTags.length === 0) {
      next.delete("tags");
    } else {
      next.set("tags", nextTags.join(","));
    }

    setSearchParams(next);
  }

  return (
    <>
      <section className="surface page-header">
        <span className="eyebrow">Explore</span>
        <h2>Browse the full developer learning catalog.</h2>
        <p>
          Move across courses, tutorials, and labs with lightweight filters that
          keep discovery fast and readable.
        </p>
      </section>

      <section className="surface page-section">
        <div className="section-heading">
          <h3>Refine the catalog</h3>
          <span className="footer-note">
            Use content type, difficulty, status, and tags to narrow the view.
          </span>
        </div>

        <FilterToolbar
          availableTags={availableTags}
          filters={filters}
          onClear={() => setSearchParams(new URLSearchParams())}
          onContentTypeChange={(value) => updateParam("content_type", value)}
          onDifficultyChange={(value) => updateParam("difficulty", value)}
          onStatusChange={(value) => updateParam("status", value)}
          onTagToggle={(tag) => {
            const nextTags = filters.tags.includes(tag)
              ? filters.tags.filter((currentTag) => currentTag !== tag)
              : [...filters.tags, tag];
            updateTags(nextTags);
          }}
          showContentType
          showStatus
        />

        {error ? (
          <EmptyState
            title="Catalog unavailable"
            message={error}
            actionLabel="Back to dashboard"
            actionTo="/"
          />
        ) : loading ? (
          <LoadingState
            title="Loading catalog"
            message="Gathering courses, tutorials, and labs."
          />
        ) : items.length === 0 ? (
          <EmptyState
            title="No catalog matches"
            message="Try clearing one or more filters to widen the catalog."
            actionLabel="Clear filters"
            actionTo="/explore"
          />
        ) : (
          <div className="content-grid">
            {items.map((item) => (
              <ContentCard item={item} key={`${item.content_type}-${item.id}`} />
            ))}
          </div>
        )}
      </section>
    </>
  );
};
