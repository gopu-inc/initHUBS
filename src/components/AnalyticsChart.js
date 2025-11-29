'use client'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

const data = [
  { name: 'Jan', commits: 45, prs: 12, issues: 8 },
  { name: 'Fév', commits: 52, prs: 15, issues: 6 },
  { name: 'Mar', commits: 48, prs: 11, issues: 9 },
  { name: 'Avr', commits: 67, prs: 18, issues: 12 },
  { name: 'Mai', commits: 73, prs: 22, issues: 14 },
  { name: 'Jun', commits: 81, prs: 25, issues: 11 },
]

export default function AnalyticsChart() {
  return (
    <div className="github-card">
      <h3 className="text-lg font-semibold text-white mb-4">
        Activité des 6 derniers mois
      </h3>
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis 
              dataKey="name" 
              stroke="#9CA3AF"
              fontSize={12}
            />
            <YAxis 
              stroke="#9CA3AF"
              fontSize={12}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#1F2937',
                border: '1px solid #374151',
                borderRadius: '6px'
              }}
            />
            <Line 
              type="monotone" 
              dataKey="commits" 
              stroke="#3B82F6" 
              strokeWidth={2}
              name="Commits"
            />
            <Line 
              type="monotone" 
              dataKey="prs" 
              stroke="#10B981" 
              strokeWidth={2}
              name="Pull Requests"
            />
            <Line 
              type="monotone" 
              dataKey="issues" 
              stroke="#EF4444" 
              strokeWidth={2}
              name="Issues"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
