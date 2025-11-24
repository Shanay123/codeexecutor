import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import Editor from '@monaco-editor/react'
import api from '../config/api'

const ProblemDetail = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  
  const [problem, setProblem] = useState(null)
  const [solution, setSolution] = useState(null)
  const [code, setCode] = useState('')
  const [testCases, setTestCases] = useState([])
  const [newTestInput, setNewTestInput] = useState('')
  const [newTestOutput, setNewTestOutput] = useState('')
  const [testResults, setTestResults] = useState(null)
  const [loading, setLoading] = useState(true)
  const [executing, setExecuting] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    fetchProblemData()
  }, [id])

  const fetchProblemData = async () => {
    try {
      const [problemRes, testCasesRes] = await Promise.all([
        api.get(`/api/problems/${id}`),
        api.get(`/api/test-cases/${id}`)
      ])
      
      setProblem(problemRes.data)
      setTestCases(testCasesRes.data)
      
      // Try to fetch existing solution
      try {
        const solutionRes = await api.get(`/api/solutions/${id}`)
        setSolution(solutionRes.data)
        setCode(solutionRes.data.solution_code)
      } catch (err) {
        // No solution exists - populate with function signature template
        if (problemRes.data.function_signature) {
          const template = `${problemRes.data.function_signature}
    """
    Implement your solution here.
    """
    pass
`
          setCode(template)
        }
      }
    } catch (err) {
      setError('Failed to load problem data')
    } finally {
      setLoading(false)
    }
  }

  const handleSaveSolution = async () => {
    try {
      const response = await api.post('/api/solutions', {
        problem_id: id,
        solution_code: code
      })
      setSolution(response.data)
      setSuccess('Solution saved!')
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError('Failed to save solution')
    }
  }

  const handleAddTestCase = async () => {
    if (!newTestInput || !newTestOutput) {
      setError('Please provide both input and output')
      return
    }

    try {
      const response = await api.post('/api/test-cases', {
        problem_id: id,
        input_data: newTestInput,
        expected_output: newTestOutput
      })
      setTestCases([...testCases, response.data])
      setNewTestInput('')
      setNewTestOutput('')
      setSuccess('Test case added!')
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError('Failed to add test case')
    }
  }

  const handleDeleteTestCase = async (testCaseId) => {
    try {
      await api.delete(`/api/test-cases/${testCaseId}`)
      setTestCases(testCases.filter(tc => tc.id !== testCaseId))
      setSuccess('Test case deleted!')
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError('Failed to delete test case')
    }
  }

  const handleRunTests = async () => {
    if (testCases.length === 0) {
      setError('Please add at least one test case')
      return
    }

    setExecuting(true)
    setError('')
    setTestResults(null)

    try {
      // Save solution first
      await handleSaveSolution()
      
      const response = await api.post('/api/execute', {
        solution_code: code,
        test_cases: testCases
      }, {
        params: {
          function_signature: problem?.function_signature
        }
      })
      setTestResults(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to execute code')
    } finally {
      setExecuting(false)
    }
  }

  const handleSubmit = async () => {
    if (!testResults || !testResults.all_passed) {
      setError('All tests must pass before submitting')
      return
    }

    setSubmitting(true)
    setError('')

    try {
      await api.post('/api/submissions', {
        problem_id: id,
        solution_id: solution.id,
        test_results: testResults.results
      })
      setSuccess('Submitted for review!')
      setTimeout(() => navigate('/submissions'), 2000)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to submit')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return <div className="text-center py-8">Loading...</div>
  }

  if (!problem) {
    return <div className="text-center py-8">Problem not found</div>
  }

  return (
    <div className="px-4 sm:px-0">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">{problem.title}</h1>
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
        {/* Left column - Problem description and test cases */}
        <div className="space-y-6">
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Problem Description</h2>
            <p className="text-gray-700 whitespace-pre-wrap">{problem.description}</p>
            
            <div className="mt-6">
              <h3 className="font-semibold mb-2">Example:</h3>
              <div className="bg-gray-50 p-4 rounded">
                <p className="text-sm font-medium text-gray-600">Input:</p>
                <pre className="text-sm text-gray-800 font-mono mb-2">{problem.example_input}</pre>
                <p className="text-sm font-medium text-gray-600">Output:</p>
                <pre className="text-sm text-gray-800 font-mono">{problem.example_output}</pre>
              </div>
            </div>
          </div>

          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Test Cases</h2>
            
            {testCases.length > 0 && (
              <div className="space-y-3 mb-4">
                {testCases.map((tc, index) => (
                  <div key={tc.id} className="border border-gray-200 rounded p-3">
                    <div className="flex justify-between items-start mb-2">
                      <span className="text-sm font-semibold text-gray-700">Test Case {index + 1}</span>
                      <button
                        onClick={() => handleDeleteTestCase(tc.id)}
                        className="text-red-600 hover:text-red-800 text-sm"
                      >
                        Delete
                      </button>
                    </div>
                    <div className="text-sm">
                      <p className="text-gray-600">Input:</p>
                      <pre className="bg-gray-50 p-2 rounded font-mono text-xs mb-2">{tc.input_data}</pre>
                      <p className="text-gray-600">Expected Output:</p>
                      <pre className="bg-gray-50 p-2 rounded font-mono text-xs">{tc.expected_output}</pre>
                    </div>
                  </div>
                ))}
              </div>
            )}

            <div className="border-t border-gray-200 pt-4">
              <h3 className="font-semibold mb-3">Add New Test Case</h3>
              <div className="mb-2 text-xs text-blue-600 bg-blue-50 p-2 rounded">
                Use JSON format: Input is array of args (e.g., [2, 3]), Output is return value (e.g., 5 or [0,1])
              </div>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Input (JSON array of arguments)
                  </label>
                  <textarea
                    rows={2}
                    className="w-full border border-gray-300 rounded px-3 py-2 text-sm font-mono"
                    value={newTestInput}
                    onChange={(e) => setNewTestInput(e.target.value)}
                    placeholder='[2, 3] or ["hello", 5] or [[1,2,3], 6]'
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Expected Output (JSON)
                  </label>
                  <textarea
                    rows={2}
                    className="w-full border border-gray-300 rounded px-3 py-2 text-sm font-mono"
                    value={newTestOutput}
                    onChange={(e) => setNewTestOutput(e.target.value)}
                    placeholder='5 or "result" or [0, 1]'
                  />
                </div>
                <button
                  onClick={handleAddTestCase}
                  className="w-full bg-gray-200 hover:bg-gray-300 text-gray-800 py-2 rounded font-medium"
                >
                  Add Test Case
                </button>
              </div>
            </div>
          </div>

          {testResults && (
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-4">Test Results</h2>
              <div className="space-y-3">
                {testResults.results.map((result, index) => (
                  <div
                    key={result.test_case_id}
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
              
              {testResults.all_passed && (
                <div className="mt-4 p-4 bg-green-100 border border-green-300 rounded">
                  <p className="text-green-800 font-semibold">All tests passed! You can now submit for review.</p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right column - Code editor and actions */}
        <div className="space-y-4">
          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">Solution</h2>
              <div className="text-xs text-gray-500">
                {problem?.function_signature && (
                  <code className="bg-gray-100 px-2 py-1 rounded">{problem.function_signature}</code>
                )}
              </div>
            </div>
            <div className="border border-gray-300 rounded overflow-hidden" style={{ height: '500px' }}>
              <Editor
                height="100%"
                defaultLanguage="python"
                value={code}
                onChange={(value) => setCode(value || '')}
                theme="vs-light"
                options={{
                  minimap: { enabled: false },
                  fontSize: 14,
                  lineNumbers: 'on',
                  scrollBeyondLastLine: false,
                  automaticLayout: true,
                }}
              />
            </div>
          </div>

          <div className="bg-white shadow rounded-lg p-6 space-y-3">
            <button
              onClick={handleSaveSolution}
              className="w-full bg-gray-200 hover:bg-gray-300 text-gray-800 py-2 rounded font-medium"
            >
              Save Solution
            </button>
            
            <button
              onClick={handleRunTests}
              disabled={executing}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded font-medium disabled:opacity-50"
            >
              {executing ? 'Running Tests...' : 'Run Tests'}
            </button>
            
            <button
              onClick={handleSubmit}
              disabled={submitting || !testResults?.all_passed}
              className="w-full bg-green-600 hover:bg-green-700 text-white py-2 rounded font-medium disabled:opacity-50"
            >
              {submitting ? 'Submitting...' : 'Submit for Review'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ProblemDetail

