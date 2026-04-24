import { Outlet } from 'react-router-dom'
import { useState } from 'react'
import Header from './Header.jsx'
import Sidebar from './Sidebar.jsx'

function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="app-shell">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <div className="app-shell__main">
        <Header onToggleSidebar={() => setSidebarOpen(true)} />
        <main className="app-shell__content">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default Layout
