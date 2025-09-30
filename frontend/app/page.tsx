'use client'

import { useState, useEffect } from 'react'
import { 
  PhoneIcon,
  ChartBarIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  PlayIcon,
  CloudArrowUpIcon
} from '@heroicons/react/24/outline'
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line
} from 'recharts'

// Mock data for demonstration
const mockStats = {
  totalCalls: 1247,
  completedCalls: 1189,
  failedCalls: 32,
  processingCalls: 26,
  goodCalls: 987,
  badCalls: 202,
  totalDurationMinutes: 15678.5,
  avgProcessingTimeSeconds: 45.2
}

const mockViolations = [
  { type: 'bindingstid_missing', count: 89 },
  { type: 'price_incomplete', count: 67 },
  { type: 'excessive_pressure', count: 46 }
]

const mockRecentCalls = [
  { 
    id: 1, 
    filename: 'call_2024_001.wav', 
    status: 'completed', 
    result: 'bad', 
    duration: '04:32',
    violations: ['bindingstid_missing'],
    createdAt: new Date('2024-01-15T10:30:00')
  },
  { 
    id: 2, 
    filename: 'call_2024_002.wav', 
    status: 'completed', 
    result: 'good', 
    duration: '06:15',
    violations: [],
    createdAt: new Date('2024-01-15T10:45:00')
  },
  { 
    id: 3, 
    filename: 'call_2024_003.wav', 
    status: 'processing', 
    result: null, 
    duration: '03:41',
    violations: [],
    createdAt: new Date('2024-01-15T11:00:00')
  }
]

const chartData = [
  { name: 'Man', good: 120, bad: 25 },
  { name: 'Tir', good: 98, bad: 31 },
  { name: 'Ons', good: 135, bad: 18 },
  { name: 'Tor', good: 142, bad: 22 },
  { name: 'Fre', good: 155, bad: 15 },
  { name: 'Lør', good: 89, bad: 12 },
  { name: 'Søn', good: 67, bad: 8 }
]

const COLORS = ['#22c55e', '#ef4444', '#f59e0b', '#3b82f6']

export default function Dashboard() {
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Simulate loading
    const timer = setTimeout(() => setIsLoading(false), 1000)
    return () => clearTimeout(timer)
  }, [])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="loading-spinner"></div>
        <span className="ml-2 text-gray-600 dark:text-gray-400">Laster dashboard...</span>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="md:flex md:items-center md:justify-between">
        <div className="min-w-0 flex-1">
          <h1 className="text-2xl font-bold leading-7 text-gray-900 dark:text-white sm:truncate sm:text-3xl sm:tracking-tight">
            Dashboard
          </h1>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Oversikt over AI-analyse av telefonsamtaler
            </p>
        </div>
        <div className="mt-4 flex md:ml-4 md:mt-0">
          <button className="btn btn-primary">
            <CloudArrowUpIcon className="h-4 w-4 mr-2" />
            Last opp ny fil
          </button>
        </div>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {/* Total Calls */}
        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <PhoneIcon className="h-8 w-8 text-primary-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                    Totale oppringinger
                  </dt>
                  <dd className="text-lg font-medium text-gray-900 dark:text-white">
                    {mockStats.totalCalls.toLocaleString()}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        {/* Good vs Bad */}
        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ChartBarIcon className="h-8 w-8 text-success-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                    Godkjente / Avviste
                  </dt>
                  <dd className="text-lg font-medium text-gray-900 dark:text-white">
                    {mockStats.goodCalls} / {mockStats.badCalls}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        {/* Processing Time */}
        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ClockIcon className="h-8 w-8 text-warning-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                    Gjennomsnittlig behandlingstid
                  </dt>
                  <dd className="text-lg font-medium text-gray-900 dark:text-white">
                    {mockStats.avgProcessingTimeSeconds}s
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        {/* Violations */}
        <div className="card">
          <div className="card-body">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ExclamationTriangleIcon className="h-8 w-8 text-error-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                    Regelbrudd funnet
                  </dt>
                  <dd className="text-lg font-medium text-gray-900 dark:text-white">
                    {mockViolations.reduce((sum, v) => sum + v.count, 0)}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
        {/* Bar Chart */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">
              Ukentlig analyse
            </h3>
          </div>
          <div className="card-body">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="good" fill="#22c55e" name="Godkjent" />
                <Bar dataKey="bad" fill="#ef4444" name="Avvist" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Pie Chart */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">
              Regelbrudd fordeling
            </h3>
          </div>
          <div className="card-body">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={mockViolations}
                  dataKey="count"
                  nameKey="type"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  fill="#8884d8"
                  label
                >
                  {mockViolations.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Recent Calls */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">
            Siste oppringinger
          </h3>
        </div>
        <div className="card-body">
          <div className="overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-800">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Fil
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Resultat
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Varighet
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Handlinger
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {mockRecentCalls.map((call) => (
                  <tr key={call.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                      {call.filename}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`badge ${
                        call.status === 'completed' ? 'badge-success' :
                        call.status === 'processing' ? 'badge-warning' :
                        'badge-error'
                      }`}>
                        {call.status === 'completed' ? 'Fullført' :
                         call.status === 'processing' ? 'Behandles' : 'Feilet'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {call.result && (
                        <span className={`badge ${
                          call.result === 'good' ? 'badge-success' : 'badge-error'
                        }`}>
                          {call.result === 'good' ? 'Godkjent' : 'Avvist'}
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {call.duration}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button className="btn btn-ghost btn-sm">
                        <PlayIcon className="h-4 w-4 mr-1" />
                        Spill av
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
