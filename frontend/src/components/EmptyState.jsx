function EmptyState({ title, description, action }) {
  return (
    <div className="empty-state">
      <div className="empty-state__icon">AI</div>
      <h3>{title}</h3>
      <p>{description}</p>
      {action}
    </div>
  )
}

export default EmptyState
