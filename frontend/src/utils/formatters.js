export const formatDateTime = (value) => {
  if (!value) {
    return 'Not available'
  }

  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return 'Not available'
  }

  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  }).format(date)
}

export const formatFileSize = (bytes) => {
  if (bytes == null || Number.isNaN(Number(bytes))) {
    return 'Unknown'
  }

  const units = ['B', 'KB', 'MB', 'GB']
  let value = Number(bytes)
  let unitIndex = 0

  while (value >= 1024 && unitIndex < units.length - 1) {
    value /= 1024
    unitIndex += 1
  }

  return `${value.toFixed(value >= 10 || unitIndex === 0 ? 0 : 1)} ${units[unitIndex]}`
}

export const formatStatusLabel = (status) => {
  if (!status) {
    return 'Unknown'
  }
  return status
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (character) => character.toUpperCase())
}

export const truncateText = (value, maxLength = 180) => {
  if (!value) {
    return ''
  }
  if (value.length <= maxLength) {
    return value
  }
  return `${value.slice(0, maxLength).trim()}...`
}
