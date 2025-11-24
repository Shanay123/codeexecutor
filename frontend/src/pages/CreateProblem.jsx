import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../config/api'

const CreateProblem = () => {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [functionSignature, setFunctionSignature] = useState('def solution(nums: list[int], target: int) -> int:')
  const [exampleInput, setExampleInput] = useState('[1, 2, 3]')
  const [exampleOutput, setExampleOutput] = useState('6')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await api.post('/api/problems', {
        title,
        description,
        function_signature: functionSignature,
        example_input: exampleInput,
        example_output: exampleOutput,
      })
      navigate(`/problem/${response.data.id}`)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create problem')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="px-4 sm:px-0">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Create New Problem</h1>
        <p className="mt-2 text-sm text-gray-600">
          Define a coding problem that you'll solve and test
        </p>
        <div className="mt-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-semibold text-blue-900 mb-2">📝 LeetCode-Style Format</h3>
          <p className="text-sm text-blue-800 mb-2">
            Define the function signature that users will implement. Test inputs will be JSON arrays passed as function arguments.
          </p>
          <div className="bg-white rounded p-3 font-mono text-xs">
            <div className="text-gray-600">Example: def two_sum(nums: list[int], target: int) -&gt; list[int]:</div>
            <div className="text-gray-600 ml-4">Test Input: [[2,7,11,15], 9]</div>
            <div className="text-gray-600 ml-4">Expected Output: [0, 1]</div>
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="bg-white shadow-md rounded-lg p-6 space-y-6">
        <div>
          <label htmlFor="title" className="block text-sm font-medium text-gray-700">
            Problem Title
          </label>
          <input
            type="text"
            id="title"
            required
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g., Two Sum"
          />
        </div>

        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700">
            Description
          </label>
          <textarea
            id="description"
            required
            rows={6}
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Describe the problem in detail..."
          />
        </div>

        <div>
          <label htmlFor="functionSignature" className="block text-sm font-medium text-gray-700">
            Function Signature
          </label>
          <input
            type="text"
            id="functionSignature"
            required
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 font-mono text-sm"
            value={functionSignature}
            onChange={(e) => setFunctionSignature(e.target.value)}
            placeholder="def my_function(param1: type1, param2: type2) -> return_type:"
          />
          <p className="mt-1 text-xs text-gray-500">
            Define the exact function users must implement (e.g., "def add(a: int, b: int) -&gt; int:")
          </p>
        </div>

        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
          <div>
            <label htmlFor="exampleInput" className="block text-sm font-medium text-gray-700">
              Example Input (JSON array)
            </label>
            <textarea
              id="exampleInput"
              required
              rows={4}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 font-mono text-sm"
              value={exampleInput}
              onChange={(e) => setExampleInput(e.target.value)}
              placeholder='[2, 3] or ["hello", "world"]'
            />
            <p className="mt-1 text-xs text-gray-500">
              JSON array of arguments (e.g., [2, 3] for two args)
            </p>
          </div>

          <div>
            <label htmlFor="exampleOutput" className="block text-sm font-medium text-gray-700">
              Example Output (JSON)
            </label>
            <textarea
              id="exampleOutput"
              required
              rows={4}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 font-mono text-sm"
              value={exampleOutput}
              onChange={(e) => setExampleOutput(e.target.value)}
              placeholder='5 or "result" or [1, 2]'
            />
            <p className="mt-1 text-xs text-gray-500">
              JSON-encoded expected return value
            </p>
          </div>
        </div>

        <div className="flex justify-end space-x-3">
          <button
            type="button"
            onClick={() => navigate('/')}
            className="bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {loading ? 'Creating...' : 'Create Problem'}
          </button>
        </div>
      </form>
    </div>
  )
}

export default CreateProblem

