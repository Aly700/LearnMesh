import { useSearchParams } from "react-router-dom";

import { ContentCard } from "../components/ContentCard";
import { EmptyState } from "../components/EmptyState";
import { FilterToolbar } from "../components/FilterToolbar";
import { LoadingState } from "../components/LoadingState";
import { useCollection } from "../hooks/useCollection";
import { defaultBrowseFilters, parseTagsParam, uniqueTags } from "../lib/content";
import { BrowseFilters, Difficulty, ResourceKind } from "../lib/types";

interface ContentCollectionPageProps {
  resource: ResourceKind;
  title: string;
  description: string;
}

export const ContentCollectionPage = ({
  resource,
  title,
  description,
}: ContentCollectionPageProps) => {
  const [searchParams, setSearchParams] = useSearchParams();
  const filters: BrowseFilters = {
    ...defaultBrowseFilters(),
    difficulty:
      (searchParams.get("difficulty") as Difficulty | "all") || "all",
    tags: parseTagsParam(searchParams.get("tags")),
  };
  const { data, loading, error } = useCollection(resource, {
    difficulty: filters.difficulty === "all" ? undefined : filters.difficulty,
    tags: filters.tags.length > 0 ? filters.tags : undefined,
  });
  const availableTags = uniqueTags(data, filters.tags);

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
        <span className="eyebrow">{title}</span>
        <h2>{title}</h2>
        <p>{description}</p>
      </section>

      <section className="surface page-section">
        <div className="section-heading">
          <h3>Catalog</h3>
          <span className="footer-note">Live data fetched from the FastAPI backend.</span>
        </div>

        <FilterToolbar
          availableTags={availableTags}
          filters={filters}
          onClear={() => setSearchParams(new URLSearchParams())}
          onContentTypeChange={() => undefined}
          onDifficultyChange={(value) => updateParam("difficulty", value)}
          onStatusChange={() => undefined}
          onTagToggle={(tag) => {
            const nextTags = filters.tags.includes(tag)
              ? filters.tags.filter((currentTag) => currentTag !== tag)
              : [...filters.tags, tag];
            updateTags(nextTags);
          }}
        />

        {error ? (
          <EmptyState title={`${title} unavailable`} message={error} actionLabel="Open explore" actionTo="/explore" />
        ) : loading ? (
          <LoadingState
            title={`Loading ${title.toLowerCase()}`}
            message="Preparing the catalog."
          />
        ) : data.length === 0 ? (
          <EmptyState
            title={`No ${title.toLowerCase()} yet`}
            message={`Seed or create ${title.toLowerCase()} to populate this view.`}
            actionLabel="Clear filters"
            actionTo={`/${resource}`}
          />
        ) : (
          <div className="content-grid">
            {data.map((item) => (
              <ContentCard key={item.id} item={item} />
            ))}
          </div>
        )}
      </section>
    </>
  );
};
