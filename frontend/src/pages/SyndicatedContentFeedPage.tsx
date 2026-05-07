import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";

import { EmptyState } from "../components/EmptyState";
import { LoadingState } from "../components/LoadingState";
import { TagBadge } from "../components/TagBadge";
import { fetchSyndicatedContentFeed } from "../lib/api";
import { formatLabel } from "../lib/content";
import {
  ContentType,
  SyndicatedContentFeedResponse,
  SyndicatedContentSummary,
} from "../lib/types";

const VALID_CONTENT_TYPES: ContentType[] = ["course", "tutorial", "lab"];

function isContentType(value: string | null): value is ContentType {
  return value !== null && (VALID_CONTENT_TYPES as string[]).includes(value);
}

const SyndicatedContentCard = ({
  item,
}: {
  item: SyndicatedContentSummary;
}) => {
  return (
    <article className="path-card">
      <div className="path-card-header">
        <h3>{item.title}</h3>
        <span className="type-pill">{formatLabel(item.content_type)}</span>
      </div>
      <p className="path-summary">{item.description}</p>
      <div className="meta-row">
        <span>{formatLabel(item.difficulty)}</span>
        <span>{item.estimated_minutes} min</span>
        <span>{item.author}</span>
      </div>
      <div className="tag-row">
        {item.tags.map((tag) => (
          <TagBadge key={`${item.slug}-${tag}`} label={tag} />
        ))}
      </div>
      <Link
        className="inline-link"
        to={`/syndication/content/${item.content_type}/${item.slug}`}
      >
        Open syndicated content
      </Link>
    </article>
  );
};

export const SyndicatedContentFeedPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const urlOffset = Math.max(0, Number(searchParams.get("offset")) || 0);
  const rawContentType = searchParams.get("content_type");
  const validatedContentType: ContentType | undefined = isContentType(
    rawContentType,
  )
    ? rawContentType
    : undefined;

  const [response, setResponse] = useState<SyndicatedContentFeedResponse | null>(
    null,
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isActive = true;
    setLoading(true);
    setError(null);

    fetchSyndicatedContentFeed(validatedContentType, undefined, urlOffset)
      .then((data) => {
        if (isActive) {
          setResponse(data);
          setLoading(false);
        }
      })
      .catch((currentError: Error) => {
        if (isActive) {
          setError(
            currentError.message || "Unable to load syndicated content feed.",
          );
          setLoading(false);
        }
      });

    return () => {
      isActive = false;
    };
  }, [urlOffset, validatedContentType]);

  function goToOffset(nextOffset: number) {
    const next = new URLSearchParams(searchParams);
    if (nextOffset <= 0) {
      next.delete("offset");
    } else {
      next.set("offset", String(nextOffset));
    }
    setSearchParams(next);
  }

  return (
    <>
      <section className="surface page-header">
        <span className="eyebrow">Syndication</span>
        <h2>Public content feed.</h2>
        <p>
          Partner-facing read-only view of published courses, tutorials, and
          labs. Stable identifier is content_type + slug.
        </p>
      </section>

      <section className="surface page-section">
        <div className="section-heading">
          <h3>Syndicated Content Feed</h3>
          <span className="footer-note">
            Slim summaries by design &mdash; follow up on an item for the full
            markdown body.
          </span>
        </div>

        {error ? (
          <EmptyState title="Syndicated content unavailable" message={error} />
        ) : loading ? (
          <LoadingState
            title="Loading syndicated content"
            message="Fetching the public content feed."
          />
        ) : !response || response.items.length === 0 ? (
          <EmptyState
            title="No syndicated content yet"
            message="No published content is currently available on the public feed."
          />
        ) : (
          <>
            <div className="path-grid">
              {response.items.map((item) => (
                <SyndicatedContentCard
                  key={`${item.content_type}-${item.slug}`}
                  item={item}
                />
              ))}
            </div>

            <div className="pagination-controls">
              <button
                type="button"
                className="pagination-button"
                onClick={() =>
                  goToOffset(response.meta.offset - response.meta.limit)
                }
                disabled={response.meta.offset === 0 || loading}
              >
                Previous
              </button>
              <span className="pagination-status">
                Page{" "}
                {Math.floor(response.meta.offset / response.meta.limit) + 1} of{" "}
                {Math.max(
                  1,
                  Math.ceil(response.meta.total / response.meta.limit),
                )}
              </span>
              <button
                type="button"
                className="pagination-button"
                onClick={() =>
                  goToOffset(response.meta.offset + response.meta.limit)
                }
                disabled={!response.meta.has_more || loading}
              >
                Next
              </button>
            </div>
          </>
        )}
      </section>
    </>
  );
};
