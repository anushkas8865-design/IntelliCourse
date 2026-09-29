import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import BackButton from '../components/BackButton'
import { apiRequest } from '../api/api'
import { useAuth } from '../context/AuthContext'
import './RevisionQuiz.css'

function RevisionQuiz() {
  const location = useLocation()
  const navigate = useNavigate()
  const { token } = useAuth()

  const quiz = location.state?.quiz

  const [selectedAnswers, setSelectedAnswers] = useState({})
  const [result, setResult] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  if (!quiz) {
    return (
      <div className="revision-quiz-page">
        <div className="revision-quiz-container">
          <BackButton />

          <div className="revision-quiz-error">
            <h2>Revision quiz not found</h2>

            <p>
              The revision quiz could not be loaded. Please return to the
              Revision Quizzes page and start again.
            </p>

            <button
              type="button"
              className="lesson-primary-button"
              onClick={() => navigate('/revision-quizzes')}
            >
              Back to Revision Quizzes
            </button>
          </div>
        </div>
      </div>
    )
  }

  function handleAnswerSelect(quizId, answer) {
    if (result) {
      return
    }

    setSelectedAnswers((previousAnswers) => ({
      ...previousAnswers,
      [quizId]: answer,
    }))

    setError('')
  }

  async function submitRevisionQuiz() {
    if (!token) {
      setError('You must be logged in to submit the quiz.')
      return
    }

    const unansweredQuestions = quiz.questions.filter(
      (question) => !selectedAnswers[question.quiz_id]
    )

    if (unansweredQuestions.length > 0) {
      setError(
        'Please answer all questions before submitting the quiz.'
      )
      return
    }

    setSubmitting(true)
    setError('')

    const answers = quiz.questions.map((question) => ({
      quiz_id: question.quiz_id,
      answer: selectedAnswers[question.quiz_id],
    }))

    try {
      const data = await apiRequest('/api/quiz/evaluate', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          course_id: quiz.course_id,
          quiz_type: 'revision',
          answers,
        }),
      })

      setResult(data)
    } catch (error) {
      console.error(
        'Revision quiz evaluation failed:',
        error
      )

      setError(
        error.message ||
          'Unable to evaluate the revision quiz.'
      )
    } finally {
      setSubmitting(false)
    }
  }

  if (result) {
    return (
      <div className="revision-quiz-page">
        <div className="revision-quiz-container">
          <BackButton />

          <section className="revision-quiz-header">
            <span className="revision-quiz-label">
              REVISION COMPLETE
            </span>

            <h1>{quiz.course_title || 'Revision Quiz'}</h1>

            <p>
              Your revision quiz has been evaluated successfully.
            </p>
          </section>

          <section className="revision-quiz-card">
            <div className="revision-quiz-section-heading">
              <h2>Revision Quiz Result</h2>
            </div>

            <div className="revision-quiz-result-summary">
              <h3>{result.score}%</h3>

              <p>
                {result.correct_answers} correct out of{' '}
                {result.total_questions} questions
              </p>

              <p>
                Incorrect answers: {result.incorrect_answers}
              </p>
            </div>

            <div className="revision-quiz-content">
              {result.results.map((questionResult, index) => (
                <div
                  key={questionResult.quiz_id}
                  className="revision-quiz-question"
                >
                  <h3>
                    {index + 1}. {questionResult.concept_name}
                  </h3>

                  <p>
                    Your answer:{' '}
                    <strong>
                      {questionResult.selected_answer}
                    </strong>
                  </p>

                  <p>
                    Correct answer:{' '}
                    <strong>
                      {questionResult.correct_answer}
                    </strong>
                  </p>

                  <p>
                    {questionResult.correct
                      ? 'Your answer is correct.'
                      : 'Your answer is incorrect.'}
                  </p>

                  <p>
                    {questionResult.explanation}
                  </p>
                </div>
              ))}
            </div>

            <div className="revision-quiz-result-actions">
              <button
                type="button"
                className="lesson-primary-button"
                onClick={() =>
                  navigate('/revision-quizzes')
                }
              >
                Back to Revision Quizzes
              </button>
            </div>
          </section>
        </div>
      </div>
    )
  }

  return (
    <div className="revision-quiz-page">
      <div className="revision-quiz-container">
        <BackButton />

        <section className="revision-quiz-header">
          <span className="revision-quiz-label">
            ADAPTIVE REVISION
          </span>

          <h1>
            {quiz.course_title || 'Revision Quiz'}
          </h1>

          <p>
            Reinforce concepts that are due for revision.
          </p>
        </section>

        <section className="revision-quiz-card">
          <div className="revision-quiz-section-heading">
            <h2>Revision Questions</h2>

            <p>
              Answer all questions below to reinforce your
              understanding.
            </p>
          </div>

          {error && (
            <div className="revision-quiz-error">
              <p>{error}</p>
            </div>
          )}

          <div className="revision-quiz-content">
            {quiz.questions.map((question, index) => (
              <div
                key={question.quiz_id}
                className="revision-quiz-question"
              >
                <h3>
                  {index + 1}. {question.question}
                </h3>

                <div className="revision-quiz-options">
                  {[
                    ['A', question.option_a],
                    ['B', question.option_b],
                    ['C', question.option_c],
                    ['D', question.option_d],
                  ].map(([letter, option]) => {
                    const isSelected =
                      selectedAnswers[question.quiz_id] === letter

                    return (
                      <button
                        key={letter}
                        type="button"
                        className={`revision-quiz-option ${
                          isSelected
                            ? 'revision-quiz-option-selected'
                            : ''
                        }`}
                        onClick={() =>
                          handleAnswerSelect(
                            question.quiz_id,
                            letter
                          )
                        }
                        disabled={submitting}
                      >
                        <span className="revision-quiz-option-letter">
                          {letter}
                        </span>

                        <span>{option}</span>
                      </button>
                    )
                  })}
                </div>
              </div>
            ))}
          </div>

          <div className="revision-quiz-submit-section">
            <button
              type="button"
              className="lesson-primary-button"
              onClick={submitRevisionQuiz}
              disabled={submitting}
            >
              {submitting
                ? 'Submitting Quiz...'
                : 'Submit Revision Quiz'}
            </button>
          </div>
        </section>
      </div>
    </div>
  )
}

export default RevisionQuiz