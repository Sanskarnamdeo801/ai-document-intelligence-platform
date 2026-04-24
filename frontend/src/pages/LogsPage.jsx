import { useEffect, useState } from 'react'
import EmptyState from '../components/EmptyState.jsx'
import ErrorMessage from '../components/ErrorMessage.jsx'
import LoadingSpinner from '../components/LoadingSpinner.jsx'
import LogTimeline from '../components/LogTimeline.jsx'
import { documentsApi } from '../services/api.js'

function LogsPage() {
  const [documents, setDocuments] = useState([])
  const [selectedDocumentId, setSelectedDocumentId] = useState('')
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const loadDocuments = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await documentsApi.list()
      setDocuments(data || [])
      if (!selectedDocumentId && data?.length) {
        setSelectedDocumentId(String(data[0].id))
      }
    } catch (loadError) {
      setError(loadError.message)
    } finally {
      setLoading(false)
    }
  }

  const loadLogs = async (documentId) => {
    if (!documentId) {
      setLogs([])
      return
    }
    try {
      const data = await documentsApi.getLogs(documentId)
      setLogs(data || [])
    } catch (loadError) {
      setError(loadError.message)
      setLogs([])
    }
  }

  useEffect(() => {
    loadDocuments()
  }, [])

  useEffect(() => {
    if (selectedDocumentId) {
      loadLogs(selectedDocumentId)
    }
  }, [selectedDocumentId])

  if (loading) {
    return <LoadingSpinner label="Loading log sources..." />
  }

  if (error && !documents.length) {
    return <ErrorMessage message={error} onRetry={loadDocuments} />
  }

  return (
    <div className="page-stack">
      <section className="panel">
        <div className="panel__header">
          <div>
            <p className="eyebrow">Execution trace</p>
            <h2>Document pipeline logs</h2>
          </div>
          <button type="button" className="button button-secondary" onClick={() => loadLogs(selectedDocumentId)}>
            Refresh logs
          </button>
        </div>

        <div className="toolbar">
          <label className="field field--grow">
            <span>Document</span>
            <select value={selectedDocumentId} onChange={(event) => setSelectedDocumentId(event.target.value)}>
              <option value="">Select a document</option>
              {documents.map((document) => (
                <option key={document.id} value={document.id}>
                  {document.file_name || `Document #${document.id}`}
                </option>
              ))}
            </select>
          </label>
        </div>

        {error ? <ErrorMessage message={error} compact /> : null}

        {logs.length ? (
          <LogTimeline logs={logs} />
        ) : (
          <EmptyState
            title="No logs to show"
            description="Select a document that has been uploaded or processed to inspect its pipeline timeline."
          />
        )}
      </section>
    </div>
  )
}

export default LogsPage
