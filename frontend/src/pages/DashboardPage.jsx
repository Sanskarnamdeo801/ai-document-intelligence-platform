import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import EmptyState from '../components/EmptyState.jsx'
import ErrorMessage from '../components/ErrorMessage.jsx'
import LoadingSpinner from '../components/LoadingSpinner.jsx'
import MetricCard from '../components/MetricCard.jsx'
import RecentActivity from '../components/RecentActivity.jsx'
import StatusBadge from '../components/StatusBadge.jsx'
import { dashboardApi, documentsApi, systemApi } from '../services/api.js'
import { formatDateTime, formatFileSize } from '../utils/formatters.js'

function DashboardPage() {
  const [metrics, setMetrics] = useState(null)
  const [documents, setDocuments] = useState([])
  const [activity, setActivity] = useState([])
  const [health, setHealth] = useState({ status: 'loading', detail: 'Checking backend...' })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const loadDashboard = async () => {
    setLoading(true)
    setError('')

    const [metricsResult, documentsResult, activityResult, healthResult] = await Promise.allSettled([
      dashboardApi.getMetrics(),
      documentsApi.list(),
      dashboardApi.getRecentActivity(),
      systemApi.getHealth(),
    ])

    if (metricsResult.status === 'fulfilled') {
      setMetrics(metricsResult.value)
    }
    if (documentsResult.status === 'fulfilled') {
      setDocuments(documentsResult.value || [])
    }
    if (activityResult.status === 'fulfilled') {
      setActivity(activityResult.value || [])
    }
    if (healthResult.status === 'fulfilled') {
      setHealth({ status: 'online', detail: healthResult.value?.status || 'healthy' })
    } else {
      setHealth({ status: 'offline', detail: healthResult.reason?.message || 'Unable to reach backend.' })
    }

    const failures = [metricsResult, documentsResult, activityResult].filter((result) => result.status === 'rejected')
    if (failures.length === 3) {
      setError('Dashboard data could not be loaded. Confirm that the backend is running and the database schema is current.')
    }

    setLoading(false)
  }

  useEffect(() => {
    loadDashboard()
  }, [])

  const cards = useMemo(() => [
    { label: 'Total Documents', value: metrics?.total_documents ?? 0, helper: 'Files tracked in the platform', accent: 'linear-gradient(135deg, #1f6feb, #4098ff)' },
    { label: 'Processed Documents', value: metrics?.completed_documents ?? 0, helper: 'Documents ready for search and Q&A', accent: 'linear-gradient(135deg, #0f9f6e, #29c68b)' },
    { label: 'Processing', value: metrics?.processing_documents ?? 0, helper: 'Documents currently in the pipeline', accent: 'linear-gradient(135deg, #f59e0b, #fbbf24)' },
    { label: 'Failed', value: metrics?.failed_documents ?? 0, helper: 'Documents requiring retry or review', accent: 'linear-gradient(135deg, #dc2626, #f87171)' },
    { label: 'Total Chunks', value: metrics?.total_chunks ?? 0, helper: 'Chunk records stored for retrieval', accent: 'linear-gradient(135deg, #0f172a, #334155)' },
    { label: 'Total Queries', value: metrics?.total_queries ?? 0, helper: 'Search and Q&A requests recorded', accent: 'linear-gradient(135deg, #5b21b6, #7c3aed)' },
  ], [metrics])

  const recentDocuments = documents.slice(0, 6)

  if (loading) {
    return <LoadingSpinner label="Loading dashboard..." />
  }

  if (error) {
    return <ErrorMessage message={error} onRetry={loadDashboard} />
  }

  return (
    <div className="page-stack">
      <section className="metrics-grid">
        {cards.map((card) => (
          <MetricCard key={card.label} {...card} />
        ))}
      </section>

      <section className="content-grid content-grid--dashboard">
        <article className="panel">
          <div className="panel__header">
            <div>
              <p className="eyebrow">Live status</p>
              <h2>Backend health</h2>
            </div>
            <button type="button" className="button button-secondary button-small" onClick={loadDashboard}>
              Refresh
            </button>
          </div>
          <div className="health-card">
            <div className={`health-pill health-pill--${health.status}`} />
            <div>
              <strong>{health.status === 'online' ? 'Backend reachable' : 'Backend unreachable'}</strong>
              <p>{health.detail}</p>
            </div>
          </div>
          <div className="quick-actions">
            <Link to="/upload" className="button button-primary">Upload a document</Link>
            <Link to="/search" className="button button-secondary">Run semantic search</Link>
          </div>
        </article>

        <article className="panel">
          <div className="panel__header">
            <div>
              <p className="eyebrow">Activity feed</p>
              <h2>Recent backend activity</h2>
            </div>
            <Link to="/logs" className="inline-link">View logs</Link>
          </div>
          {activity.length ? (
            <RecentActivity items={activity.slice(0, 8)} />
          ) : (
            <EmptyState
              title="No recent activity"
              description="Upload and process documents to populate the activity timeline."
            />
          )}
        </article>
      </section>

      <section className="panel">
        <div className="panel__header">
          <div>
            <p className="eyebrow">Latest uploads</p>
            <h2>Recent documents</h2>
          </div>
          <Link to="/documents" className="inline-link">Open full library</Link>
        </div>

        {recentDocuments.length ? (
          <div className="document-card-grid">
            {recentDocuments.map((document) => (
              <article key={document.id} className="document-card">
                <div className="document-card__topline">
                  <div>
                    <h3>{document.file_name || `Document #${document.id}`}</h3>
                    <p>{formatFileSize(document.file_size)}</p>
                  </div>
                  <StatusBadge status={document.status} />
                </div>
                <div className="document-card__meta">
                  <span>Uploaded {formatDateTime(document.upload_time)}</span>
                  <span>{document.file_type || document.mime_type || 'Unknown type'}</span>
                </div>
                <Link to={`/documents/${document.id}`} className="button button-secondary button-small">
                  View details
                </Link>
              </article>
            ))}
          </div>
        ) : (
          <EmptyState
            title="No documents yet"
            description="Start by uploading a document to populate the dashboard."
            action={
              <Link to="/upload" className="button button-primary">
                Go to upload
              </Link>
            }
          />
        )}
      </section>
    </div>
  )
}

export default DashboardPage
