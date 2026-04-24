import { NavLink } from 'react-router-dom'

const navigation = [
  { to: '/', label: 'Dashboard', short: 'DB' },
  { to: '/upload', label: 'Upload Document', short: 'UP' },
  { to: '/documents', label: 'Documents', short: 'DO' },
  { to: '/search', label: 'Semantic Search', short: 'SE' },
  { to: '/ask', label: 'Ask AI', short: 'AI' },
  { to: '/logs', label: 'Pipeline Logs', short: 'LG' },
  { to: '/settings', label: 'Settings', short: 'ST' },
]

function Sidebar({ isOpen, onClose }) {
  return (
    <>
      <aside className={`sidebar ${isOpen ? 'sidebar--open' : ''}`}>
        <div className="sidebar__brand">
          <div className="sidebar__logo">DI</div>
          <div>
            <strong>Doc Intelligence</strong>
            <span>AI operations console</span>
          </div>
        </div>
        <nav className="sidebar__nav">
          {navigation.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => `sidebar__link ${isActive ? 'sidebar__link--active' : ''}`}
              onClick={onClose}
            >
              <span className="sidebar__link-icon">{item.short}</span>
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
        <div className="sidebar__footer">
          <p>Document processing, retrieval, and AI-assisted review in one workspace.</p>
        </div>
      </aside>
      {isOpen ? <button type="button" className="sidebar-backdrop" onClick={onClose} aria-label="Close navigation" /> : null}
    </>
  )
}

export default Sidebar
