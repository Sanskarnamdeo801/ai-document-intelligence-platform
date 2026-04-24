import { useEffect, useMemo, useState } from 'react'
import DocumentTable from '../components/DocumentTable.jsx'
import EmptyState from '../components/EmptyState.jsx'
import ErrorMessage from '../components/ErrorMessage.jsx'
import LoadingSpinner from '../components/LoadingSpinner.jsx'
import { documentsApi } from '../services/api.js'

function DocumentsPage() {
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [searchTerm, setSearchTerm] = useState('')
  const [processingId, setProcessingId] = useState(null)

  const loadDocuments = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await documentsApi.list()
      setDocuments(data || [])
    } catch (loadError) {
      setError(loadError.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadDocuments()
  }, [])

  const filteredDocuments = useMemo(() => {
    return documents.filter((document) => {
      const matchesStatus = statusFilter === 'all' || document.status === statusFilter
      const term = searchTerm.trim().toLowerCase()
      const matchesSearch = !term || document.file_name?.toLowerCase().includes(term) || String(document.id).includes(term)
      return matchesStatus && matchesSearch
    })
  }, [documents, searchTerm, statusFilter])

  const handleProcess = async (document) => {
    setProcessingId(document.id)
    try {
      await documentsApi.process(document.id)
      await loadDocuments()
    } catch (processError) {
      setError(processError.message)
    } finally {
      setProcessingId(null)
    }
  }

  if (loading) {
    return <LoadingSpinner label="Loading documents..." />
  }

  if (error && documents.length === 0) {
    return <ErrorMessage message={error} onRetry={loadDocuments} />
  }

  return (
    <div className="page-stack">
      <section className="panel">
        <div className="panel__header">
          <div>
            <p className="eyebrow">Document library</p>
            <h2>All uploaded documents</h2>
          </div>
          <button type="button" className="button button-secondary" onClick={loadDocuments}>
            Refresh
          </button>
        </div>

        <div className="toolbar">
          <label className="field">
            <span>Search</span>
            <input
              type="search"
              placeholder="Search by file name or document ID"
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
            />
          </label>
          <label className="field field--small">
            <span>Status</span>
            <select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
              <option value="all">All statuses</option>
              <option value="uploaded">Uploaded</option>
              <option value="processing">Processing</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
            </select>
          </label>
        </div>

        {error ? <ErrorMessage message={error} compact /> : null}

        {filteredDocuments.length ? (
          <DocumentTable documents={filteredDocuments} onProcess={handleProcess} processingId={processingId} />
        ) : (
          <EmptyState
            title="No matching documents"
            description="Adjust the search term or status filter, or upload a new document."
          />
        )}
      </section>
    </div>
  )
}

export default DocumentsPage
