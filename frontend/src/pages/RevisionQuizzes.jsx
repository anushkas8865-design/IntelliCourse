import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiRequest } from '../api/api'
import { useAuth } from '../context/AuthContext'
import './RevisionQuizzes.css'

function RevisionQuizzes() {
  const navigate = useNavigate()
  const { token } = useAuth()

  const [revisionConcepts, setRevisionConcepts] = useState([])
  const [revisionHistory, setRevisionHistory] = useState([])
  const [courseTitles, setCourseTitles] = useState({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [generatingCourseId, setGeneratingCourseId] = useState('')
  const [selectedAttemptId, setSelectedAttemptId] = useState('')
  const [attemptDetails, setAttemptDetails] = useState(null)
  const [attemptLoading, setAttemptLoading] = useState(false)

  const [activeSection, setActiveSection] = useState('new')

  useEffect(() => {
    async function loadRevisionData() {
      if (!token) {
        setLoading(false)
        return
      }

      setLoading(true)
      setError('')

      try {
        const [
          conceptData,
          historyData,
          courseData,
        ] = await Promise.all([
          apiRequest('/api/progress/revision', {
            method: 'GET',
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }),

          apiRequest('/api/quiz/revision/history', {
            method: 'GET',
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }),

          apiRequest('/api/course/all', {
            method: 'GET',
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }),
        ])

        setRevisionConcepts(
          conceptData.concepts || []
        )

        setRevisionHistory(
          historyData.history || []
        )

        const titles = {}

        ;(courseData.courses || []).forEach((course) => {
          const courseId =
            course.course_id || course.id

          const courseTitle =
            course.title ||
            course.course_title ||
            course.name

          if (courseId && courseTitle) {
            titles[courseId] = courseTitle
          }
        })

        setCourseTitles(titles)
      } catch (error) {
        console.error(
          'Revision quiz data loading failed:',
          error
        )

        setError(
          error.message ||
            'Unable to load revision quizzes.'
        )
      } finally {
        setLoading(false)
      }
    }

    loadRevisionData()
  }, [token])

  function groupConceptsByCourse() {
    const groupedCourses = {}

    revisionConcepts.forEach((concept) => {
      if (!concept.course_id) {
        return
      }

      if (!groupedCourses[concept.course_id]) {
        groupedCourses[concept.course_id] = {
          course_id: concept.course_id,
          course_title:
            courseTitles[concept.course_id] ||
            concept.course_title ||
            concept.course_name ||
            concept.course_id,
          concepts: [],
        }
      }

      groupedCourses[
        concept.course_id
      ].concepts.push(concept)
    })

    return Object.values(groupedCourses)
  }

  async function startRevisionQuiz(courseId) {
    if (!token || !courseId) {
      return
    }

    setGeneratingCourseId(courseId)
    setError('')

    try {
      const data = await apiRequest(
        '/api/quiz/revision/generate',
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            course_id: courseId,
            number_of_questions: 5,
          }),
        }
      )

      if (
        !data.questions ||
        data.questions.length === 0
      ) {
        setError(
          data.message ||
            'No revision quiz questions are available.'
        )
        return
      }

      navigate('/revision-quiz', {
        state: {
          quiz: data,
        },
      })
    } catch (error) {
      console.error(
        'Revision quiz generation failed:',
        error
      )

      setError(
        error.message ||
          'Unable to generate revision quiz.'
      )
    } finally {
      setGeneratingCourseId('')
    }
  }

  async function viewAttempt(attemptId) {
    if (!token || !attemptId) {
      return
    }

    setSelectedAttemptId(attemptId)
    setAttemptDetails(null)
    setAttemptLoading(true)
    setError('')

    try {
      const data = await apiRequest(
        `/api/quiz/revision/history/${attemptId}`,
        {
          method: 'GET',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )

      setAttemptDetails(data)

      setTimeout(() => {
        const section = document.getElementById(
          'revision-attempt-review'
        )

        if (section) {
          section.scrollIntoView({
            behavior: 'smooth',
            block: 'start',
          })
        }
      }, 50)
    } catch (error) {
      console.error(
        'Revision quiz attempt loading failed:',
        error
      )

      setError(
        error.message ||
          'Unable to load revision quiz attempt.'
      )

      setSelectedAttemptId('')
    } finally {
      setAttemptLoading(false)
    }
  }

  function closeAttemptDetails() {
    setSelectedAttemptId('')
    setAttemptDetails(null)
  }

  function formatAttemptDate(dateValue) {
    if (!dateValue) {
      return 'Date unavailable'
    }

    const date = new Date(dateValue)

    if (Number.isNaN(date.getTime())) {
      return 'Date unavailable'
    }

    return date.toLocaleString()
  }

  const groupedCourses = groupConceptsByCourse()

  return (
    <div className="revision-page">

      {/* =================================================
          SIDEBAR
      ================================================== */}

      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">
            ◆
          </div>

          <span>
            AI Course Builder
          </span>
        </div>

        <nav className="sidebar-nav">

          <button
            type="button"
            className="nav-item"
            onClick={() => navigate('/')}
          >
            <span>⌂</span>
            Dashboard
          </button>

          <button
            type="button"
            className={`nav-item ${
              activeSection === 'new'
                ? 'active'
                : ''
            }`}
            onClick={() => {
              setActiveSection('new')
              closeAttemptDetails()
            }}
          >
            <span>↻</span>
            New Revision Quizzes
          </button>

          <button
            type="button"
            className={`nav-item ${
              activeSection === 'previous'
                ? 'active'
                : ''
            }`}
            onClick={() => {
              setActiveSection('previous')
              closeAttemptDetails()
            }}
          >
            <span>◷</span>
            Previous Revision Quizzes
          </button>

        </nav>
      </aside>

      {/* =================================================
          MAIN CONTENT
      ================================================== */}

      <main className="revision-main">

        <section className="revision-header">
          <span className="revision-label">
            ADAPTIVE REVISION
          </span>

          <h1>
            Revision Quizzes
          </h1>

          <p>
            Reinforce concepts that are due for revision
            based on your learning progress.
          </p>
        </section>

        {error && (
          <div className="revision-error">
            <h3>
              Unable to load revision quizzes
            </h3>

            <p>
              {error}
            </p>
          </div>
        )}

        {/* =================================================
            NEW REVISION QUIZZES
        ================================================== */}

        {activeSection === 'new' && (
          <section
            className="revision-card"
          >
            <div className="revision-section-heading">
              <h2>
                New Revision Quizzes
              </h2>

              <p>
                Start one revision quiz for each course
                containing concepts that are due.
              </p>
            </div>

            {loading ? (
              <div className="revision-empty">
                <h3>
                  Checking for revision quizzes...
                </h3>

                <p>
                  Checking your learning progress for
                  concepts that are due for revision.
                </p>
              </div>
            ) : groupedCourses.length === 0 ? (
              <div className="revision-empty">
                <h3>
                  No revision quizzes available
                </h3>

                <p>
                  Complete lessons and continue learning.
                  Revision quizzes will appear here when
                  concepts become due.
                </p>
              </div>
            ) : (
              <div className="revision-list">
                {groupedCourses.map((course) => (
                  <div
                    key={course.course_id}
                    className="revision-item"
                  >
                    <div className="revision-item-content">
                      <span className="revision-item-label">
                        REVISION QUIZ
                      </span>

                      <h3>
                        {course.course_title}
                      </h3>

                      <p>
                        {course.concepts.length}{' '}
                        concept
                        {course.concepts.length !== 1
                          ? 's'
                          : ''}{' '}
                        are due for revision.
                      </p>
                    </div>

                    <button
                      type="button"
                      className="lesson-primary-button"
                      onClick={() =>
                        startRevisionQuiz(
                          course.course_id
                        )
                      }
                      disabled={
                        generatingCourseId ===
                        course.course_id
                      }
                    >
                      {generatingCourseId ===
                      course.course_id
                        ? 'Generating Quiz...'
                        : 'Start Quiz'}
                    </button>
                  </div>
                ))}
              </div>
            )}
          </section>
        )}

        {/* =================================================
            PREVIOUS REVISION QUIZZES
        ================================================== */}

        {activeSection === 'previous' && (
          <>
            {!selectedAttemptId && (
              <section
                className="revision-card"
              >
                <div className="revision-section-heading">
                  <h2>
                    Previous Revision Quizzes
                  </h2>

                  <p>
                    Review your completed revision quiz
                    attempts and see the answers you selected.
                  </p>
                </div>

                {loading ? (
                  <div className="revision-empty">
                    <h3>
                      Loading previous revision quizzes...
                    </h3>
                  </div>
                ) : revisionHistory.length === 0 ? (
                  <div className="revision-empty">
                    <h3>
                      No previous revision quizzes
                    </h3>

                    <p>
                      Completed revision quizzes will appear
                      here after you submit one.
                    </p>
                  </div>
                ) : (
                  <div className="revision-list">
                    {revisionHistory.map((attempt) => (
                      <div
                        key={attempt.attempt_id}
                        className="revision-item"
                      >
                        <div className="revision-item-content">
                          <span className="revision-item-label">
                            COMPLETED REVISION QUIZ
                          </span>

                          <h3>
                            {attempt.course_title}
                          </h3>

                          <p>
                            Score:{' '}
                            <strong>
                              {attempt.score}%
                            </strong>
                          </p>

                          <p>
                            {attempt.correct_answers}{' '}
                            correct out of{' '}
                            {attempt.total_questions}
                            {' '}questions
                          </p>

                          <span className="revision-attempt-date">
                            {formatAttemptDate(
                              attempt.attempted_at
                            )}
                          </span>
                        </div>

                        <button
                          type="button"
                          className="lesson-primary-button"
                          onClick={() =>
                            viewAttempt(
                              attempt.attempt_id
                            )
                          }
                        >
                          View Attempt
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </section>
            )}

            {/* =================================================
                DETAILED ATTEMPT REVIEW
            ================================================== */}

            {selectedAttemptId && (
              <section
                id="revision-attempt-review"
                className="revision-card"
              >
                <div className="revision-section-heading">
                  <h2>
                    Detailed Review
                  </h2>

                  {attemptDetails && (
                    <p>
                      {attemptDetails.course_title}
                      {' — '}
                      {attemptDetails.score}%
                    </p>
                  )}
                </div>

                {attemptLoading ? (
                  <div className="revision-empty">
                    <h3>
                      Loading attempt...
                    </h3>

                    <p>
                      Retrieving your saved answers.
                    </p>
                  </div>
                ) : attemptDetails ? (
                  <>
                    <div className="revision-result-summary">
                      <h3>
                        {attemptDetails.score}%
                      </h3>

                      <p>
                        {attemptDetails.correct_answers}{' '}
                        correct out of{' '}
                        {attemptDetails.total_questions}
                        {' '}questions
                      </p>

                      <p>
                        Attempted:{' '}
                        {formatAttemptDate(
                          attemptDetails.attempted_at
                        )}
                      </p>
                    </div>

                    <div className="revision-review-list">
                      {attemptDetails.results.map(
                        (questionResult, index) => (
                          <div
                            key={
                              questionResult.quiz_id
                            }
                            className="revision-review-question"
                          >
                            <h3>
                              {index + 1}.{' '}
                              {questionResult.question}
                            </h3>

                            <p>
                              Concept:{' '}
                              <strong>
                                {
                                  questionResult.concept_name
                                }
                              </strong>
                            </p>

                            <p>
                              Your answer:{' '}
                              <strong>
                                {
                                  questionResult.selected_answer
                                }
                              </strong>
                            </p>

                            <p>
                              Correct answer:{' '}
                              <strong>
                                {
                                  questionResult.correct_answer
                                }
                              </strong>
                            </p>

                            <p
                              className={
                                questionResult.correct
                                  ? 'revision-result-correct'
                                  : 'revision-result-incorrect'
                              }
                            >
                              <strong>
                                {questionResult.correct
                                  ? 'Result: Correct'
                                  : 'Result: Incorrect'}
                              </strong>
                            </p>

                            <p>
                              {questionResult.explanation}
                            </p>
                          </div>
                        )
                      )}
                    </div>

                    <div className="revision-review-actions">
                      <button
                        type="button"
                        className="lesson-primary-button"
                        onClick={
                          closeAttemptDetails
                        }
                      >
                        Back to Previous Quizzes
                      </button>
                    </div>
                  </>
                ) : null}
              </section>
            )}
          </>
        )}

      </main>
    </div>
  )
}

export default RevisionQuizzes