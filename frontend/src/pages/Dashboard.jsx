import './Dashboard.css'

const courses = [
  {
    title: 'React Fundamentals',
    description: 'Learn the basics of React and build modern user interfaces.',
    status: 'In Progress',
    progress: 60,
    completedLessons: 6,
    totalLessons: 10,
  },
  {
    title: 'Python for AI',
    description: 'Master Python for machine learning and AI applications.',
    status: 'Not Started',
    progress: 0,
    completedLessons: 0,
    totalLessons: 8,
  },
  {
    title: 'Node.js Backend',
    description: 'Build scalable backend applications with Node.js.',
    status: 'Not Started',
    progress: 0,
    completedLessons: 0,
    totalLessons: 12,
  },
  {
    title: 'UI/UX Design',
    description: 'Create beautiful and user-friendly interfaces.',
    status: 'Not Started',
    progress: 0,
    completedLessons: 0,
    totalLessons: 10,
  },
]

function ProgressBar({ progress }) {
  return (
    <div className="progress-row">
      <div className="progress-track">
        <div
          className="progress-fill"
          style={{ width: `${progress}%` }}
        ></div>
      </div>

      <span className="progress-value">{progress}%</span>
    </div>
  )
}

function Dashboard() {
  const overallProgress = 15

  return (
    <div className="dashboard">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">◆</div>
          <span>AI Course Builder</span>
        </div>

        <nav className="sidebar-nav">
          <button className="nav-item active">
            <span>⌂</span>
            Dashboard
          </button>

          <button className="nav-item">
            <span>▣</span>
            My Courses
          </button>

          <button className="nav-item">
            <span>✎</span>
            Create Course
          </button>

          <button className="nav-item">
            <span>✦</span>
            AI Assistant
          </button>

          <button className="nav-item">
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

      {/* Main Content */}
      <main className="dashboard-main">
        {/* Header */}
        <header className="top-header">
          <div></div>

          <div className="profile">
            <button
              className="notification-button"
              aria-label="Notifications"
            >
              ♧
            </button>

            <div className="profile-avatar">JD</div>

            <span className="profile-name">John Doe</span>
            <span className="profile-arrow">⌄</span>
          </div>
        </header>

        <div className="dashboard-content">
          {/* Welcome Section */}
          <section className="welcome-card">
            <div>
              <p className="welcome-label">WELCOME BACK, JOHN!</p>

              <h1>Continue your learning journey</h1>

              <p className="welcome-description">
                Build your skills with AI-powered courses, tailored to your
                learning goals.
              </p>

              <button className="primary-button">
                Browse Courses
                <span>→</span>
              </button>
            </div>
          </section>

          {/* Learning Section */}
          <section className="learning-section">
            <div className="courses-area">
              <div className="section-heading">
                <div>
                  <h2>My Courses</h2>
                  <p>Your enrolled courses and learning progress</p>
                </div>

                <button className="view-all-button">
                  View all →
                </button>
              </div>

              <div className="course-grid">
                {courses.map((course) => (
                  <article className="course-card" key={course.title}>
                    <div className="course-card-title">
                      <h3>{course.title}</h3>

                      <span
                        className={`status ${
                          course.status === 'In Progress'
                            ? 'in-progress'
                            : 'not-started'
                        }`}
                      >
                        {course.status}
                      </span>
                    </div>

                    <p className="course-description">
                      {course.description}
                    </p>

                    <ProgressBar progress={course.progress} />

                    <div className="lesson-count">
                      <span>▣</span>
                      {course.completedLessons} / {course.totalLessons} lessons
                    </div>
                  </article>
                ))}
              </div>
            </div>

            {/* Progress Overview */}
            <aside className="progress-card">
              <div className="progress-card-heading">
                <div className="progress-heading-icon">↗</div>
                <h2>Progress Overview</h2>
              </div>

              <div className="progress-circle">
                <div>
                  <strong>{overallProgress}%</strong>
                  <span>Overall Progress</span>
                </div>
              </div>

              <div className="progress-stat">
                <span className="stat-icon completed">✓</span>
                <span>Completed Courses</span>
                <strong>0</strong>
              </div>

              <div className="progress-stat">
                <span className="stat-icon current">◷</span>
                <span>In Progress Courses</span>
                <strong>1</strong>
              </div>

              <div className="progress-stat">
                <span className="stat-icon not-started">○</span>
                <span>Not Started Courses</span>
                <strong>3</strong>
              </div>

              <div className="progress-stat">
                <span className="stat-icon total">▣</span>
                <span>Total Courses</span>
                <strong>4</strong>
              </div>
            </aside>
          </section>

          {/* Continue Learning */}
          <section className="continue-section">
            <div className="section-heading continue-heading">
              <div>
                <h2>Continue Learning</h2>
                <p>Pick up where you left off</p>
              </div>
            </div>

            <div className="continue-card">
              <div className="continue-info">
                <h3>React Fundamentals</h3>
                <p>Lesson 6: React Components</p>

                <div className="continue-progress">
                  <div className="progress-track">
                    <div
                      className="progress-fill"
                      style={{ width: '60%' }}
                    ></div>
                  </div>

                  <span>60%</span>
                </div>
              </div>

              <button className="continue-button">
                <span>▶</span>
                Continue
              </button>
            </div>
          </section>
        </div>
      </main>
    </div>
  )
}

export default Dashboard