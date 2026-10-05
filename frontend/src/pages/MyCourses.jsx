import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import BackButton from '../components/BackButton'
import { apiRequest } from '../api/api'
import { useAuth } from '../context/AuthContext'
import './MyCourses.css'
import './Dashboard.css'

const STATUS_OPTIONS = [
  { value: 'all', label: 'All Courses' },
  { value: 'completed', label: 'Completed Courses' },
  { value: 'in-progress', label: 'In Progress Courses' },
  { value: 'not-started', label: 'Not Started Courses' },
]

function MyCourses() {
  const { user, token } = useAuth()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  const requestedStatus = searchParams.get('status') || 'all'
  const validStatus = STATUS_OPTIONS.some(
    (option) => option.value === requestedStatus
  )
  const selectedStatus = validStatus ? requestedStatus : 'all'

  const [courses, setCourses] = useState([])
  const [progressRecords, setProgressRecords] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    async function loadCourses() {
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
        console.error('My Courses loading failed:', error)
        setError(error.message || 'Failed to load your courses.')
      } finally {
        setLoading(false)
      }
    }

    loadCourses()
  }, [user?.user_id, token])

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

  const filteredCourses = courseData.filter((course) => {
    if (selectedStatus === 'completed') {
      return course.status === 'Completed'
    }

    if (selectedStatus === 'in-progress') {
      return course.status === 'In Progress'
    }

    if (selectedStatus === 'not-started') {
      return course.status === 'Not Started'
    }

    return true
  })

  function handleStatusNavigation(status) {
    if (status === 'all') {
      navigate('/courses')
    } else {
      navigate(`/courses?status=${status}`)
    }
  }

  function getStatusClass(status) {
    if (status === 'Completed') return 'completed'
    if (status === 'In Progress') return 'in-progress'
    return 'not-started'
  }

  const selectedStatusLabel =
    STATUS_OPTIONS.find((option) => option.value === selectedStatus)?.label ||
    'All Courses'

  if (loading) {
    return (
      <div className="my-courses-page">
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

            <button className="nav-item active">
              <span>▣</span>
              My Courses
            </button>

            <div className="sidebar-section-title">Course Status</div>

            {STATUS_OPTIONS.map((option) => (
              <button
                key={option.value}
                className={`nav-item ${
                  selectedStatus === option.value ? 'active' : ''
                }`}
                onClick={() => handleStatusNavigation(option.value)}
              >
                <span>•</span>
                {option.label}
              </button>
            ))}

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

        <main className="my-courses-main">
          <div className="my-courses-container">
            <BackButton />
            <div className="my-courses-loading">
              Loading your courses...
            </div>
          </div>
        </main>
      </div>
    )
  }

  if (error) {
    return (
      <div className="my-courses-page">
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

            <button className="nav-item active">
              <span>▣</span>
              My Courses
            </button>

            <div className="sidebar-section-title">Course Status</div>

            {STATUS_OPTIONS.map((option) => (
              <button
                key={option.value}
                className={`nav-item ${
                  selectedStatus === option.value ? 'active' : ''
                }`}
                onClick={() => handleStatusNavigation(option.value)}
              >
                <span>•</span>
                {option.label}
              </button>
            ))}

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

        <main className="my-courses-main">
          <div className="my-courses-container">
            <BackButton />
            <div className="my-courses-error">
              <p>{error}</p>
            </div>
          </div>
        </main>
      </div>
    )
  }

  return (
    <div className="my-courses-page">
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

          <button className="nav-item active">
            <span>▣</span>
            My Courses
          </button>

          <div className="sidebar-section-title">Course Status</div>

          {STATUS_OPTIONS.map((option) => (
            <button
              key={option.value}
              className={`nav-item ${
                selectedStatus === option.value ? 'active' : ''
              }`}
              onClick={() => handleStatusNavigation(option.value)}
            >
              <span>•</span>
              {option.label}
            </button>
          ))}

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

      <main className="my-courses-main">
        <div className="my-courses-container">
          <BackButton />

          <div className="my-courses-header">
            <div>
              <h1>My Courses</h1>
              <p>View and continue your AI-powered learning courses.</p>
            </div>
          </div>

          <div className="my-courses-summary">
            <span>
              Showing <strong>{filteredCourses.length}</strong>{' '}
              {filteredCourses.length === 1 ? 'course' : 'courses'}
            </span>
            <span>{selectedStatusLabel}</span>
          </div>

          {filteredCourses.length === 0 ? (
            <div className="my-courses-empty">
              <h2>No courses found</h2>
              <p>
                There are no courses matching the selected status.
              </p>
            </div>
          ) : (
            <div className="my-courses-grid">
              {filteredCourses.map((course) => (
                <div
                  className="my-course-card"
                  key={course.course_id}
                  onClick={() => navigate(`/course/${course.course_id}`)}
                >
                  <div className="my-course-card-top">
                    <span
                      className={`course-status-badge ${getStatusClass(
                        course.status
                      )}`}
                    >
                      {course.status}
                    </span>
                  </div>

                  <h2>{course.title}</h2>

                  {course.description && (
                    <p className="my-course-description">
                      {course.description}
                    </p>
                  )}

                  <div className="my-course-progress">
                    <div className="my-course-progress-header">
                      <span>Progress</span>
                      <strong>{course.progress}%</strong>
                    </div>

                    <div className="my-course-progress-bar">
                      <div
                        className="my-course-progress-fill"
                        style={{ width: `${course.progress}%` }}
                      />
                    </div>

                    <span className="my-course-lessons">
                      {course.completedLessons} of {course.totalLessons}{' '}
                      lessons completed
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

export default MyCourses