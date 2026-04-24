function LoadingSpinner({ label = 'Loading...', compact = false }) {
  return (
    <div className={`loading-state ${compact ? 'loading-state--compact' : ''}`}>
      <span className="spinner" aria-hidden="true" />
      <span>{label}</span>
    </div>
  )
}

export default LoadingSpinner
