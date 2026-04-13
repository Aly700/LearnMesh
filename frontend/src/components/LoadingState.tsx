interface LoadingStateProps {
  title: string;
  message: string;
}

export const LoadingState = ({ title, message }: LoadingStateProps) => {
  return (
    <div className="loading-state">
      <div className="loading-state-bar" />
      <div className="loading-state-bar short" />
      <h3>{title}</h3>
      <p>{message}</p>
    </div>
  );
};
