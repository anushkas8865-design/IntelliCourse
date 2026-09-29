import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import BackButton from '../components/BackButton'
import { apiRequest } from '../api/api'
import { useAuth } from '../context/AuthContext'
import './RevisionQuizzes.css'

function RevisionQuizzes() {
  const navigate = useNavigate()
  const { token } = useAuth()

  const [revisionConcepts, setRevisionConcepts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [generatingCourseId, setGeneratingCourseId] = useState('')

  useEffect(() => {
    async function loadRevisionConcepts() {
      if (!token) {
        setLoading(false)
        return
      }

      setLoading(true)
      setError('')

      try {
        const data = await apiRequest('/api/progress/revision', {
          method: 'GET',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })

        setRevisionConcepts(data.concepts || [])
      } catch (error) {
        console.error('Revision concepts loading failed:', error)
        setError(
          error.message || 'Unable to load revision concepts.'
        )
      } finally {
        setLoading(false)
      }
    }

    loadRevisionConcepts()
  }, [token])

  async function startRevisionQuiz(courseId) {
    if (!token || !courseId) {
      return
    }

    setGeneratingCourseId(courseId)
    setError('')

    try {
      const data = await apiRequest('/api/quiz/revision/generate', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          course_id: courseId,
          number_of_questions: 5,
        }),
      })

      if (!data.questions || data.questions.length === 0) {
        setError(
          data.message || 'No revision quiz questions are available.'
        )
        return
      }

      navigate('/revision-quiz', {
        state: {
          quiz: data,
        },
      })
    } catch (error) {
      console.error('Revision quiz generation failed:', error)
      setError(
        error.message || 'Unable to generate revision quiz.'
      )
    } finally {
      setGeneratingCourseId('')
    }
  }

  return (
    <div className="revision-page">
      <div className="revision-container">
        <BackButton />

        <section className="revision-header">
          <span className="revision-label">ADAPTIVE REVISION</span>

          <h1>Revision Quizzes</h1>

          <p>
            Reinforce concepts that are due for revision based on your
            learning progress.
          </p>
        </section>

        <section className="revision-card">
          <div className="revision-section-heading">
            <h2>Available Revision Quizzes</h2>

            <p>
              Your revision quizzes will appear here when concepts become due
              for review.
            </p>
          </div>

          {loading ? (
            <div className="revision-empty">
              <h3>Checking for revision quizzes...</h3>

              <p>
                Checking your learning progress for concepts that are due
                for revision.
              </p>
            </div>
          ) : error ? (
            <div className="revision-empty">
              <h3>Unable to load revision quizzes</h3>

              <p>{error}</p>
            </div>
          ) : revisionConcepts.length === 0 ? (
            <div className="revision-empty">
              <h3>No revision quizzes available</h3>

              <p>
                Complete lessons and continue learning. Revision quizzes will
                appear here when they become due.
              </p>
            </div>
          ) : (
            <div className="revision-list">
              {revisionConcepts.map((concept) => (
                <div
                  key={concept.knowledge_node_id}
                  className="revision-item"
                >
                  <div>
                    <span className="revision-item-label">
                      REVISION QUIZ
                    </span>

                    <h3>{concept.concept_name}</h3>

                    <p>
                      {concept.description ||
                        'Reinforce this concept through a revision quiz.'}
                    </p>

                    <span>
                      Course: {concept.course_id}
                    </span>
                  </div>

                  <button
                    type="button"
                    className="lesson-primary-button"
                    onClick={() =>
                      startRevisionQuiz(concept.course_id)
                    }
                    disabled={generatingCourseId === concept.course_id}
                  >
                    {generatingCourseId === concept.course_id
                      ? 'Generating Quiz...'
                      : 'Start Revision Quiz'}
                  </button>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  )
}

export default RevisionQuizzes