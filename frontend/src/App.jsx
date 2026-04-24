import { Navigate, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout.jsx'
import AskPage from './pages/AskPage.jsx'
import DashboardPage from './pages/DashboardPage.jsx'
import DocumentDetailsPage from './pages/DocumentDetailsPage.jsx'
import DocumentsPage from './pages/DocumentsPage.jsx'
import LogsPage from './pages/LogsPage.jsx'
import SearchPage from './pages/SearchPage.jsx'
import SettingsPage from './pages/SettingsPage.jsx'
import UploadPage from './pages/UploadPage.jsx'

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/upload" element={<UploadPage />} />
        <Route path="/documents" element={<DocumentsPage />} />
        <Route path="/documents/:id" element={<DocumentDetailsPage />} />
        <Route path="/search" element={<SearchPage />} />
        <Route path="/ask" element={<AskPage />} />
        <Route path="/logs" element={<LogsPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
