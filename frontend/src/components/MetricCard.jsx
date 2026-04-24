function MetricCard({ label, value, accent, helper }) {
  return (
    <article className="metric-card">
      <span className="metric-card__accent" style={{ background: accent }} />
      <div className="metric-card__content">
        <p className="metric-card__label">{label}</p>
        <strong className="metric-card__value">{value}</strong>
        {helper ? <span className="metric-card__helper">{helper}</span> : null}
      </div>
    </article>
  )
}

export default MetricCard
