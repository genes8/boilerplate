import { createFileRoute, Link } from '@tanstack/react-router'
import { useAuth } from '@/hooks/useAuth'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { Button } from '@/components/ui/button'
import { motion } from 'motion/react'
import { 
  LayoutDashboard, 
  Users, 
  FileText, 
  TrendingUp,
  Clock,
  CheckCircle2,
  AlertCircle,
  LogOut,
  ChevronRight,
  Search,
  Shield,
  Zap,
  Activity,
  ArrowUpRight,
  ArrowDownRight,
  Plus
} from 'lucide-react'

export const Route = createFileRoute('/dashboard/')({
  component: DashboardPage,
})

function DashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  )
}

function DashboardContent() {
  const { user, logout } = useAuth()

  const stats = [
    { 
      title: 'Documents', 
      value: '1,234', 
      change: '+12%', 
      changeType: 'positive' as const,
      icon: FileText,
      color: 'from-blue-500 to-cyan-500'
    },
    { 
      title: 'Active Users', 
      value: '56', 
      change: '+8%', 
      changeType: 'positive' as const,
      icon: Users,
      color: 'from-violet-500 to-purple-500'
    },
    { 
      title: 'Pending', 
      value: '23', 
      change: '-15%', 
      changeType: 'negative' as const,
      icon: Clock,
      color: 'from-amber-500 to-orange-500'
    },
    { 
      title: 'Completed', 
      value: '89%', 
      change: '+5%', 
      changeType: 'positive' as const,
      icon: CheckCircle2,
      color: 'from-emerald-500 to-teal-500'
    },
  ]

  const recentActivity = [
    { action: 'Document uploaded', item: 'Q4 Report.pdf', time: '2 min ago', status: 'success' },
    { action: 'User invited', item: 'john@example.com', time: '15 min ago', status: 'success' },
    { action: 'Permission updated', item: 'Marketing Team', time: '1 hour ago', status: 'warning' },
    { action: 'Document shared', item: 'Budget 2024.xlsx', time: '2 hours ago', status: 'success' },
    { action: 'Comment added', item: 'Project Proposal', time: '3 hours ago', status: 'success' },
  ]

  const quickActions = [
    { title: 'Documents', description: 'Browse & manage', icon: FileText, color: 'from-blue-500 to-cyan-500', href: '/documents' },
    { title: 'Search', description: 'Full-text search', icon: Search, color: 'from-violet-500 to-purple-500', href: '/search' },
    { title: 'Users', description: 'Manage team', icon: Users, color: 'from-emerald-500 to-teal-500', href: '/admin/users' },
    { title: 'Roles', description: 'Access control', icon: Shield, color: 'from-amber-500 to-orange-500', href: '/admin/roles' },
  ]

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.08,
        delayChildren: 0.1,
      },
    },
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20, scale: 0.95 },
    visible: {
      opacity: 1,
      y: 0,
      scale: 1,
      transition: {
        type: 'spring' as const,
        stiffness: 100,
        damping: 15,
      },
    },
  }

  const headerVariants = {
    hidden: { opacity: 0, y: -20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        type: 'spring' as const,
        stiffness: 100,
        damping: 20,
      },
    },
  }

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-50 overflow-hidden">
      {/* Animated background grid */}
      <div className="fixed inset-0 pointer-events-none">
        <motion.div
          className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage: `
              linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px),
              linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)
            `,
            backgroundSize: '60px 60px',
          }}
          animate={{
            backgroundPosition: ['0 0', '60px 60px'],
          }}
          transition={{
            duration: 30,
            repeat: Infinity,
            ease: 'linear',
          }}
        />
      </div>

      {/* Header */}
      <motion.div
        variants={headerVariants}
        initial="hidden"
        animate="visible"
        className="relative z-40 border-b border-neutral-800 bg-neutral-900/50 backdrop-blur-xl"
      >
        <div className="max-w-7xl mx-auto px-6 py-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <motion.div 
                className="w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center"
                whileHover={{ rotate: 5, scale: 1.05 }}
                transition={{ type: 'spring', stiffness: 300, damping: 15 }}
              >
                <LayoutDashboard className="w-6 h-6 text-white" />
              </motion.div>
              <div>
                <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
                <p className="text-sm text-neutral-400">
                  Welcome back, <span className="text-neutral-200">{user?.username || 'User'}</span>
                </p>
              </div>
            </div>
            <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={logout}
                className="text-neutral-400 hover:text-neutral-50 hover:bg-neutral-800"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Sign out
              </Button>
            </motion.div>
          </div>
        </div>
      </motion.div>

      <div className="relative z-10 max-w-7xl mx-auto px-6 py-8">
        {/* Stats Grid */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8"
        >
          {stats.map((stat, index) => (
            <motion.div
              key={index}
              variants={itemVariants}
              whileHover={{ y: -4, scale: 1.02 }}
              transition={{ type: 'spring', stiffness: 300, damping: 20 }}
              className="group relative"
            >
              <div className="relative p-6 border border-neutral-800 bg-neutral-900/50 backdrop-blur-sm overflow-hidden hover:border-neutral-700 transition-colors">
                {/* Hover gradient effect */}
                <motion.div
                  className={`absolute inset-0 bg-gradient-to-br ${stat.color} opacity-0 group-hover:opacity-5 transition-opacity duration-500`}
                />
                
                <div className="relative flex items-start justify-between mb-4">
                  <motion.div
                    className={`w-12 h-12 rounded-xl bg-gradient-to-br ${stat.color} flex items-center justify-center`}
                    whileHover={{ rotate: 5, scale: 1.1 }}
                    transition={{ type: 'spring', stiffness: 300, damping: 15 }}
                  >
                    <stat.icon className="w-6 h-6 text-white" />
                  </motion.div>
                  <div className={`flex items-center gap-1 text-xs font-medium ${
                    stat.changeType === 'positive' ? 'text-emerald-400' : 'text-red-400'
                  }`}>
                    {stat.changeType === 'positive' ? (
                      <ArrowUpRight className="w-3 h-3" />
                    ) : (
                      <ArrowDownRight className="w-3 h-3" />
                    )}
                    {stat.change}
                  </div>
                </div>
                
                <div className="relative">
                  <div className="text-3xl font-bold tracking-tight mb-1">{stat.value}</div>
                  <div className="text-sm text-neutral-500">{stat.title}</div>
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Quick Actions */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, type: 'spring', stiffness: 100, damping: 15 }}
              className="border border-neutral-800 bg-neutral-900/30 backdrop-blur-sm p-6"
            >
              <div className="flex items-center gap-3 mb-6">
                <motion.div
                  className="w-10 h-10 rounded-xl bg-neutral-800 flex items-center justify-center"
                  whileHover={{ rotate: 180, scale: 1.1 }}
                  transition={{ type: 'spring', stiffness: 200, damping: 10 }}
                >
                  <Zap className="w-5 h-5 text-neutral-400" />
                </motion.div>
                <div>
                  <h2 className="text-lg font-semibold">Quick Actions</h2>
                  <p className="text-sm text-neutral-500">Navigate to key areas</p>
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {quickActions.map((action, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.4 + index * 0.05 }}
                    whileHover={{ y: -4, scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <Link to={action.href} params={{}}>
                      <div className="group relative p-4 border border-neutral-800 bg-neutral-900/50 hover:border-neutral-700 transition-all cursor-pointer overflow-hidden">
                        <motion.div
                          className={`absolute inset-0 bg-gradient-to-br ${action.color} opacity-0 group-hover:opacity-5 transition-opacity duration-500`}
                        />
                        <motion.div
                          className={`relative w-10 h-10 rounded-xl bg-gradient-to-br ${action.color} flex items-center justify-center mb-3`}
                          whileHover={{ rotate: 5, scale: 1.1 }}
                          transition={{ type: 'spring', stiffness: 300, damping: 15 }}
                        >
                          <action.icon className="w-5 h-5 text-white" />
                        </motion.div>
                        <div className="relative">
                          <h3 className="font-medium text-sm mb-0.5 group-hover:text-neutral-200 transition-colors">
                            {action.title}
                          </h3>
                          <p className="text-xs text-neutral-500">{action.description}</p>
                        </div>
                        <ChevronRight className="absolute bottom-4 right-4 w-4 h-4 text-neutral-600 opacity-0 group-hover:opacity-100 transition-opacity" />
                      </div>
                    </Link>
                  </motion.div>
                ))}
              </div>
            </motion.div>

            {/* Activity Chart Placeholder */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5, type: 'spring', stiffness: 100, damping: 15 }}
              className="border border-neutral-800 bg-neutral-900/30 backdrop-blur-sm p-6"
            >
              <div className="flex items-center gap-3 mb-6">
                <motion.div
                  className="w-10 h-10 rounded-xl bg-neutral-800 flex items-center justify-center"
                  whileHover={{ rotate: 180, scale: 1.1 }}
                  transition={{ type: 'spring', stiffness: 200, damping: 10 }}
                >
                  <Activity className="w-5 h-5 text-neutral-400" />
                </motion.div>
                <div>
                  <h2 className="text-lg font-semibold">Activity Overview</h2>
                  <p className="text-sm text-neutral-500">Last 30 days performance</p>
                </div>
              </div>

              <div className="h-48 flex items-center justify-center border border-dashed border-neutral-800 rounded-lg">
                <div className="text-center">
                  <TrendingUp className="w-10 h-10 text-neutral-700 mx-auto mb-3" />
                  <p className="text-sm text-neutral-500">Chart integration coming soon</p>
                </div>
              </div>
            </motion.div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Recent Activity */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4, type: 'spring', stiffness: 100, damping: 15 }}
              className="border border-neutral-800 bg-neutral-900/30 backdrop-blur-sm p-6"
            >
              <div className="flex items-center gap-3 mb-5">
                <motion.div
                  className="w-10 h-10 rounded-xl bg-neutral-800 flex items-center justify-center"
                  whileHover={{ rotate: 180, scale: 1.1 }}
                  transition={{ type: 'spring', stiffness: 200, damping: 10 }}
                >
                  <Clock className="w-5 h-5 text-neutral-400" />
                </motion.div>
                <div>
                  <h2 className="text-lg font-semibold">Recent Activity</h2>
                  <p className="text-sm text-neutral-500">Latest updates</p>
                </div>
              </div>

              <div className="space-y-1">
                {recentActivity.map((activity, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.5 + index * 0.05 }}
                    whileHover={{ x: 4, backgroundColor: 'rgba(255,255,255,0.02)' }}
                    className="group flex items-start gap-3 p-3 rounded-lg cursor-pointer transition-colors"
                  >
                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
                      activity.status === 'success' 
                        ? 'bg-emerald-500/10' 
                        : 'bg-amber-500/10'
                    }`}>
                      {activity.status === 'success' ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                      ) : (
                        <AlertCircle className="w-4 h-4 text-amber-400" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate group-hover:text-neutral-200 transition-colors">
                        {activity.action}
                      </p>
                      <p className="text-xs text-neutral-500 truncate">{activity.item}</p>
                    </div>
                    <span className="text-xs text-neutral-600 flex-shrink-0">{activity.time}</span>
                  </motion.div>
                ))}
              </div>
            </motion.div>

            {/* Pro Tip Card */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.6, type: 'spring', stiffness: 100, damping: 15 }}
              whileHover={{ scale: 1.02 }}
              className="relative overflow-hidden border border-neutral-800 bg-gradient-to-br from-blue-500/10 via-cyan-500/5 to-transparent p-6"
            >
              <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-blue-500/20 to-transparent rounded-full -translate-y-1/2 translate-x-1/2 blur-2xl" />
              
              <div className="relative">
                <div className="flex items-center gap-3 mb-4">
                  <motion.div
                    className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center"
                    whileHover={{ rotate: 5, scale: 1.1 }}
                    transition={{ type: 'spring', stiffness: 300, damping: 15 }}
                  >
                    <Zap className="w-5 h-5 text-white" />
                  </motion.div>
                  <div>
                    <h3 className="font-semibold">Pro Tip</h3>
                    <p className="text-xs text-neutral-400">Boost productivity</p>
                  </div>
                </div>
                <p className="text-sm text-neutral-300 leading-relaxed">
                  Use keyboard shortcuts to navigate faster. Press{' '}
                  <kbd className="px-1.5 py-0.5 bg-neutral-800 border border-neutral-700 rounded text-xs font-mono">⌘K</kbd>{' '}
                  to open the command palette.
                </p>
              </div>
            </motion.div>

            {/* Create New */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.7, type: 'spring', stiffness: 100, damping: 15 }}
            >
              <Link to="/documents" params={{}}>
                <motion.div
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="group flex items-center justify-between p-4 border border-dashed border-neutral-700 hover:border-neutral-600 bg-neutral-900/20 cursor-pointer transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-neutral-800 group-hover:bg-neutral-700 flex items-center justify-center transition-colors">
                      <Plus className="w-5 h-5 text-neutral-400" />
                    </div>
                    <div>
                      <p className="font-medium text-sm group-hover:text-neutral-200 transition-colors">Create Document</p>
                      <p className="text-xs text-neutral-500">Start something new</p>
                    </div>
                  </div>
                  <ChevronRight className="w-4 h-4 text-neutral-600 group-hover:text-neutral-400 transition-colors" />
                </motion.div>
              </Link>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  )
}
