import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import BackButton from '../components/BackButton'
import { apiRequest } from '../api/api'
import { useAuth } from '../context/AuthContext'
import './Lesson.css'

function Lesson() {
  const { lessonId } = useParams()
  const navigate = useNavigate()
  const { token, user } = useAuth()

  const [lesson, setLesson] = useState(null)
  const [videos, setVideos] = useState([])
  const [challenge, setChallenge] = useState(null)

  const [progress, setProgress] = useState(null)
  const [lessonCompleted, setLessonCompleted] = useState(false)
  const [completeLoading, setCompleteLoading] = useState(false)
  const [completeError, setCompleteError] = useState('')

  const [loading, setLoading] = useState(true)
  const [challengeLoading, setChallengeLoading] = useState(false)

  const [error, setError] = useState('')
  const [challengeError, setChallengeError] = useState('')

  useEffect(() => {
    async function loadLesson() {
      if (!token || !user || !lessonId) {
        setLoading(false)
        return
      }

      setLoading(true)
      setError('')

      try {
        const [lessonData, videoData, progressData] = await Promise.all([
          apiRequest(`/api/lesson/${lessonId}`, {
            method: 'GET',
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }),

          apiRequest(`/api/video/${lessonId}`, {
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

        setLesson(lessonData)
        setVideos(videoData.videos || [])

        const courseProgress = (progressData.progress || []).find(
          (item) => item.course_id === lessonData.course_id
        )

        setProgress(courseProgress || null)

        if (
          courseProgress &&
          courseProgress.completed_lessons >= lessonData.sequence_number
        ) {
          setLessonCompleted(true)
        } else {
          setLessonCompleted(false)
        }
      } catch (error) {
        console.error('Lesson loading failed:', error)
        setError(error.message || 'Failed to load lesson.')
      } finally {
        setLoading(false)
      }
    }

    loadLesson()
  }, [lessonId, token, user])

  async function generateCodingChallenge() {
    if (!token || !lessonId) {
      return
    }

    setChallengeLoading(true)
    setChallengeError('')
    setChallenge(null)

    try {
      const data = await apiRequest('/api/challenge/generate', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          lesson_id: lessonId,
        }),
      })

      setChallenge(data)
    } catch (error) {
      console.error('Coding challenge generation failed:', error)
      setChallengeError(
        error.message || 'Unable to generate coding challenge.'
      )
    } finally {
      setChallengeLoading(false)
    }
  }

  async function markLessonComplete() {
    if (!token || !user || !lesson) {
      return
    }

    if (lessonCompleted) {
      return
    }

    setCompleteLoading(true)
    setCompleteError('')

    try {
      const currentCompletedLessons =
        progress?.completed_lessons || 0

      const nextCompletedLessons = currentCompletedLessons + 1

      const data = await apiRequest('/api/progress/update', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          course_id: lesson.course_id,
          completed_lessons: nextCompletedLessons,
          quiz_score: progress?.quiz_score || 0,
        }),
      })

      setProgress({
        ...progress,
        completed_lessons: data.completed_lessons,
        total_lessons: data.total_lessons,
        quiz_score: data.quiz_score,
        progress_percentage: data.progress_percentage,
      })

      setLessonCompleted(true)
    } catch (error) {
      console.error('Lesson completion failed:', error)

      setCompleteError(
        error.message || 'Unable to mark lesson as complete.'
      )
    } finally {
      setCompleteLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="lesson-page">
        <div className="lesson-container">
          <BackButton />

          <div className="lesson-loading">
            <h2>Loading lesson...</h2>
            <p>Fetching your lesson content and learning resources.</p>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="lesson-page">
        <div className="lesson-container">
          <BackButton />

          <div className="lesson-error">
            <h2>Unable to load lesson</h2>
            <p>{error}</p>

            <button
              type="button"
              className="lesson-primary-button"
              onClick={() => window.location.reload()}
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    )
  }

  if (!lesson) {
    return (
      <div className="lesson-page">
        <div className="lesson-container">
          <BackButton />

          <div className="lesson-error">
            <h2>Lesson not found</h2>
            <p>The requested lesson could not be found.</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="lesson-page">
      <div className="lesson-container">
        <BackButton />

        <section className="lesson-header">
          <span className="lesson-label">
            LESSON {lesson.sequence_number}
          </span>

          <h1>{lesson.title || 'Untitled Lesson'}</h1>

          <p>
            {lesson.summary || 'No lesson summary available.'}
          </p>
        </section>

        <section className="lesson-card">
          <div className="lesson-section-heading">
            <h2>Lesson Content</h2>
            <p>Study the lesson material below.</p>
          </div>

          <div className="lesson-content">
            {lesson.content ? (
              lesson.content.split('\n').map((line, index) => (
                <p key={index}>
                  {line || '\u00A0'}
                </p>
              ))
            ) : (
              <p>No lesson content is available.</p>
            )}
          </div>
        </section>

        <section className="lesson-card">
          <div className="lesson-section-heading">
            <h2>Recommended Videos</h2>
            <p>
              Additional YouTube resources related to this lesson.
            </p>
          </div>

          {videos.length === 0 ? (
            <div className="lesson-empty">
              <p>No YouTube videos are available for this lesson.</p>
            </div>
          ) : (
            <div className="lesson-videos">
              {videos.map((video) => (
                <a
                  key={video.video_id}
                  href={video.youtube_url}
                  target="_blank"
                  rel="noreferrer"
                  className="lesson-video-card"
                >
                  <div className="lesson-video-icon">
                    ▶
                  </div>

                  <div className="lesson-video-info">
                    <h3>{video.title || 'YouTube Lesson Video'}</h3>
                    <span>Watch on YouTube →</span>
                  </div>
                </a>
              ))}
            </div>
          )}
        </section>

        <section className="lesson-card">
          <div className="lesson-section-heading">
            <h2>Coding Challenge</h2>
            <p>
              Practice your programming skills with an AI-generated
              challenge.
            </p>
          </div>

          {!challenge ? (
            <div className="challenge-start">
              <p>
                Coding challenges are available for programming
                courses.
              </p>

              <button
                type="button"
                className="lesson-primary-button"
                onClick={generateCodingChallenge}
                disabled={challengeLoading}
              >
                {challengeLoading
                  ? 'Generating Challenge...'
                  : 'Generate Coding Challenge'}
              </button>

              {challengeError && (
                <p className="challenge-error">
                  {challengeError}
                </p>
              )}
            </div>
          ) : (
            <div className="coding-challenge">
              <div className="challenge-header">
                <div>
                  <span className="challenge-label">
                    CODING CHALLENGE
                  </span>

                  <h3>
                    {challenge.title || 'Coding Challenge'}
                  </h3>
                </div>

                <span className="challenge-difficulty">
                  {challenge.difficulty || 'Not specified'}
                </span>
              </div>

              <div className="challenge-description">
                <p>
                  {challenge.description ||
                    'No challenge description available.'}
                </p>
              </div>
            </div>
          )}
        </section>

        <section className="lesson-completion-card">
          <div>
            <h2>Lesson Complete?</h2>
            <p>
              Mark this lesson as complete after you finish studying
              it.
            </p>
          </div>

          <div>
            <button
              type="button"
              className="lesson-complete-button"
              onClick={markLessonComplete}
              disabled={lessonCompleted || completeLoading}
            >
              {lessonCompleted
                ? '✓ Lesson Completed'
                : completeLoading
                  ? 'Updating Progress...'
                  : 'Mark Lesson Complete'}
            </button>

            {completeError && (
              <p className="challenge-error">
                {completeError}
              </p>
            )}
          </div>
        </section>
      </div>
    </div>
  )
}

export default Lesson