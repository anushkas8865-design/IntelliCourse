import BackButton from '../components/BackButton'
import './Settings.css'

function Settings() {
  return (
    <div className="settings-page">
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
    </div>
  )
}

export default Settings