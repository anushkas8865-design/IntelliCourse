import './App.css'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'

import Dashboard from './pages/Dashboard'
import Login from './pages/Login'
import Register from './pages/Register'
import MyCourses from './pages/MyCourses'
import CreateCourse from './pages/CreateCourse'
import CourseDetails from './pages/CourseDetails'
import Lesson from './pages/Lesson'
import Settings from './pages/Settings'

import { useAuth } from './context/AuthContext'

function App() {
  const { isAuthenticated, loading } = useAuth()

  if (loading) {
    return <div>Loading...</div>
  }

  return (
    <BrowserRouter>
      <Routes>
        {!isAuthenticated ? (
          <>
            <Route path="/" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route
              path="*"
              element={<Navigate to="/" replace />}
            />
          </>
        ) : (
          <>
            <Route path="/" element={<Dashboard />} />
            <Route path="/courses" element={<MyCourses />} />
            <Route
              path="/create-course"
              element={<CreateCourse />}
            />
            <Route
              path="/course/:courseId"
              element={<CourseDetails />}
            />
            <Route
              path="/lesson/:lessonId"
              element={<Lesson />}
            />
            <Route path="/settings" element={<Settings />} />

            <Route
              path="*"
              element={<Navigate to="/" replace />}
            />
          </>
        )}
      </Routes>
    </BrowserRouter>
  )
}

export default App