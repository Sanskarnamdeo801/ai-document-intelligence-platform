import { useEffect, useMemo, useState } from 'react'
import EmptyState from '../components/EmptyState.jsx'
import ErrorMessage from '../components/ErrorMessage.jsx'
import SearchResultCard from '../components/SearchResultCard.jsx'
import { documentsApi, searchApi } from '../services/api.js'

function SearchPage() {
  const [documents, setDocuments] = useState([])
  const [query, setQuery] = useState('')
  const [topK, setTopK] = useState(5)
  const [documentId, setDocumentId] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    documentsApi.list().then(setDocuments).catch(() => setDocuments([]))
  }, [])

  const documentMap = useMemo(() => Object.fromEntries(documents.map((document) => [document.id, document.file_name])), [documents])

  const handleSearch = async () => {
    if (!query.trim()) {
      return
    }
    setLoading(true)
    setError('')
    try {
      const data = await searchApi.semanticSearch({
        query,
        top_k: Number(topK),
        document_id: documentId ? Number(documentId) : null,
      })
      setResults(data || [])
    } catch (searchError) {
      setError(searchError.message)
      setResults([])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page-stack">
      <section className="panel">
        <div className="panel__header">
          <div>
            <p className="eyebrow">Retrieval</p>
            <h2>Semantic search</h2>
          </div>
        </div>
        <div className="toolbar toolbar--stacked">
          <label className="field field--grow">
            <span>Query</span>
            <input
              type="text"
              placeholder="Search by meaning, topic, clause, or entity"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
            />
          </label>
          <label className="field field--small">
            <span>Top K</span>
            <select value={topK} onChange={(event) => setTopK(event.target.value)}>
              <option value={3}>3</option>
              <option value={5}>5</option>
              <option value={10}>10</option>
            </select>
          </label>
          <label className="field field--medium">
            <span>Document filter</span>
            <select value={documentId} onChange={(event) => setDocumentId(event.target.value)}>
              <option value="">All documents</option>
              {documents.map((document) => (
                <option key={document.id} value={document.id}>
                  {document.file_name || `Document #${document.id}`}
                </option>
              ))}
            </select>
          </label>
          <button type="button" className="button button-primary" onClick={handleSearch} disabled={loading}>
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
        {error ? <ErrorMessage message={error} compact /> : null}
      </section>

      <section className="panel">
        <div className="panel__header">
          <div>
            <p className="eyebrow">Results</p>
            <h2>{results.length ? `${results.length} matching chunks` : 'No results yet'}</h2>
          </div>
        </div>
        {results.length ? (
          <div className="result-list">
            {results.map((result) => (
              <SearchResultCard
                key={`${result.document_id}-${result.chunk_id}`}
                result={result}
                documentName={documentMap[result.document_id]}
              />
            ))}
          </div>
        ) : (
          <EmptyState
            title="No search results"
            description="Run a semantic query to inspect the most relevant document chunks."
          />
        )}
      </section>
    </div>
  )
}

export default SearchPage
