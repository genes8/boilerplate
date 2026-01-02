import { createFileRoute } from '@tanstack/react-router'
import { useAuth } from '@/hooks/useAuth'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { 
  LayoutDashboard, 
  Users, 
  FileText, 
  Settings, 
  TrendingUp,
  Clock,
  CheckCircle2,
  AlertCircle,
  LogOut,
  ChevronRight,
  Sparkles
} from 'lucide-react'

export const Route = createFileRoute('/dashboard/' as string)({
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
      title: 'Total Documents', 
      value: '1,234', 
      change: '+12%', 
      changeType: 'positive' as const,
      icon: FileText 
    },
    { 
      title: 'Active Users', 
      value: '56', 
      change: '+3', 
      changeType: 'positive' as const,
      icon: Users 
    },
    { 
      title: 'Pending Tasks', 
      value: '23', 
      change: '-5', 
      changeType: 'positive' as const,
      icon: Clock 
    },
    { 
      title: 'Completed', 
      value: '89%', 
      change: '+2%', 
      changeType: 'positive' as const,
      icon: CheckCircle2 
    },
  ]

  const recentActivity = [
    { action: 'Document uploaded', item: 'Q4 Report.pdf', time: '2 minutes ago', status: 'success' },
    { action: 'User invited', item: 'john@example.com', time: '15 minutes ago', status: 'success' },
    { action: 'Permission updated', item: 'Marketing Team', time: '1 hour ago', status: 'warning' },
    { action: 'Document shared', item: 'Budget 2024.xlsx', time: '2 hours ago', status: 'success' },
    { action: 'Comment added', item: 'Project Proposal', time: '3 hours ago', status: 'success' },
  ]

  const quickActions = [
    { title: 'Upload Document', icon: FileText, color: 'from-blue-500 to-indigo-500' },
    { title: 'Invite User', icon: Users, color: 'from-emerald-500 to-teal-500' },
    { title: 'Create Report', icon: TrendingUp, color: 'from-violet-500 to-purple-500' },
    { title: 'Settings', icon: Settings, color: 'from-amber-500 to-orange-500' },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950">
      <div className="border-b bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm sticky top-0 z-40">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold tracking-tight">Dashboard</h1>
                <p className="text-sm text-muted-foreground">
                  Welcome back, {user?.username || 'User'}
                </p>
              </div>
            </div>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={logout}
              className="text-muted-foreground hover:text-foreground"
            >
              <LogOut className="w-4 h-4 mr-2" />
              Sign out
            </Button>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, index) => (
            <Card key={index} className="relative overflow-hidden border-0 shadow-lg shadow-slate-200/50 dark:shadow-slate-900/50">
              <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-primary/5 to-primary/10 rounded-full -translate-y-1/2 translate-x-1/2" />
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {stat.title}
                </CardTitle>
                <stat.icon className="w-4 h-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold tracking-tight">{stat.value}</div>
                <p className={`text-xs mt-1 ${
                  stat.changeType === 'positive' ? 'text-emerald-600' : 'text-red-600'
                }`}>
                  {stat.change} from last month
                </p>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-8">
            <Card className="border-0 shadow-lg shadow-slate-200/50 dark:shadow-slate-900/50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <LayoutDashboard className="w-5 h-5" />
                  Quick Actions
                </CardTitle>
                <CardDescription>
                  Common tasks and shortcuts
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {quickActions.map((action, index) => (
                    <button
                      key={index}
                      className="group flex flex-col items-center gap-3 p-4 rounded-xl border border-slate-200 dark:border-slate-800 hover:border-transparent hover:shadow-lg transition-all duration-200 bg-white dark:bg-slate-900 hover:scale-105"
                    >
                      <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${action.color} flex items-center justify-center shadow-lg`}>
                        <action.icon className="w-6 h-6 text-white" />
                      </div>
                      <span className="text-sm font-medium text-center">{action.title}</span>
                    </button>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg shadow-slate-200/50 dark:shadow-slate-900/50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5" />
                  Activity Overview
                </CardTitle>
                <CardDescription>
                  Your team's activity for the past 30 days
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-64 flex items-center justify-center border-2 border-dashed border-slate-200 dark:border-slate-800 rounded-xl">
                  <p className="text-muted-foreground">Chart placeholder - integrate with your preferred charting library</p>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="space-y-8">
            <Card className="border-0 shadow-lg shadow-slate-200/50 dark:shadow-slate-900/50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="w-5 h-5" />
                  Recent Activity
                </CardTitle>
                <CardDescription>
                  Latest actions in your workspace
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {recentActivity.map((activity, index) => (
                  <div 
                    key={index} 
                    className="flex items-start gap-3 p-3 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors cursor-pointer group"
                  >
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                      activity.status === 'success' 
                        ? 'bg-emerald-100 dark:bg-emerald-900/30' 
                        : 'bg-amber-100 dark:bg-amber-900/30'
                    }`}>
                      {activity.status === 'success' ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
                      ) : (
                        <AlertCircle className="w-4 h-4 text-amber-600 dark:text-amber-400" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">{activity.action}</p>
                      <p className="text-xs text-muted-foreground truncate">{activity.item}</p>
                      <p className="text-xs text-muted-foreground mt-1">{activity.time}</p>
                    </div>
                    <ChevronRight className="w-4 h-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                  </div>
                ))}
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg shadow-slate-200/50 dark:shadow-slate-900/50 bg-gradient-to-br from-indigo-500 to-violet-600 text-white">
              <CardContent className="pt-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center">
                    <Sparkles className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-semibold">Pro Tip</h3>
                    <p className="text-sm text-white/80">Boost your productivity</p>
                  </div>
                </div>
                <p className="text-sm text-white/90 leading-relaxed">
                  Use keyboard shortcuts to navigate faster. Press <kbd className="px-1.5 py-0.5 bg-white/20 rounded text-xs font-mono">⌘K</kbd> to open the command palette.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
