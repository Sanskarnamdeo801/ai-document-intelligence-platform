import { useEffect, useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import EmptyState from '../components/EmptyState.jsx'
import ErrorMessage from '../components/ErrorMessage.jsx'
import LoadingSpinner from '../components/LoadingSpinner.jsx'
import LogTimeline from '../components/LogTimeline.jsx'
import SourceChunkCard from '../components/SourceChunkCard.jsx'
import StatusBadge from '../components/StatusBadge.jsx'
import { documentsApi, qaApi } from '../services/api.js'
import { formatDateTime, formatFileSize } from '../utils/formatters.js'

function DocumentDetailsPage() {
  const { id } = useParams()
  const [document, setDocument] = useState(null)
  const [summary, setSummary] = useState(null)
  const [metadata, setMetadata] = useState(null)
  const [chunks, setChunks] = useState([])
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [expandedChunks, setExpandedChunks] = useState({})
  const [processState, setProcessState] = useState({ loading: false, message: '' })
  const [qaQuestion, setQaQuestion] = useState('')
  const [qaResponse, setQaResponse] = useState(null)
  const [qaLoading, setQaLoading] = useState(false)

  const loadDocument = async () => {
    setLoading(true)
    setError('')

    try {
      const documentData = await documentsApi.get(id)
      setDocument(documentData)

      const [summaryResult, metadataResult, chunksResult, logsResult] = await Promise.allSettled([
        documentsApi.getSummary(id),
        documentsApi.getMetadata(id),
        documentsApi.getChunks(id),
        documentsApi.getLogs(id),
      ])

      setSummary(summaryResult.status === 'fulfilled' ? summaryResult.value : null)
      setMetadata(metadataResult.status === 'fulfilled' ? metadataResult.value : null)
      setChunks(chunksResult.status === 'fulfilled' ? chunksResult.value || [] : [])
      setLogs(logsResult.status === 'fulfilled' ? logsResult.value || [] : [])
    } catch (loadError) {
      setError(loadError.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadDocument()
  }, [id])

  const detailItems = useMemo(() => [
    { label: 'Document ID', value: document?.id ?? 'Unknown' },
    { label: 'File type', value: document?.file_type || document?.mime_type || 'Unknown' },
    { label: 'File size', value: formatFileSize(document?.file_size) },
    { label: 'Uploaded', value: formatDateTime(document?.upload_time) },
    { label: 'Processed', value: formatDateTime(document?.processed_time) },
    { label: 'Checksum', value: document?.checksum || 'Not available' },
  ], [document])

  const handleProcess = async () => {
    setProcessState({ loading: true, message: '' })
    try {
      const response = await documentsApi.process(id)
      setProcessState({ loading: false, message: response.message || 'Processing started.' })
      await loadDocument()
    } catch (processError) {
      setProcessState({ loading: false, message: processError.message })
    }
  }

  const handleAsk = async () => {
    if (!qaQuestion.trim()) {
      return
    }
    setQaLoading(true)
    try {
      const response = await qaApi.askQuestion({
        question: qaQuestion,
        document_id: Number(id),
        top_k: 3,
      })
      setQaResponse(response)
    } catch (qaError) {
      setQaResponse({ answer: qaError.message, sources: [] })
    } finally {
      setQaLoading(false)
    }
  }

  if (loading) {
    return <LoadingSpinner label="Loading document details..." />
  }

  if (error || !document) {
    return <ErrorMessage message={error || 'Document not found.'} onRetry={loadDocument} />
  }

  return (
    <div className="page-stack">
      <section className="panel">
        <div className="panel__header">
          <div>
            <p className="eyebrow">Document overview</p>
            <h2>{document.file_name || `Document #${document.id}`}</h2>
          </div>
          <div className="panel__actions">
            <StatusBadge status={document.status} />
            <button type="button" className="button button-primary" onClick={handleProcess} disabled={processState.loading || document.status === 'processing'}>
              {processState.loading ? 'Starting...' : document.status === 'failed' ? 'Retry processing' : 'Trigger processing'}
            </button>
          </div>
        </div>
        {processState.message ? <div className="callout">{processState.message}</div> : null}
        <div className="details-grid">
          {detailItems.map((item) => (
            <div key={item.label} className="detail-card">
              <span>{item.label}</span>
              <strong>{item.value}</strong>
            </div>
          ))}
        </div>
      </section>

      <section className="content-grid content-grid--details">
        <article className="panel">
          <div className="panel__header">
            <div>
              <p className="eyebrow">AI summary</p>
              <h2>Summary</h2>
            </div>
          </div>
          {summary ? (
            <p className="rich-text">{summary.summary_text}</p>
          ) : (
            <EmptyState
              title="Summary not ready"
              description="Run document processing to generate an AI summary."
            />
          )}
        </article>

        <article className="panel">
          <div className="panel__header">
            <div>
              <p className="eyebrow">Structured fields</p>
              <h2>Metadata</h2>
            </div>
          </div>
          {metadata ? (
            <div className="metadata-grid">
              <div className="metadata-row"><span>Title</span><strong>{metadata.title || 'Not available'}</strong></div>
              <div className="metadata-row"><span>Document type</span><strong>{metadata.doc_type || 'Unknown'}</strong></div>
              <div className="metadata-row"><span>Language</span><strong>{metadata.language || 'Unknown'}</strong></div>
              <div className="metadata-row"><span>Effective date</span><strong>{metadata.effective_date || 'Not available'}</strong></div>
              <div className="metadata-row"><span>Expiration date</span><strong>{metadata.expiration_date || 'Not available'}</strong></div>
              <div className="metadata-row"><span>Parties</span><strong>{metadata.parties?.length ? metadata.parties.join(', ') : 'None detected'}</strong></div>
              <div className="metadata-row"><span>Tags</span><strong>{metadata.tags?.length ? metadata.tags.join(', ') : 'No tags generated'}</strong></div>
            </div>
          ) : (
            <EmptyState
              title="Metadata not ready"
              description="Metadata appears after the backend completes extraction and analysis."
            />
          )}
        </article>
      </section>

      <section className="content-grid content-grid--details">
        <article className="panel">
          <div className="panel__header">
            <div>
              <p className="eyebrow">Extracted chunks</p>
              <h2>Chunk browser</h2>
            </div>
            <span className="panel__meta">{chunks.length} chunks</span>
          </div>
          {chunks.length ? (
            <div className="chunk-list">
              {chunks.map((chunk) => {
                const expanded = Boolean(expandedChunks[chunk.id])
                const preview = expanded ? chunk.chunk_text : `${chunk.chunk_text?.slice(0, 240) || ''}${chunk.chunk_text?.length > 240 ? '...' : ''}`
                return (
                  <article key={chunk.id} className="chunk-card">
                    <div className="chunk-card__header">
                      <div>
                        <h3>Chunk #{chunk.chunk_index}</h3>
                        <p>Chunk ID {chunk.id} • Page {chunk.page_number || 'N/A'} • {chunk.token_count} tokens</p>
                      </div>
                      <button
                        type="button"
                        className="button button-ghost button-small"
                        onClick={() => setExpandedChunks((current) => ({ ...current, [chunk.id]: !expanded }))}
                      >
                        {expanded ? 'Collapse' : 'Expand'}
                      </button>
                    </div>
                    <p>{preview || 'No chunk text available.'}</p>
                  </article>
                )
              })}
            </div>
          ) : (
            <EmptyState
              title="No chunks available"
              description="Chunk records will appear after extraction, cleaning, and chunking finish."
            />
          )}
        </article>

        <article className="panel">
          <div className="panel__header">
            <div>
              <p className="eyebrow">Ask this document</p>
              <h2>Document Q&A</h2>
            </div>
            <Link to="/ask" className="inline-link">Open full AI page</Link>
          </div>
          <div className="qa-panel">
            <textarea
              rows="4"
              placeholder="Ask a question grounded in this document."
              value={qaQuestion}
              onChange={(event) => setQaQuestion(event.target.value)}
            />
            <button type="button" className="button button-primary" onClick={handleAsk} disabled={qaLoading}>
              {qaLoading ? 'Asking...' : 'Ask question'}
            </button>
          </div>
          {qaResponse ? (
            <div className="answer-card">
              <h3>Answer</h3>
              <p>{qaResponse.answer || 'No answer returned.'}</p>
              {qaResponse.sources?.length ? (
                <div className="source-list">
                  {qaResponse.sources.map((source) => (
                    <SourceChunkCard
                      key={`${source.document_id}-${source.chunk_id}`}
                      source={source}
                      documentName={document.file_name}
                    />
                  ))}
                </div>
              ) : null}
            </div>
          ) : null}
        </article>
      </section>

      <section className="panel">
        <div className="panel__header">
          <div>
            <p className="eyebrow">Pipeline execution</p>
            <h2>Document logs</h2>
          </div>
        </div>
        {logs.length ? (
          <LogTimeline logs={logs} />
        ) : (
          <EmptyState
            title="No pipeline logs yet"
            description="Logs will appear once the document has been uploaded or processing has started."
          />
        )}
      </section>
    </div>
  )
}

export default DocumentDetailsPage
