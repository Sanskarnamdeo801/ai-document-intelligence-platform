import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import ErrorMessage from '../components/ErrorMessage.jsx'
import UploadDropzone from '../components/UploadDropzone.jsx'
import { documentsApi } from '../services/api.js'
import { formatFileSize } from '../utils/formatters.js'

function UploadPage() {
  const [file, setFile] = useState(null)
  const [progress, setProgress] = useState(0)
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState('')
  const [uploadedDocument, setUploadedDocument] = useState(null)

  const filePreview = useMemo(() => {
    if (!file) {
      return null
    }
    return {
      name: file.name,
      size: formatFileSize(file.size),
      type: file.type || 'Unknown type',
    }
  }, [file])

  const handleUpload = async () => {
    if (!file) {
      return
    }

    setIsUploading(true)
    setError('')
    setUploadedDocument(null)
    setProgress(0)

    const formData = new FormData()
    formData.append('file', file)
    formData.append('created_by', 'frontend-user')

    try {
      const document = await documentsApi.upload(formData, (event) => {
        if (event.total) {
          setProgress(Math.round((event.loaded * 100) / event.total))
        }
      })
      setUploadedDocument(document)
      setFile(null)
      setProgress(100)
    } catch (uploadError) {
      setError(uploadError.message)
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="page-stack">
      <section className="panel panel--wide">
        <div className="panel__header">
          <div>
            <p className="eyebrow">Ingestion</p>
            <h2>Upload a new document</h2>
          </div>
        </div>
        <UploadDropzone file={file} onFileSelect={setFile} disabled={isUploading} />

        {filePreview ? (
          <div className="file-preview">
            <div>
              <span className="eyebrow">Selected file</span>
              <h3>{filePreview.name}</h3>
              <p>{filePreview.type} • {filePreview.size}</p>
            </div>
            <button type="button" className="button button-primary" onClick={handleUpload} disabled={isUploading}>
              {isUploading ? 'Uploading...' : 'Upload document'}
            </button>
          </div>
        ) : null}

        {isUploading ? (
          <div className="progress-card">
            <div className="progress-card__header">
              <strong>Uploading document</strong>
              <span>{progress}%</span>
            </div>
            <div className="progress-bar">
              <span style={{ width: `${progress}%` }} />
            </div>
          </div>
        ) : null}

        {error ? <ErrorMessage message={error} compact /> : null}

        {uploadedDocument ? (
          <div className="success-card">
            <div>
              <span className="eyebrow">Upload complete</span>
              <h3>{uploadedDocument.file_name || `Document #${uploadedDocument.id}`}</h3>
              <p>The file is stored and ready for backend processing.</p>
            </div>
            <div className="success-card__actions">
              <Link to={`/documents/${uploadedDocument.id}`} className="button button-primary">
                Open details
              </Link>
              <Link to="/documents" className="button button-secondary">
                View library
              </Link>
            </div>
          </div>
        ) : null}
      </section>
    </div>
  )
}

export default UploadPage
