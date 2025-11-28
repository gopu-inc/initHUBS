export default function StatsCard({ title, value, icon, color = 'blue' }) {
  const colorClasses = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    yellow: 'bg-yellow-500',
    purple: 'bg-purple-500',
  }

  return (
    <div className="github-card">
      <div className="flex items-center">
        <div className={`p-3 rounded-lg ${colorClasses[color]} text-white`}>
          {icon}
        </div>
        <div className="ml-4">
          <p className="text-sm font-medium text-gray-300">{title}</p>
          <p className="text-2xl font-bold text-white">{value}</p>
        </div>
      </div>
    </div>
  )
}
