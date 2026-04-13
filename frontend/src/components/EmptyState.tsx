import { Link } from "react-router-dom";

interface EmptyStateProps {
  title: string;
  message: string;
  actionLabel?: string;
  actionTo?: string;
}

export const EmptyState = ({
  title,
  message,
  actionLabel,
  actionTo,
}: EmptyStateProps) => {
  return (
    <div className="empty-state">
      <h3>{title}</h3>
      <p>{message}</p>
      {actionLabel && actionTo ? (
        <Link className="primary-link-button" to={actionTo}>
          {actionLabel}
        </Link>
      ) : null}
    </div>
  );
};
