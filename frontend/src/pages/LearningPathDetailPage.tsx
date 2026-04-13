import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { EmptyState } from "../components/EmptyState";
import { LoadingState } from "../components/LoadingState";
import { ProgressBadge } from "../components/ProgressBadge";
import { StepProgressControl } from "../components/StepProgressControl";
import { TagBadge } from "../components/TagBadge";
import { usePathProgress } from "../hooks/usePathProgress";
import { fetchLearningPathDetail } from "../lib/api";
import { useAuth } from "../lib/auth";
import { formatLabel, getLearningStepHref } from "../lib/content";
import { useProgressIndex } from "../lib/progressIndex";
import { LearningPath } from "../lib/types";

export const LearningPathDetailPage = () => {
  const { slug } = useParams();
  const [path, setPath] = useState<LearningPath | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!slug) {
      return;
    }

    let isActive = true;
    setLoading(true);
    setError(null);

    fetchLearningPathDetail(slug)
      .then((data) => {
        if (isActive) {
          setPath(data);
          setLoading(false);
        }
      })
      .catch((currentError: Error) => {
        if (isActive) {
          setError(currentError.message || "Unable to load learning path.");
          setLoading(false);
        }
      });

    return () => {
      isActive = false;
    };
  }, [slug]);

  if (error) {
    return (
      <section className="surface page-section">
        <EmptyState
          title="Learning path unavailable"
          message={error}
          actionLabel="Back to learning paths"
          actionTo="/learning-paths"
        />
      </section>
    );
  }

  const { user } = useAuth();
  const { completed, total } = usePathProgress(path?.ordered_content ?? []);
  const { statusFor } = useProgressIndex();

  if (loading || !path) {
    return (
      <section className="surface page-section">
        <LoadingState
          title="Loading learning path"
          message="Building the step-by-step path view."
        />
      </section>
    );
  }

  return (
    <>
      <section className="surface detail-hero">
        <div>
          <span className="eyebrow">Learning Path</span>
          <h2>{path.title}</h2>
          <p>{path.description}</p>
          <div className="meta-row">
            <span>{path.step_count} steps</span>
            <span>{path.estimated_minutes_total} min</span>
            {user && completed > 0 ? (
              <span>{completed} of {total} steps completed</span>
            ) : null}
          </div>
        </div>

        <aside className="detail-side-panel">
          <div className="detail-side-card">
            <strong>Quick navigation</strong>
            <ul className="quick-nav-list">
              {path.ordered_content.map((item) => (
                <li key={item.id}>
                  <a href={`#step-${item.position}`}>
                    Step {item.position}: {item.content_title}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </aside>
      </section>

      <section className="surface page-section">
        <div className="section-heading">
          <h3>Path Timeline</h3>
          <span className="footer-note">
            Follow the sequence or jump directly into any lesson.
          </span>
        </div>

        <div className="timeline-list">
          {path.ordered_content.map((item) => (
            <article
              className="timeline-step"
              id={`step-${item.position}`}
              key={item.id}
            >
              <div className="timeline-marker">0{item.position}</div>
              <div className="timeline-body">
                <div className="card-kicker-row">
                  <span className="type-pill">{formatLabel(item.content_type)}</span>
                  <span className={`status-pill ${item.status}`}>
                    {formatLabel(item.status)}
                  </span>
                  {(() => {
                    const stepStatus = statusFor(item.content_type, item.content_id);
                    return stepStatus ? <ProgressBadge status={stepStatus} /> : null;
                  })()}
                </div>
                <h3>{item.content_title}</h3>
                <p className="panel-subtitle">{item.description}</p>
                <div className="meta-row">
                  <span>{formatLabel(item.difficulty)}</span>
                  <span>{item.estimated_minutes} min</span>
                  <span>{item.author}</span>
                </div>
                <div className="tag-row">
                  {item.tags.map((tag) => (
                    <TagBadge key={`${item.id}-${tag}`} label={tag} />
                  ))}
                </div>
                <Link className="inline-link" to={getLearningStepHref(item)}>
                  Open lesson
                </Link>
                {user ? (
                  <StepProgressControl
                    contentType={item.content_type}
                    contentId={item.content_id}
                  />
                ) : null}
              </div>
            </article>
          ))}
        </div>
      </section>
    </>
  );
};
