import { Link } from "react-router-dom";

import { formatLabel, getContentHref } from "../lib/content";
import { useProgressIndex } from "../lib/progressIndex";
import { ContentSummary } from "../lib/types";
import { ProgressBadge } from "./ProgressBadge";
import { TagBadge } from "./TagBadge";

interface ContentCardProps {
  item: ContentSummary;
}

export const ContentCard = ({ item }: ContentCardProps) => {
  const { statusFor } = useProgressIndex();
  const progressStatus = statusFor(item.content_type, item.id);

  return (
    <article className="content-card">
      <span className="content-card-accent" aria-hidden="true" />
      <div className="card-kicker-row">
        <span className="type-pill">{formatLabel(item.content_type)}</span>
        <span className={`status-pill ${item.status}`}>{formatLabel(item.status)}</span>
        {progressStatus ? <ProgressBadge status={progressStatus} /> : null}
      </div>

      <div>
        <Link className="content-card-link" to={getContentHref(item)}>
          <h3>{item.title}</h3>
        </Link>
        <p className="panel-subtitle">{item.description}</p>
      </div>

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

      <div className="card-meta">
        <Link className="inline-link" to={getContentHref(item)}>
          Open lesson
        </Link>
      </div>
    </article>
  );
};
