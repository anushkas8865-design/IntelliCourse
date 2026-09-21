import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import BackButton from '../components/BackButton'
import { apiRequest } from '../api/api'
import { useAuth } from '../context/AuthContext'
import './CourseDetails.css'

function CourseDetails() {
  const { courseId } = useParams()
  const navigate = useNavigate()
  const { token } = useAuth()

  const [course, setCourse] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    async function loadCourse() {
      setLoading(true)
      setError('')

      try {
        const data = await apiRequest(`/api/course/${courseId}`, {
          method: 'GET',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })

        setCourse(data)
      } catch (error) {
        console.error('Course loading failed:', error)
        setError(error.message || 'Failed to load course.')
      } finally {
        setLoading(false)
      }
    }

    if (courseId && token) {
      loadCourse()
    }
  }, [courseId, token])

  if (loading) {
    return (
      <div className="course-details-page">
        <div className="course-details-container">
          <BackButton />

          <div className="course-details-loading">
            <h2>Loading course...</h2>
            <p>Fetching your course information and lessons.</p>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="course-details-page">
        <div className="course-details-container">
          <BackButton />

          <div className="course-details-error">
            <h2>Unable to load course</h2>
            <p>{error}</p>

            <button
              type="button"
              className="course-details-primary-button"
              onClick={() => window.location.reload()}
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    )
  }

  if (!course) {
    return (
      <div className="course-details-page">
        <div className="course-details-container">
          <BackButton />

          <div className="course-details-error">
            <h2>Course not found</h2>
            <p>The requested course could not be found.</p>
          </div>
        </div>
      </div>
    )
  }

  const lessons = course.lessons || []
  const learningOutcomes = course.learning_outcomes || []

  return (
    <div className="course-details-page">
      <div className="course-details-container">
        <BackButton />

        <section className="course-details-header">
          <div className="course-details-title-section">
            <span className="course-details-label">
              AI GENERATED COURSE
            </span>

            <h1>{course.title || 'Untitled Course'}</h1>

            <p>
              {course.description ||
                'No course description available.'}
            </p>
          </div>

          <div className="course-details-meta">
            <div className="course-meta-item">
              <span className="course-meta-label">
                Difficulty
              </span>
              <strong>
                {course.difficulty || 'Not specified'}
              </strong>
            </div>

            <div className="course-meta-item">
              <span className="course-meta-label">
                Duration
              </span>
              <strong>
                {course.duration || 'Not specified'}
              </strong>
            </div>

            <div className="course-meta-item">
              <span className="course-meta-label">
                Lessons
              </span>
              <strong>{lessons.length}</strong>
            </div>
          </div>
        </section>

        <section className="course-details-section">
          <div className="course-section-heading">
            <h2>Learning Outcomes</h2>
            <p>
              What you will learn by completing this course.
            </p>
          </div>

          {learningOutcomes.length === 0 ? (
            <div className="course-details-empty">
              <p>No learning outcomes available.</p>
            </div>
          ) : (
            <div className="learning-outcomes-list">
              {learningOutcomes.map((outcome, index) => (
                <div
                  className="learning-outcome"
                  key={index}
                >
                  <span className="learning-outcome-icon">
                    ✓
                  </span>

                  <span>{outcome}</span>
                </div>
              ))}
            </div>
          )}
        </section>

        <section className="course-details-section">
          <div className="course-section-heading">
            <h2>Course Lessons</h2>
            <p>
              Follow the lessons in order to complete your
              learning journey.
            </p>
          </div>

          {lessons.length === 0 ? (
            <div className="course-details-empty">
              <h3>No lessons available</h3>
              <p>
                This course does not contain any lessons yet.
              </p>
            </div>
          ) : (
            <div className="course-lessons-list">
              {lessons.map((lesson) => (
                <article
                  className="course-lesson-card"
                  key={lesson.lesson_id}
                  onClick={() =>
                    navigate(`/lesson/${lesson.lesson_id}`)
                  }
                  role="button"
                  tabIndex={0}
                  onKeyDown={(event) => {
                    if (event.key === 'Enter') {
                      navigate(
                        `/lesson/${lesson.lesson_id}`
                      )
                    }
                  }}
                >
                  <div className="course-lesson-number">
                    {lesson.sequence_number}
                  </div>

                  <div className="course-lesson-content">
                    <div className="course-lesson-title-row">
                      <h3>
                        {lesson.title || 'Untitled Lesson'}
                      </h3>

                      <span className="course-lesson-arrow">
                        →
                      </span>
                    </div>

                    <p>
                      {lesson.summary ||
                        'No lesson summary available.'}
                    </p>
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  )
}

export default CourseDetails