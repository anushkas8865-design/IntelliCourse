import { useNavigate } from 'react-router-dom'
import BackButton from '../components/BackButton'
import './Dashboard.css'
import './Settings.css'

function Settings() {
  const navigate = useNavigate()

  return (
    <div className="settings-page">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">◆</div>
          <span>AI Course Builder</span>
        </div>

        <nav className="sidebar-nav">
          <button
            className="nav-item"
            onClick={() => navigate('/')}
          >
            <span>⌂</span>
            Dashboard
          </button>

          <button
            className="nav-item"
            onClick={() => navigate('/courses')}
          >
            <span>▣</span>
            My Courses
          </button>

          <button
            className="nav-item"
            onClick={() => navigate('/create-course')}
          >
            <span>✎</span>
            Create Course
          </button>

          <button
            className="nav-item"
            onClick={() => navigate('/revision-quizzes')}
          >
            <span>↻</span>
            Revision Quizzes
          </button>

          <button className="nav-item">
            <span>✦</span>
            AI Assistant
          </button>

          <button
            className="nav-item active"
            onClick={() => navigate('/settings')}
          >
            <span>⚙</span>
            Settings
          </button>
        </nav>

        <div className="sidebar-bottom">
          <div className="sidebar-sparkle">✦</div>
          <strong>Build your future with AI</strong>
          <span>Learn. Create. Grow.</span>
        </div>
      </aside>

      <main className="settings-main">
        <div className="settings-container">
          <BackButton />

          <div className="settings-header">
            <h1>Settings</h1>
            <p>Manage your profile and account information.</p>
          </div>

          <div className="settings-card">
            <section className="settings-section">
              <h2>Profile Information</h2>

              <div className="settings-field">
                <label htmlFor="settings-name">Name</label>
                <input
                  id="settings-name"
                  type="text"
                  placeholder="Your name"
                />
              </div>

              <div className="settings-field">
                <label htmlFor="settings-email">Email</label>
                <input
                  id="settings-email"
                  type="email"
                  placeholder="Your email"
                />
              </div>

              <button
                type="button"
                className="settings-save-button"
              >
                Save Changes
              </button>
            </section>
          </div>
        </div>
      </main>
    </div>
  )
}

export default Settings