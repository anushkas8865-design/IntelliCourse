import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import './Dashboard.css'
import { apiRequest } from '../api/api'
import { useAuth } from '../context/AuthContext'

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
  const { user, token, logout } = useAuth()
  const navigate = useNavigate()

  const [courses, setCourses] = useState([])
  const [progressRecords, setProgressRecords] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    async function loadDashboardData() {
      if (!user?.user_id || !token) {
        setLoading(false)
        return
      }

      setLoading(true)
      setError('')

      try {
        const [courseData, progressData] = await Promise.all([
          apiRequest('/api/course/all', {
            method: 'GET',
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }),

          apiRequest(`/api/progress/${user.user_id}`, {
            method: 'GET',
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }),
        ])

        setCourses(courseData.courses || [])
        setProgressRecords(progressData.progress || [])
      } catch (error) {
        console.error('Dashboard data loading failed:', error)
        setError(error.message || 'Failed to load dashboard data.')
      } finally {
        setLoading(false)
      }
    }

    loadDashboardData()
  }, [user?.user_id, token])

  // ---------------------------------------------------------
  // Combine course data with progress data
  // ---------------------------------------------------------

  const courseData = courses.map((course) => {
    const progress = progressRecords.find(
      (record) => record.course_id === course.course_id
    )

    const progressPercentage = progress
      ? Math.round(Number(progress.progress_percentage) || 0)
      : 0

    const completedLessons = progress
      ? progress.completed_lessons || 0
      : 0

    const totalLessons = progress
      ? progress.total_lessons || 0
      : course.total_lessons || 0

    let status = 'Not Started'

    if (progressPercentage >= 100) {
      status = 'Completed'
    } else if (progressPercentage > 0) {
      status = 'In Progress'
    }

    return {
      ...course,
      progress: progressPercentage,
      completedLessons,
      totalLessons,
      status,
    }
  })

  // ---------------------------------------------------------
  // Dashboard statistics
  // ---------------------------------------------------------

  const totalCourses = courseData.length

  const completedCourses = courseData.filter(
    (course) => course.status === 'Completed'
  ).length

  const inProgressCourses = courseData.filter(
    (course) => course.status === 'In Progress'
  ).length

  const notStartedCourses = courseData.filter(
    (course) => course.status === 'Not Started'
  ).length

  const overallProgress =
    totalCourses > 0
      ? Math.round(
          courseData.reduce(
            (total, course) => total + course.progress,
            0
          ) / totalCourses
        )
      : 0

  const currentCourse = courseData.find(
    (course) => course.status === 'In Progress'
  )

  // ---------------------------------------------------------
  // Navigation helpers
  // ---------------------------------------------------------

  function openCourses(status) {
    navigate(`/courses?status=${status}`)
  }

  // ---------------------------------------------------------
  // Loading state
  // ---------------------------------------------------------

  if (loading) {
    return (
      <div className="dashboard-loading">
        <h2>Loading your dashboard...</h2>
        <p>Fetching your courses and learning progress.</p>
      </div>
    )
  }

  // ---------------------------------------------------------
  // Error state
  // ---------------------------------------------------------

  if (error) {
    return (
      <div className="dashboard-loading">
        <h2>Unable to load dashboard</h2>
        <p>{error}</p>

        <button
          type="button"
          className="primary-button"
          onClick={() => window.location.reload()}
        >
          Try Again
        </button>
      </div>
    )
  }

  return (
    <div className="dashboard">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">◆</div>
          <span>AI Course Builder</span>
        </div>

        <nav className="sidebar-nav">
          <button
            type="button"
            className="nav-item active"
            onClick={() => navigate('/')}
          >
            <span>⌂</span>
            Dashboard
          </button>

          <button
            type="button"
            className="nav-item"
            onClick={() => navigate('/courses')}
          >
            <span>▣</span>
            My Courses
          </button>

          <button
            type="button"
            className="nav-item"
            onClick={() => navigate('/create-course')}
          >
            <span>✎</span>
            Create Course
          </button>

          <button
            type="button"
            className="nav-item"
          >
            <span>✦</span>
            AI Assistant
          </button>

          <button
            type="button"
            className="nav-item"
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

      <main className="dashboard-main">
        <header className="top-header">
          <div></div>

          <div className="profile">
            <button
              className="notification-button"
              aria-label="Notifications"
            >
              ♧
            </button>

            <div className="profile-avatar">
              {user?.name
                ? user.name
                    .split(' ')
                    .map((part) => part[0])
                    .join('')
                    .slice(0, 2)
                    .toUpperCase()
                : 'U'}
            </div>

            <span className="profile-name">
              {user?.name || 'User'}
            </span>

            <button
              type="button"
              className="profile-arrow"
              aria-label="Open Settings"
              onClick={() => navigate('/settings')}
            >
              ⌄
            </button>

            <button
              type="button"
              onClick={logout}
              className="logout-button"
            >
              Logout
            </button>
          </div>
        </header>

        <div className="dashboard-content">

          {/* =====================================================
              WELCOME
          ===================================================== */}

          <section className="welcome-card">
            <div>
              <p className="welcome-label">
                WELCOME BACK, {user?.name?.toUpperCase() || 'USER'}!
              </p>

              <h1>Continue your learning journey</h1>

              <p className="welcome-description">
                Build your skills with AI-powered courses, tailored to
                your learning goals.
              </p>

              <button
                type="button"
                className="primary-button"
                onClick={() => navigate('/courses')}
              >
                Browse Courses
                <span>→</span>
              </button>
            </div>
          </section>

          {/* =====================================================
              COURSES + PROGRESS
          ===================================================== */}

          <section className="learning-section">
            <div className="courses-area">

              <div className="section-heading">
                <div>
                  <h2>My Courses</h2>
                  <p>
                    Your enrolled courses and learning progress
                  </p>
                </div>

                <button
                  type="button"
                  className="view-all-button"
                  onClick={() => openCourses('all')}
                >
                  View all →
                </button>
              </div>

              <div className="course-grid">

                {courseData.length === 0 ? (
                  <article className="course-card">
                    <div className="course-card-title">
                      <h3>No courses yet</h3>
                    </div>

                    <p className="course-description">
                      You haven't created any courses yet. Start building
                      your first AI-powered course.
                    </p>

                    <button
                      type="button"
                      className="primary-button"
                      onClick={() => navigate('/create-course')}
                    >
                      Create Course
                    </button>
                  </article>
                ) : (
                  courseData.map((course) => (
                    <article
                      className="course-card"
                      key={course.course_id}
                      onClick={() =>
                        navigate(`/course/${course.course_id}`)
                      }
                      role="button"
                      tabIndex={0}
                      onKeyDown={(event) => {
                        if (event.key === 'Enter') {
                          navigate(`/course/${course.course_id}`)
                        }
                      }}
                    >
                      <div className="course-card-title">
                        <h3>
                          {course.title || 'Untitled Course'}
                        </h3>

                        <span
                          className={`status ${
                            course.status === 'In Progress'
                              ? 'in-progress'
                              : course.status === 'Completed'
                                ? 'completed'
                                : 'not-started'
                          }`}
                        >
                          {course.status}
                        </span>
                      </div>

                      <p className="course-description">
                        {course.description ||
                          'No course description available.'}
                      </p>

                      <ProgressBar
                        progress={course.progress}
                      />

                      <div className="lesson-count">
                        <span>▣</span>

                        {course.completedLessons} /{' '}
                        {course.totalLessons} lessons
                      </div>
                    </article>
                  ))
                )}

              </div>
            </div>

            {/* =================================================
                PROGRESS OVERVIEW
            ================================================= */}

            <aside className="progress-card">

              <div className="progress-card-heading">
                <div className="progress-heading-icon">↗</div>
                <h2>Progress Overview</h2>
              </div>

              <div
                className="progress-circle"
                style={{
                  background: `conic-gradient(
                    #6845f5 0deg ${overallProgress * 3.6}deg,
                    #e5eaf2 ${overallProgress * 3.6}deg 360deg
                  )`,
                }}
              >
                <div>
                  <strong>{overallProgress}%</strong>
                  <span>Overall Progress</span>
                </div>
              </div>

              <button
                type="button"
                className="progress-stat progress-stat-button"
                onClick={() => openCourses('completed')}
              >
                <span className="stat-icon completed">✓</span>
                <span>Completed Courses</span>
                <strong>{completedCourses}</strong>
              </button>

              <button
                type="button"
                className="progress-stat progress-stat-button"
                onClick={() => openCourses('in-progress')}
              >
                <span className="stat-icon current">◷</span>
                <span>In Progress Courses</span>
                <strong>{inProgressCourses}</strong>
              </button>

              <button
                type="button"
                className="progress-stat progress-stat-button"
                onClick={() => openCourses('not-started')}
              >
                <span className="stat-icon not-started">○</span>
                <span>Not Started Courses</span>
                <strong>{notStartedCourses}</strong>
              </button>

              <button
                type="button"
                className="progress-stat progress-stat-button"
                onClick={() => openCourses('all')}
              >
                <span className="stat-icon total">▣</span>
                <span>Total Courses</span>
                <strong>{totalCourses}</strong>
              </button>

            </aside>
          </section>

          {/* =====================================================
              CONTINUE LEARNING
          ===================================================== */}

          <section className="continue-section">

            <div className="section-heading continue-heading">
              <div>
                <h2>Continue Learning</h2>
                <p>Pick up where you left off</p>
              </div>
            </div>

            {currentCourse ? (
              <div className="continue-card">

                <div className="continue-info">

                  <h3>{currentCourse.title}</h3>

                  <p>
                    {currentCourse.completedLessons > 0
                      ? `Lesson ${currentCourse.completedLessons + 1}`
                      : 'Start your first lesson'}
                  </p>

                  <div className="continue-progress">

                    <div className="progress-track">
                      <div
                        className="progress-fill"
                        style={{
                          width: `${currentCourse.progress}%`,
                        }}
                      ></div>
                    </div>

                    <span>{currentCourse.progress}%</span>

                  </div>

                </div>

                <button
                  type="button"
                  className="continue-button"
                  onClick={() =>
                    navigate(
                      `/course/${currentCourse.course_id}`
                    )
                  }
                >
                  <span>▶</span>
                  Continue
                </button>

              </div>
            ) : (
              <div className="continue-card">

                <div className="continue-info">
                  <h3>No course in progress</h3>
                  <p>
                    Start a course to continue your learning journey.
                  </p>
                </div>

                <button
                  type="button"
                  className="continue-button"
                  onClick={() => openCourses('all')}
                >
                  Browse Courses
                </button>

              </div>
            )}

          </section>

        </div>
      </main>
    </div>
  )
}

export default Dashboard