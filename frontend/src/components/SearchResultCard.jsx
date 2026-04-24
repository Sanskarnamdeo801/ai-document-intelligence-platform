import { Link } from 'react-router-dom'

function SearchResultCard({ result, documentName }) {
  return (
    <article className="result-card">
      <div className="result-card__header">
        <div>
          <h3>{documentName || `Document #${result.document_id}`}</h3>
          <p>
            Chunk #{result.chunk_id} • Similarity {(Number(result.similarity || 0) * 100).toFixed(1)}%
          </p>
        </div>
        <Link to={`/documents/${result.document_id}`} className="button button-secondary button-small">
          Open
        </Link>
      </div>
      <p className="result-card__text">{result.chunk_text || 'No chunk text returned.'}</p>
    </article>
  )
}

export default SearchResultCard
