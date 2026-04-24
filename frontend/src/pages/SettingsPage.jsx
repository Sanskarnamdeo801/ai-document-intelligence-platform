import { useEffect, useState } from 'react'
import ErrorMessage from '../components/ErrorMessage.jsx'
import LoadingSpinner from '../components/LoadingSpinner.jsx'
import { API_BASE_URL, systemApi } from '../services/api.js'

function SettingsPage() {
  const [health, setHealth] = useState(null)
  const [dbHealth, setDbHealth] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const loadHealth = async () => {
    setLoading(true)
    setError('')
    const [healthResult, dbHealthResult] = await Promise.allSettled([
      systemApi.getHealth(),
      systemApi.getDatabaseHealth(),
    ])

    if (healthResult.status === 'fulfilled') {
      setHealth(healthResult.value)
    } else {
      setHealth(null)
      setError(healthResult.reason?.message || 'Backend health check failed.')
    }

    if (dbHealthResult.status === 'fulfilled') {
      setDbHealth(dbHealthResult.value)
    } else {
      setDbHealth(null)
    }

    setLoading(false)
  }

  useEffect(() => {
    loadHealth()
  }, [])

  if (loading) {
    return <LoadingSpinner label="Checking system health..." />
  }

  return (
    <div className="page-stack">
      <section className="panel">
        <div className="panel__header">
          <div>
            <p className="eyebrow">Runtime settings</p>
            <h2>System health and frontend configuration</h2>
          </div>
          <button type="button" className="button button-secondary" onClick={loadHealth}>
            Refresh health
          </button>
        </div>

        {error ? <ErrorMessage message={error} compact /> : null}

        <div className="settings-grid">
          <article className="settings-card">
            <span>Backend API URL</span>
            <strong>{API_BASE_URL}</strong>
            <p>Configured from `VITE_API_BASE_URL` or the frontend fallback.</p>
          </article>
          <article className="settings-card">
            <span>Health endpoint</span>
            <strong>{health?.status || 'Unavailable'}</strong>
            <p>GET /health</p>
          </article>
          <article className="settings-card">
            <span>Database health</span>
            <strong>{dbHealth?.status || 'Unavailable'}</strong>
            <p>GET /health/db</p>
          </article>
          <article className="settings-card">
            <span>Ollama model</span>
            <strong>{import.meta.env.VITE_OLLAMA_MODEL || 'Not exposed to frontend env'}</strong>
            <p>Displayed only if provided through Vite env variables.</p>
          </article>
          <article className="settings-card">
            <span>Embedding model</span>
            <strong>{import.meta.env.VITE_EMBEDDING_MODEL || 'Not exposed to frontend env'}</strong>
            <p>Displayed only if provided through Vite env variables.</p>
          </article>
          <article className="settings-card">
            <span>Upload / log directories</span>
            <strong>Not exposed by backend API</strong>
            <p>The current backend does not return filesystem paths to the UI.</p>
          </article>
        </div>
      </section>
    </div>
  )
}

export default SettingsPage
