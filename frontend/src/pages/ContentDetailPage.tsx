import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { EmptyState } from "../components/EmptyState";
import { LoadingState } from "../components/LoadingState";
import { MarkdownContent } from "../components/MarkdownContent";
import { ProgressControl } from "../components/ProgressControl";
import { TagBadge } from "../components/TagBadge";
import { useContentProgress } from "../hooks/useContentProgress";
import { fetchContentDetail } from "../lib/api";
import { useAuth } from "../lib/auth";
import { formatLabel } from "../lib/content";
import { ContentDetail, ResourceKind } from "../lib/types";

interface ContentDetailPageProps {
  resource: ResourceKind;
}

const resourceLabels: Record<ResourceKind, string> = {
  courses: "Course",
  tutorials: "Tutorial",
  labs: "Lab",
};

export const ContentDetailPage = ({ resource }: ContentDetailPageProps) => {
  const { slug } = useParams();
  const { user } = useAuth();
  const [content, setContent] = useState<ContentDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const progress = useContentProgress(content?.content_type, content?.id);

  useEffect(() => {
    if (!slug) {
      return;
    }

    let isActive = true;
    setLoading(true);
    setError(null);

    fetchContentDetail(resource, slug)
      .then((data) => {
        if (isActive) {
          setContent(data);
          setLoading(false);
        }
      })
      .catch((currentError: Error) => {
        if (isActive) {
          setError(currentError.message || "Unable to load content.");
          setLoading(false);
        }
      });

    return () => {
      isActive = false;
    };
  }, [resource, slug]);

  if (error) {
    return (
      <section className="surface page-section">
        <EmptyState
          title={`${resourceLabels[resource]} unavailable`}
          message={error}
          actionLabel={`Back to ${resource}`}
          actionTo={`/${resource}`}
        />
      </section>
    );
  }

  if (loading || !content) {
    return (
      <section className="surface page-section">
        <LoadingState
          title="Loading lesson"
          message="Preparing the long-form content experience."
        />
      </section>
    );
  }

  return (
    <>
      <section className="surface detail-hero">
        <div>
          <span className="eyebrow">{resourceLabels[resource]}</span>
          <h2>{content.title}</h2>
          <p>{content.description}</p>
          <div className="meta-row">
            <span>{formatLabel(content.content_type)}</span>
            <span>{formatLabel(content.difficulty)}</span>
            <span>{content.estimated_minutes} min</span>
            <span>{content.author}</span>
          </div>
          <div className="tag-row">
            {content.tags.map((tag) => (
              <TagBadge key={`${content.slug}-${tag}`} label={tag} />
            ))}
          </div>
        </div>

        <aside className="detail-side-panel">
          <div className="detail-side-card">
            <span className={`status-pill ${content.status}`}>
              {formatLabel(content.status)}
            </span>
            {user ? (
              <ProgressControl
                status={progress.status}
                loading={progress.loading}
                updating={progress.updating}
                error={progress.error}
                onChange={(next) => {
                  void progress.setStatus(next);
                }}
              />
            ) : null}
            <p className="footer-note">
              This lesson is rendered from markdown content stored on the backend.
            </p>
            <Link className="primary-link-button" to={`/${resource}`}>
              Back to {resource}
            </Link>
            <Link className="secondary-link-button" to="/learning-paths">
              Browse learning paths
            </Link>
          </div>
        </aside>
      </section>

      <section className="surface detail-content-layout">
        <div className="detail-article">
          <MarkdownContent content={content.body_markdown} />
        </div>
      </section>
    </>
  );
};
