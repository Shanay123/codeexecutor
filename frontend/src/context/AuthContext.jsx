import React, { createContext, useState, useContext, useEffect } from 'react'
import api from '../config/api'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('access_token')
    const userData = localStorage.getItem('user')
    
    if (token && userData) {
      setUser(JSON.parse(userData))
    }
    setLoading(false)
  }, [])

  const login = async (email, password) => {
    const response = await api.post('/api/auth/login', { email, password })
    const { user, session } = response.data
    
    localStorage.setItem('access_token', session.access_token)
    localStorage.setItem('user', JSON.stringify(user))
    setUser(user)
    
    return user
  }

  const signup = async (email, password, username) => {
    const response = await api.post('/api/auth/signup', { email, password, username })
    const { user, session } = response.data
    
    if (session?.access_token) {
      localStorage.setItem('access_token', session.access_token)
      localStorage.setItem('user', JSON.stringify(user))
      setUser(user)
    }
    
    return user
  }

  const logout = async () => {
    try {
      await api.post('/api/auth/logout')
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      setUser(null)
    }
  }

  const value = {
    user,
    login,
    signup,
    logout,
    loading,
    isAdmin: user?.role === 'admin'
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

