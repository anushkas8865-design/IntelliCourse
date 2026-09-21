import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import BackButton from '../components/BackButton'
import { apiRequest } from '../api/api'
import { useAuth } from '../context/AuthContext'
import './MyCourses.css'

const STATUS_OPTIONS = [
  {
    value: 'all',
    label: 'All Courses',
  },
  {
    value: 'completed',
    label: 'Completed Courses',
  },
  {
    value: 'in-progress',
    label: 'In Progress Courses',
  },
  {
    value: 'not-started',
    label: 'Not Started Courses',
  },
]

function MyCourses() {
  const { user, token } = useAuth()
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()

  const requestedStatus = searchParams.get('status') || 'all'

  const validStatus = STATUS_OPTIONS.some(
    (option) => option.value === requestedStatus
  )

  const selectedStatus = validStatus
    ? requestedStatus
    : 'all'

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

  function handleStatusChange(event) {
    const newStatus = event.target.value

    if (newStatus === 'all') {
      setSearchParams({})
    } else {
      setSearchParams({ status: newStatus })
    }
  }

  function getStatusClass(status) {
    if (status === 'Completed') {
      return 'completed'
    }

    if (status === 'In Progress') {
      return 'in-progress'
    }

    return 'not-started'
  }

  const selectedStatusLabel =
    STATUS_OPTIONS.find(
      (option) => option.value === selectedStatus
    )?.label || 'All Courses'

  if (loading) {
    return (
      <div className="my-courses-page">
        <div className="my-courses-container">
          <BackButton />

          <div className="my-courses-loading">
            <h2>Loading your courses...</h2>
            <p>Fetching your courses and learning progress.</p>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="my-courses-page">
        <div className="my-courses-container">
          <BackButton />

          <div className="my-courses-empty">
            <h2>Unable to load courses</h2>
            <p>{error}</p>

            <button
              type="button"
              className="my-course-button"
              onClick={() => window.location.reload()}
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="my-courses-page">
      <div className="my-courses-container">
        <BackButton />

        <div className="my-courses-header">
          <div>
            <h1>My Courses</h1>
            <p>
              View and continue your AI-powered learning courses.
            </p>
          </div>

          <div className="my-courses-filter">
            <label htmlFor="course-status">
              Course Status
            </label>

            <select
              id="course-status"
              value={selectedStatus}
              onChange={handleStatusChange}
            >
              {STATUS_OPTIONS.map((option) => (
                <option
                  key={option.value}
                  value={option.value}
                >
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="my-courses-summary">
          <span>
            Showing <strong>{filteredCourses.length}</strong>{' '}
            {filteredCourses.length === 1
              ? 'course'
              : 'courses'}
          </span>

          <span>{selectedStatusLabel}</span>
        </div>

        {filteredCourses.length === 0 ? (
          <div className="my-courses-empty">
            <h2>No {selectedStatusLabel.toLowerCase()} found</h2>

            <p>
              There are no courses in this category right now.
            </p>
          </div>
        ) : (
          <div className="my-courses-grid">
            {filteredCourses.map((course) => (
              <article
                className="my-course-card"
                key={course.course_id}
              >
                <div className="my-course-card-header">
                  <h2>
                    {course.title || 'Untitled Course'}
                  </h2>

                  <span
                    className={`my-course-status ${getStatusClass(
                      course.status
                    )}`}
                  >
                    {course.status}
                  </span>
                </div>

                <p className="my-course-description">
                  {course.description ||
                    'No course description available.'}
                </p>

                <div className="my-course-meta">
                  <span>
                    Progress: {course.progress}%
                  </span>

                  <span>
                    Lessons: {course.completedLessons} /{' '}
                    {course.totalLessons}
                  </span>
                </div>

                <div className="my-course-progress">
                  <div className="my-course-progress-track">
                    <div
                      className="my-course-progress-fill"
                      style={{
                        width: `${course.progress}%`,
                      }}
                    ></div>
                  </div>
                </div>

                <button
                  type="button"
                  className="my-course-button"
                  onClick={() =>
                    navigate(
                      `/course/${course.course_id}`
                    )
                  }
                >
                  {course.status === 'Not Started'
                    ? 'Start Course'
                    : course.status === 'Completed'
                      ? 'View Course'
                      : 'Continue Course'}
                </button>
              </article>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default MyCourses