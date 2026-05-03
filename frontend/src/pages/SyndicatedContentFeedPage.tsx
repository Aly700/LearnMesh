import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { EmptyState } from "../components/EmptyState";
import { LoadingState } from "../components/LoadingState";
import { TagBadge } from "../components/TagBadge";
import { fetchSyndicatedContentFeed } from "../lib/api";
import { formatLabel } from "../lib/content";
import { SyndicatedContentSummary } from "../lib/types";

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
  const [items, setItems] = useState<SyndicatedContentSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isActive = true;

    fetchSyndicatedContentFeed()
      .then((data) => {
        if (isActive) {
          setItems(data.items);
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
  }, []);

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
        ) : items.length === 0 ? (
          <EmptyState
            title="No syndicated content yet"
            message="No published content is currently available on the public feed."
          />
        ) : (
          <div className="path-grid">
            {items.map((item) => (
              <SyndicatedContentCard
                key={`${item.content_type}-${item.slug}`}
                item={item}
              />
            ))}
          </div>
        )}
      </section>
    </>
  );
};
