function SourceChunkCard({ source, documentName }) {
  return (
    <article className="source-card">
      <div className="source-card__header">
        <strong>{documentName || `Document #${source.document_id}`}</strong>
        <span>Chunk #{source.chunk_id}</span>
      </div>
      <p>{source.chunk_text || 'No source text provided.'}</p>
      <span className="source-card__score">
        Relevance {(Number(source.similarity || 0) * 100).toFixed(1)}%
      </span>
    </article>
  )
}

export default SourceChunkCard
