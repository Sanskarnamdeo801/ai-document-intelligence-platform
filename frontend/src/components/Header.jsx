import { Link, useLocation } from 'react-router-dom'

const pageMeta = {
  '/': {
    title: 'Document Intelligence Dashboard',
    subtitle: 'Monitor ingestion, processing, search, and AI-assisted answers in one place.',
  },
  '/upload': {
    title: 'Upload Documents',
    subtitle: 'Ingest PDF, DOCX, and TXT files and hand them off to the backend pipeline.',
  },
  '/documents': {
    title: 'Document Library',
    subtitle: 'Review every uploaded document, its status, and processing readiness.',
  },
  '/search': {
    title: 'Semantic Search',
    subtitle: 'Query stored chunk embeddings and inspect the most relevant document passages.',
  },
  '/ask': {
    title: 'Ask AI',
    subtitle: 'Run retrieval-augmented Q&A against all documents or a selected source.',
  },
  '/logs': {
    title: 'Pipeline Logs',
    subtitle: 'Track stage-by-stage processing signals, warnings, and failures.',
  },
  '/settings': {
    title: 'System Health',
    subtitle: 'Verify API connectivity, health endpoints, and frontend runtime settings.',
  },
}

function Header({ onToggleSidebar }) {
  const location = useLocation()
  const meta = pageMeta[location.pathname] || {
    title: 'Document Details',
    subtitle: 'Inspect extracted content, generated outputs, and backend logs for a single document.',
  }

  return (
    <header className="topbar">
      <div className="topbar__content">
        <div className="topbar__intro">
          <button type="button" className="topbar__menu" onClick={onToggleSidebar} aria-label="Open navigation">
            <span />
            <span />
            <span />
          </button>
          <div>
            <p className="eyebrow">AI Document Intelligence Platform</p>
            <h1>{meta.title}</h1>
            <p className="topbar__subtitle">{meta.subtitle}</p>
          </div>
        </div>
        <div className="topbar__actions">
          <Link to="/upload" className="button button-primary">
            Upload
          </Link>
          <Link to="/ask" className="button button-secondary">
            Ask AI
          </Link>
        </div>
      </div>
    </header>
  )
}

export default Header
