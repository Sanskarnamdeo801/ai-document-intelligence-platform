import StatusBadge from './StatusBadge.jsx'
import { formatDateTime } from '../utils/formatters.js'

function LogTimeline({ logs = [] }) {
  return (
    <div className="timeline">
      {logs.map((log, index) => (
        <article key={`${log.stage}-${log.created_at}-${index}`} className="timeline-item">
          <div className="timeline-item__rail" />
          <div className="timeline-item__body">
            <div className="timeline-item__header">
              <div>
                <h4>{log.stage || 'Unknown stage'}</h4>
                <p>{formatDateTime(log.created_at)}</p>
              </div>
              <StatusBadge status={log.status || 'unknown'} />
            </div>
            <p className="timeline-item__message">{log.message || 'No message provided.'}</p>
            {log.error_trace ? (
              <details className="timeline-item__error">
                <summary>View error trace</summary>
                <pre>{log.error_trace}</pre>
              </details>
            ) : null}
          </div>
        </article>
      ))}
    </div>
  )
}

export default LogTimeline
