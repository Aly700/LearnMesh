import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { EmptyState } from "../components/EmptyState";
import { LoadingState } from "../components/LoadingState";
import { MarkdownContent } from "../components/MarkdownContent";
import { TagBadge } from "../components/TagBadge";
import { fetchSyndicatedContentDetail } from "../lib/api";
import { formatLabel } from "../lib/content";
import { ContentType, SyndicatedContentDetail } from "../lib/types";

const VALID_CONTENT_TYPES: ContentType[] = ["course", "tutorial", "lab"];

const isContentType = (value: string | undefined): value is ContentType =>
  value !== undefined &&
  VALID_CONTENT_TYPES.includes(value as ContentType);

export const SyndicatedContentDetailPage = () => {
  const { contentType, slug } = useParams();
  const [item, setItem] = useState<SyndicatedContentDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const validContentType = useMemo(
    () => (isContentType(contentType) ? contentType : null),
    [contentType],
  );

  useEffect(() => {
    if (!validContentType || !slug) {
      setError("Invalid syndicated content URL.");
      setLoading(false);
      return;
    }

    let isActive = true;
    setLoading(true);
    setError(null);

    fetchSyndicatedContentDetail(validContentType, slug)
      .then((data) => {
        if (isActive) {
          setItem(data);
          setLoading(false);
        }
      })
      .catch((currentError: Error) => {
        if (isActive) {
          setError(
            currentError.message || "Unable to load syndicated content.",
          );
          setLoading(false);
        }
      });

    return () => {
      isActive = false;
    };
  }, [validContentType, slug]);

  if (error) {
    return (
      <section className="surface page-section">
        <EmptyState
          title="Syndicated content unavailable"
          message={error}
          actionLabel="Back to syndicated content"
          actionTo="/syndication/content"
        />
      </section>
    );
  }

  if (loading || !item) {
    return (
      <section className="surface page-section">
        <LoadingState
          title="Loading syndicated content"
          message="Fetching the public content detail payload."
        />
      </section>
    );
  }

  return (
    <>
      <section className="surface detail-hero">
        <div>
          <span className="eyebrow">Syndicated {formatLabel(item.content_type)}</span>
          <h2>{item.title}</h2>
          <p>{item.description}</p>
          <div className="meta-row">
            <span>{formatLabel(item.content_type)}</span>
            <span>{formatLabel(item.difficulty)}</span>
            <span>{item.estimated_minutes} min</span>
            <span>{item.author}</span>
          </div>
          <div className="tag-row">
            {item.tags.map((tag) => (
              <TagBadge key={`${item.slug}-${tag}`} label={tag} />
            ))}
          </div>
        </div>

        <aside className="detail-side-panel">
          <div className="detail-side-card">
            <span className="type-pill">{formatLabel(item.content_type)}</span>
            <p className="footer-note">
              Reference-only public view &mdash; no progress tracking or
              editing on this surface.
            </p>
            <p className="panel-subtitle">
              Slug: <code>{item.slug}</code>
            </p>
            <Link className="primary-link-button" to="/syndication/content">
              Back to syndicated content
            </Link>
            <Link
              className="secondary-link-button"
              to="/syndication/learning-paths"
            >
              Browse syndicated paths
            </Link>
          </div>
        </aside>
      </section>

      <section className="surface detail-content-layout">
        <div className="detail-article">
          <MarkdownContent content={item.body_markdown} />
        </div>
      </section>
    </>
  );
};
