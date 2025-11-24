import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import Login from './pages/Login'
import Signup from './pages/Signup'
import Dashboard from './pages/Dashboard'
import CreateProblem from './pages/CreateProblem'
import ProblemDetail from './pages/ProblemDetail'
import Submissions from './pages/Submissions'
import AdminDashboard from './pages/AdminDashboard'
import AdminReview from './pages/AdminReview'
import Layout from './components/Layout'

const ProtectedRoute = ({ children, adminOnly = false }) => {
  const { user, loading, isAdmin } = useAuth()

  if (loading) {
    return <div className="flex items-center justify-center h-screen">
      <div className="text-xl">Loading...</div>
    </div>
  }

  if (!user) {
    return <Navigate to="/login" />
  }

  if (adminOnly && !isAdmin) {
    return <Navigate to="/" />
  }

  return children
}

const AppRoutes = () => {
  const { user } = useAuth()

  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to="/" /> : <Login />} />
      <Route path="/signup" element={user ? <Navigate to="/" /> : <Signup />} />
      
      <Route path="/" element={
        <ProtectedRoute>
          <Layout><Dashboard /></Layout>
        </ProtectedRoute>
      } />
      
      <Route path="/create-problem" element={
        <ProtectedRoute>
          <Layout><CreateProblem /></Layout>
        </ProtectedRoute>
      } />
      
      <Route path="/problem/:id" element={
        <ProtectedRoute>
          <Layout><ProblemDetail /></Layout>
        </ProtectedRoute>
      } />
      
      <Route path="/submissions" element={
        <ProtectedRoute>
          <Layout><Submissions /></Layout>
        </ProtectedRoute>
      } />
      
      <Route path="/admin" element={
        <ProtectedRoute adminOnly>
          <Layout><AdminDashboard /></Layout>
        </ProtectedRoute>
      } />
      
      <Route path="/admin/review/:id" element={
        <ProtectedRoute adminOnly>
          <Layout><AdminReview /></Layout>
        </ProtectedRoute>
      } />
    </Routes>
  )
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </Router>
  )
}

export default App

