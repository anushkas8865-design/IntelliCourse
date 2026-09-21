import { createContext, useContext, useEffect, useState } from 'react'
import { getProfile, loginUser } from '../api/authApi'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => {
    return localStorage.getItem('access_token')
  })

  const [user, setUser] = useState(() => {
    const storedUser = localStorage.getItem('user')

    return storedUser ? JSON.parse(storedUser) : null
  })

  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function restoreSession() {
      if (!token) {
        setLoading(false)
        return
      }

      try {
        const data = await getProfile(token)

        setUser(data.user)
        localStorage.setItem('user', JSON.stringify(data.user))
      } catch (error) {
        console.error('Session restore failed:', error)

        localStorage.removeItem('access_token')
        localStorage.removeItem('user')

        setToken(null)
        setUser(null)
      } finally {
        setLoading(false)
      }
    }

    restoreSession()
  }, [token])

  async function login(email, password) {
    const data = await loginUser(email, password)

    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('user', JSON.stringify(data.user))

    setToken(data.access_token)
    setUser(data.user)

    return data
  }

  function logout() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')

    setToken(null)
    setUser(null)
  }

  const value = {
    token,
    user,
    loading,
    isAuthenticated: Boolean(token && user),
    login,
    logout,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}