import { formatStatusLabel } from '../utils/formatters.js'

function StatusBadge({ status = 'unknown' }) {
  const normalizedStatus = status.toLowerCase()
  const className = `status-badge status-badge--${normalizedStatus}`

  return <span className={className}>{formatStatusLabel(status)}</span>
}

export default StatusBadge
