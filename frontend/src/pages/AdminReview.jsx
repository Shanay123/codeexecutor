import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import Editor from '@monaco-editor/react'
import api from '../config/api'

const AdminReview = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  
  const [submission, setSubmission] = useState(null)
  const [testCases, setTestCases] = useState([])
  const [editingTestCase, setEditingTestCase] = useState(null)
  const [adminNotes, setAdminNotes] = useState('')
  const [loading, setLoading] = useState(true)
  const [rerunning, setRerunning] = useState(false)
  const [testResults, setTestResults] = useState(null)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    fetchSubmissionData()
  }, [id])

  const fetchSubmissionData = async () => {
    try {
      const submissionRes = await api.get(`/api/admin/submissions/${id}`)
      setSubmission(submissionRes.data)
      setAdminNotes(submissionRes.data.admin_notes || '')
      setTestResults({ results: submissionRes.data.test_results })
      
      // Fetch test cases
      const testCasesRes = await api.get(`/api/test-cases/${submissionRes.data.problem_id}`)
      setTestCases(testCasesRes.data)
    } catch (err) {
      setError('Failed to load submission data')
    } finally {
      setLoading(false)
    }
  }

  const handleUpdateTestCase = async (testCaseId, input, output) => {
    try {
      await api.put(`/api/admin/test-cases/${testCaseId}`, {
        input_data: input,
        expected_output: output
      })
      
      // Update local state
      setTestCases(testCases.map(tc => 
        tc.id === testCaseId 
          ? { ...tc, input_data: input, expected_output: output }
          : tc
      ))
      
      setEditingTestCase(null)
      setSuccess('Test case updated!')
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError('Failed to update test case')
    }
  }

  const handleRerun = async () => {
    setRerunning(true)
    setError('')
    
    try {
      const response = await api.post(`/api/admin/rerun/${id}`)
      setTestResults(response.data)
      setSuccess('Tests rerun successfully!')
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to rerun tests')
    } finally {
      setRerunning(false)
    }
  }

  const handleReview = async (status) => {
    try {
      await api.put(`/api/admin/submissions/${id}`, {
        status,
        admin_notes: adminNotes
      })
      setSuccess(`Submission ${status}!`)
      setTimeout(() => navigate('/admin'), 2000)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update submission')
    }
  }

  if (loading) {
    return <div className="text-center py-8">Loading...</div>
  }

  if (!submission) {
    return <div className="text-center py-8">Submission not found</div>
  }

  return (
    <div className="px-4 sm:px-0">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Review Submission</h1>
        <p className="mt-2 text-sm text-gray-600">
          Problem: {submission.problem_title}
        </p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {success && (
        <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded mb-4">
          {success}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left column - Solution and test cases */}
        <div className="space-y-6">
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Submitted Solution</h2>
            <div className="border border-gray-300 rounded overflow-hidden" style={{ height: '400px' }}>
              <Editor
                height="100%"
                defaultLanguage="python"
                value={submission.solution_code || ''}
                theme="vs-light"
                options={{
                  readOnly: true,
                  minimap: { enabled: false },
                  fontSize: 14,
                  lineNumbers: 'on',
                  scrollBeyondLastLine: false,
                }}
              />
            </div>
          </div>

          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">Test Cases</h2>
              <button
                onClick={handleRerun}
                disabled={rerunning}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded font-medium disabled:opacity-50 text-sm"
              >
                {rerunning ? 'Rerunning...' : 'Rerun Tests'}
              </button>
            </div>
            
            <div className="mb-3 text-xs text-gray-600 bg-gray-50 p-2 rounded">
              You can edit test cases and rerun tests at any time to verify edge cases
            </div>
            
            <div className="space-y-4">
              {testCases.map((tc, index) => (
                <div key={tc.id} className="border border-gray-200 rounded p-4">
                  <div className="flex justify-between items-start mb-2">
                    <span className="text-sm font-semibold text-gray-700">Test Case {index + 1}</span>
                    {editingTestCase?.id === tc.id ? (
                      <div className="space-x-2">
                        <button
                          onClick={() => handleUpdateTestCase(
                            tc.id,
                            editingTestCase.input,
                            editingTestCase.output
                          )}
                          className="text-green-600 hover:text-green-800 text-sm font-medium"
                        >
                          Save
                        </button>
                        <button
                          onClick={() => setEditingTestCase(null)}
                          className="text-gray-600 hover:text-gray-800 text-sm font-medium"
                        >
                          Cancel
                        </button>
                      </div>
                    ) : (
                      <button
                        onClick={() => setEditingTestCase({
                          id: tc.id,
                          input: tc.input_data,
                          output: tc.expected_output
                        })}
                        className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                      >
                        Edit
                      </button>
                    )}
                  </div>
                  
                  {editingTestCase?.id === tc.id ? (
                    <div className="space-y-3">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Input</label>
                        <textarea
                          rows={2}
                          className="w-full border border-gray-300 rounded px-3 py-2 text-sm font-mono"
                          value={editingTestCase.input}
                          onChange={(e) => setEditingTestCase({
                            ...editingTestCase,
                            input: e.target.value
                          })}
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Expected Output</label>
                        <textarea
                          rows={2}
                          className="w-full border border-gray-300 rounded px-3 py-2 text-sm font-mono"
                          value={editingTestCase.output}
                          onChange={(e) => setEditingTestCase({
                            ...editingTestCase,
                            output: e.target.value
                          })}
                        />
                      </div>
                    </div>
                  ) : (
                    <div className="text-sm">
                      <p className="text-gray-600">Input:</p>
                      <pre className="bg-gray-50 p-2 rounded font-mono text-xs mb-2">{tc.input_data}</pre>
                      <p className="text-gray-600">Expected Output:</p>
                      <pre className="bg-gray-50 p-2 rounded font-mono text-xs">{tc.expected_output}</pre>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right column - Test results and review */}
        <div className="space-y-6">
          {testResults && (
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-4">Test Results</h2>
              <div className="space-y-3">
                {testResults.results.map((result, index) => (
                  <div
                    key={index}
                    className={`border rounded p-3 ${
                      result.passed ? 'border-green-500 bg-green-50' : 'border-red-500 bg-red-50'
                    }`}
                  >
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-semibold">Test Case {index + 1}</span>
                      <span className={`text-sm font-semibold ${result.passed ? 'text-green-700' : 'text-red-700'}`}>
                        {result.passed ? 'PASSED' : 'FAILED'}
                      </span>
                    </div>
                    {!result.passed && (
                      <div className="text-sm">
                        {result.error && (
                          <div>
                            <p className="font-medium text-red-700">Error:</p>
                            <pre className="bg-white p-2 rounded text-xs text-red-600 overflow-x-auto">{result.error}</pre>
                          </div>
                        )}
                        {result.actual_output && (
                          <div className="mt-2">
                            <p className="font-medium text-gray-700">Actual Output:</p>
                            <pre className="bg-white p-2 rounded text-xs overflow-x-auto">{result.actual_output}</pre>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Review Decision</h2>
            
            {submission.status !== 'pending' && (
              <div className={`mb-4 p-4 rounded ${
                submission.status === 'approved' ? 'bg-green-100 border border-green-300' : 'bg-red-100 border border-red-300'
              }`}>
                <p className={`font-semibold ${
                  submission.status === 'approved' ? 'text-green-800' : 'text-red-800'
                }`}>
                  This submission has been {submission.status}
                </p>
                {submission.reviewed_at && (
                  <p className="text-sm text-gray-600 mt-1">
                    Reviewed on {new Date(submission.reviewed_at).toLocaleString()}
                  </p>
                )}
              </div>
            )}
            
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Admin Notes
              </label>
              <textarea
                rows={4}
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
                value={adminNotes}
                onChange={(e) => setAdminNotes(e.target.value)}
                placeholder="Add notes for the user..."
                disabled={submission.status !== 'pending'}
              />
            </div>

            <div className="space-y-3">
              {submission.status === 'pending' ? (
                <>
                  <button
                    onClick={() => handleReview('approved')}
                    className="w-full bg-green-600 hover:bg-green-700 text-white py-2 rounded font-medium"
                  >
                    Approve Submission
                  </button>
                  <button
                    onClick={() => handleReview('rejected')}
                    className="w-full bg-red-600 hover:bg-red-700 text-white py-2 rounded font-medium"
                  >
                    Reject Submission
                  </button>
                </>
              ) : (
                <div className="text-center text-gray-500 py-2">
                  Submission already reviewed
                </div>
              )}
              <button
                onClick={() => navigate('/admin')}
                className="w-full bg-gray-200 hover:bg-gray-300 text-gray-800 py-2 rounded font-medium"
              >
                Back to Dashboard
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AdminReview

