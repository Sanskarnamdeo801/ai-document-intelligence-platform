function ErrorMessage({ message = 'Something went wrong.', onRetry, compact = false }) {
  return (
    <div className={`error-message ${compact ? 'error-message--compact' : ''}`}>
      <div>
        <h3>Request failed</h3>
        <p>{message}</p>
      </div>
      {onRetry ? (
        <button type="button" className="button button-secondary" onClick={onRetry}>
          Retry
        </button>
      ) : null}
    </div>
  )
}

export default ErrorMessage
