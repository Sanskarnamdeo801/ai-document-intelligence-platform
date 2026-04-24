import { Link } from 'react-router-dom'
import StatusBadge from './StatusBadge.jsx'
import { formatDateTime, formatFileSize, formatStatusLabel } from '../utils/formatters.js'

function DocumentTable({ documents = [], onProcess, processingId }) {
  return (
    <div className="table-shell">
      <table className="data-table">
        <thead>
          <tr>
            <th>File Name</th>
            <th>Type</th>
            <th>Size</th>
            <th>Status</th>
            <th>Uploaded</th>
            <th>Processed</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {documents.map((document) => (
            <tr key={document.id}>
              <td>
                <div className="table-primary">
                  <strong>{document.file_name || `Document #${document.id}`}</strong>
                  <span>#{document.id}</span>
                </div>
              </td>
              <td>{formatStatusLabel(document.file_type || document.mime_type || 'unknown')}</td>
              <td>{formatFileSize(document.file_size)}</td>
              <td>
                <StatusBadge status={document.status} />
              </td>
              <td>{formatDateTime(document.upload_time)}</td>
              <td>{formatDateTime(document.processed_time)}</td>
              <td>
                <div className="table-actions">
                  <Link to={`/documents/${document.id}`} className="button button-secondary button-small">
                    Details
                  </Link>
                  {onProcess ? (
                    <button
                      type="button"
                      className="button button-ghost button-small"
                      onClick={() => onProcess(document)}
                      disabled={processingId === document.id || document.status === 'processing'}
                    >
                      {processingId === document.id
                        ? 'Starting...'
                        : document.status === 'failed'
                          ? 'Retry'
                          : 'Process'}
                    </button>
                  ) : null}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default DocumentTable
