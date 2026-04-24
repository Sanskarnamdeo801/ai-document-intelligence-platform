import { Link } from 'react-router-dom'
import { formatDateTime } from '../utils/formatters.js'

function RecentActivity({ items = [] }) {
  return (
    <div className="activity-list">
      {items.map((item, index) => (
        <div key={`${item.activity_type}-${item.created_at}-${index}`} className="activity-item">
          <div className="activity-item__marker" />
          <div className="activity-item__content">
            <div className="activity-item__topline">
              <span className="activity-item__type">{item.activity_type || 'activity'}</span>
              <span className="activity-item__time">{formatDateTime(item.created_at)}</span>
            </div>
            <p>{item.message || 'No activity details available.'}</p>
            {item.document_id ? (
              <Link to={`/documents/${item.document_id}`} className="inline-link">
                View document
              </Link>
            ) : null}
          </div>
        </div>
      ))}
    </div>
  )
}

export default RecentActivity
