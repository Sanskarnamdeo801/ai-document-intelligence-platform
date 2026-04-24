import { useRef, useState } from 'react'
import { formatFileSize } from '../utils/formatters.js'

function UploadDropzone({ file, onFileSelect, disabled = false }) {
  const inputRef = useRef(null)
  const [isDragging, setIsDragging] = useState(false)

  const acceptFile = (selectedFile) => {
    if (!selectedFile || disabled) {
      return
    }
    onFileSelect(selectedFile)
  }

  const handleDrop = (event) => {
    event.preventDefault()
    setIsDragging(false)
    acceptFile(event.dataTransfer.files?.[0])
  }

  return (
    <section
      className={`dropzone ${isDragging ? 'dropzone--active' : ''} ${disabled ? 'dropzone--disabled' : ''}`}
      onDragEnter={(event) => {
        event.preventDefault()
        if (!disabled) {
          setIsDragging(true)
        }
      }}
      onDragOver={(event) => event.preventDefault()}
      onDragLeave={(event) => {
        event.preventDefault()
        setIsDragging(false)
      }}
      onDrop={handleDrop}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.docx,.txt"
        hidden
        onChange={(event) => acceptFile(event.target.files?.[0])}
      />
      <div className="dropzone__icon">+</div>
      <h3>Drag documents here</h3>
      <p>Drop PDF, DOCX, or TXT files, or browse your computer.</p>
      <div className="dropzone__actions">
        <button
          type="button"
          className="button button-primary"
          onClick={() => inputRef.current?.click()}
          disabled={disabled}
        >
          Choose file
        </button>
        <span className="dropzone__hint">Supports up to the backend limit configured in `.env`.</span>
      </div>
      {file ? (
        <div className="file-chip">
          <strong>{file.name}</strong>
          <span>
            {file.type || 'Unknown type'} • {formatFileSize(file.size)}
          </span>
        </div>
      ) : null}
    </section>
  )
}

export default UploadDropzone
