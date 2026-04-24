import { useEffect, useMemo, useState } from 'react'
import EmptyState from '../components/EmptyState.jsx'
import ErrorMessage from '../components/ErrorMessage.jsx'
import SourceChunkCard from '../components/SourceChunkCard.jsx'
import { documentsApi, qaApi } from '../services/api.js'
import { formatDateTime } from '../utils/formatters.js'

function AskPage() {
  const [documents, setDocuments] = useState([])
  const [question, setQuestion] = useState('')
  const [selectedDocumentId, setSelectedDocumentId] = useState('')
  const [topK, setTopK] = useState(3)
  const [chatHistory, setChatHistory] = useState(() => {
    try {
      const stored = window.sessionStorage.getItem('ai-document-chat-history')
      return stored ? JSON.parse(stored) : []
    } catch {
      return []
    }
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    documentsApi.list().then(setDocuments).catch(() => setDocuments([]))
  }, [])

  useEffect(() => {
    window.sessionStorage.setItem('ai-document-chat-history', JSON.stringify(chatHistory))
  }, [chatHistory])

  const documentMap = useMemo(() => Object.fromEntries(documents.map((document) => [document.id, document.file_name])), [documents])

  const handleAsk = async () => {
    if (!question.trim()) {
      return
    }

    setLoading(true)
    setError('')
    try {
      const response = await qaApi.askQuestion({
        question,
        document_id: selectedDocumentId ? Number(selectedDocumentId) : null,
        top_k: Number(topK),
      })
      setChatHistory((current) => [
        {
          id: `${Date.now()}-${current.length}`,
          question,
          documentId: selectedDocumentId ? Number(selectedDocumentId) : null,
          createdAt: new Date().toISOString(),
          answer: response.answer,
          sources: response.sources || [],
        },
        ...current,
      ])
      setQuestion('')
    } catch (qaError) {
      setError(qaError.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page-stack">
      <section className="panel">
        <div className="panel__header">
          <div>
            <p className="eyebrow">AI workspace</p>
            <h2>Ask the document corpus</h2>
          </div>
        </div>
        <div className="toolbar toolbar--stacked">
          <label className="field field--grow">
            <span>Question</span>
            <textarea
              rows="3"
              placeholder="Ask about obligations, entities, dates, renewals, or any document topic."
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
            />
          </label>
          <div className="toolbar">
            <label className="field field--medium">
              <span>Document scope</span>
              <select value={selectedDocumentId} onChange={(event) => setSelectedDocumentId(event.target.value)}>
                <option value="">All documents</option>
                {documents.map((document) => (
                  <option key={document.id} value={document.id}>
                    {document.file_name || `Document #${document.id}`}
                  </option>
                ))}
              </select>
            </label>
            <label className="field field--small">
              <span>Top K</span>
              <select value={topK} onChange={(event) => setTopK(event.target.value)}>
                <option value={3}>3</option>
                <option value={5}>5</option>
                <option value={7}>7</option>
              </select>
            </label>
          </div>
          <button type="button" className="button button-primary" onClick={handleAsk} disabled={loading}>
            {loading ? 'Thinking...' : 'Ask AI'}
          </button>
        </div>
        {error ? <ErrorMessage message={error} compact /> : null}
      </section>

      <section className="panel">
        <div className="panel__header">
          <div>
            <p className="eyebrow">Session history</p>
            <h2>Answers in this browser session</h2>
          </div>
        </div>
        {chatHistory.length ? (
          <div className="chat-thread">
            {chatHistory.map((entry) => (
              <article key={entry.id} className="chat-card">
                <div className="chat-card__question">
                  <span className="eyebrow">Question • {formatDateTime(entry.createdAt)}</span>
                  <h3>{entry.question}</h3>
                  <p>{entry.documentId ? `Scoped to ${documentMap[entry.documentId] || `Document #${entry.documentId}`}` : 'Scoped to all documents'}</p>
                </div>
                <div className="chat-card__answer">
                  <span className="eyebrow">Answer</span>
                  <p>{entry.answer || 'No answer returned.'}</p>
                  {entry.sources?.length ? (
                    <div className="source-list">
                      {entry.sources.map((source) => (
                        <SourceChunkCard
                          key={`${entry.id}-${source.document_id}-${source.chunk_id}`}
                          source={source}
                          documentName={documentMap[source.document_id]}
                        />
                      ))}
                    </div>
                  ) : null}
                </div>
              </article>
            ))}
          </div>
        ) : (
          <EmptyState
            title="No AI answers yet"
            description="Ask a question to start a local chat history for this session."
          />
        )}
      </section>
    </div>
  )
}

export default AskPage
