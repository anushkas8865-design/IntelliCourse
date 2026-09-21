import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import BackButton from '../components/BackButton'
import { apiRequest } from '../api/api'
import { useAuth } from '../context/AuthContext'
import './CreateCourse.css'

function CreateCourse() {
  const navigate = useNavigate()
  const { token } = useAuth()

  const [topic, setTopic] = useState('')
  const [difficulty, setDifficulty] = useState('Beginner')
  const [duration, setDuration] = useState('4 weeks')

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleGenerateCourse() {
    if (!topic.trim()) {
      setError('Please enter a course topic.')
      return
    }

    if (!token) {
      setError('Please log in again to generate a course.')
      return
    }

    setLoading(true)
    setError('')

    try {
      const data = await apiRequest('/api/course/generate', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic: topic.trim(),
          difficulty,
          duration,
        }),
      })

      if (!data?.course_id) {
        throw new Error('Course was generated, but no course ID was returned.')
      }

      navigate('/')
    } catch (error) {
      console.error('Course generation failed:', error)
      setError(error.message || 'Unable to generate course.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="create-course-page">
      <div className="create-course-container">
        <BackButton />

        <div className="create-course-header">
          <h1>Create Course</h1>
          <p>
            Build a personalized course using AI-powered course generation.
          </p>
        </div>

        <div className="create-course-card">
          <div className="create-course-form">
            <div className="create-course-field">
              <label htmlFor="course-topic">Course Topic</label>
              <input
                id="course-topic"
                type="text"
                placeholder="e.g. Python Programming"
                value={topic}
                onChange={(event) => setTopic(event.target.value)}
                disabled={loading}
              />
            </div>

            <div className="create-course-field">
              <label htmlFor="course-difficulty">Difficulty</label>
              <select
                id="course-difficulty"
                value={difficulty}
                onChange={(event) => setDifficulty(event.target.value)}
                disabled={loading}
              >
                <option value="Beginner">Beginner</option>
                <option value="Intermediate">Intermediate</option>
                <option value="Advanced">Advanced</option>
              </select>
            </div>

            <div className="create-course-field">
              <label htmlFor="course-duration">Duration</label>
              <select
                id="course-duration"
                value={duration}
                onChange={(event) => setDuration(event.target.value)}
                disabled={loading}
              >
                <option value="2 weeks">2 weeks</option>
                <option value="4 weeks">4 weeks</option>
                <option value="6 weeks">6 weeks</option>
                <option value="8 weeks">8 weeks</option>
              </select>
            </div>

            {error && (
              <div className="create-course-error">
                {error}
              </div>
            )}

            <button
              type="button"
              className="create-course-submit"
              onClick={handleGenerateCourse}
              disabled={loading}
            >
              {loading ? 'Generating Course...' : 'Generate Course'}
            </button>
          </div>

          <div className="create-course-info">
            Your course will be generated using the AI Course Builder
            backend and saved to your learning dashboard.
          </div>
        </div>
      </div>
    </div>
  )
}

export default CreateCourse