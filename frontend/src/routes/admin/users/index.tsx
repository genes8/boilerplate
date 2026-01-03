import { createFileRoute, Link } from '@tanstack/react-router'
import { useState, useEffect } from 'react'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { RequireRole } from '@/components/RequireRole'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Checkbox } from '@/components/ui/checkbox'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
  DialogClose,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { rbacApi, Role, UserWithRoles } from '@/lib/rbac-api'
import { motion, AnimatePresence } from 'motion/react'
import {
  Users,
  Search,
  Loader2,
  AlertTriangle,
  Shield,
  Plus,
  X,
  Check,
  Mail,
  Calendar,
  ChevronLeft,
  ChevronRight,
  UserCog,
  ArrowLeft,
} from 'lucide-react'

export const Route = createFileRoute('/admin/users/')({
  component: UsersPage,
})

function UsersPage() {
  return (
    <ProtectedRoute>
      <RequireRole
        roles={['Admin', 'Super Admin']}
        fallback={<AccessDenied />}
      >
        <UsersContent />
      </RequireRole>
    </ProtectedRoute>
  )
}

function AccessDenied() {
  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-50 flex items-center justify-center">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ type: 'spring', stiffness: 100, damping: 15 }}
        className="w-full max-w-md border border-neutral-800 bg-neutral-900/50 backdrop-blur-sm p-8 text-center"
      >
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, type: 'spring', stiffness: 200, damping: 15 }}
          className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-red-500/10 flex items-center justify-center"
        >
          <AlertTriangle className="w-8 h-8 text-red-400" />
        </motion.div>
        <h2 className="text-xl font-bold mb-2">Access Denied</h2>
        <p className="text-neutral-400 mb-6">
          You don't have permission to access this page.
        </p>
        <Link to="/dashboard">
          <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
            <Button className="bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Return to Dashboard
            </Button>
          </motion.div>
        </Link>
      </motion.div>
    </div>
  )
}

function UsersContent() {
  const [users, setUsers] = useState<UserWithRoles[]>([])
  const [roles, setRoles] = useState<Role[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const limit = 10

  const [selectedUser, setSelectedUser] = useState<UserWithRoles | null>(null)
  const [isRoleDialogOpen, setIsRoleDialogOpen] = useState(false)
  const [isBulkDialogOpen, setIsBulkDialogOpen] = useState(false)
  const [selectedUserIds, setSelectedUserIds] = useState<Set<string>>(new Set())
  const [isSubmitting, setIsSubmitting] = useState(false)

  const fetchData = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const [usersResponse, rolesResponse] = await Promise.all([
        rbacApi.getUsers({
          skip: (page - 1) * limit,
          limit,
          search: searchQuery || undefined,
        }),
        rbacApi.getRoles(),
      ])
      setUsers(usersResponse.items)
      setTotal(usersResponse.total)
      setRoles(rolesResponse.items)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch data')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [page, searchQuery])

  const handleAssignRole = async (userId: string, roleId: string) => {
    setIsSubmitting(true)
    try {
      await rbacApi.assignUserRole(userId, { role_id: roleId })
      await fetchData()
      setIsRoleDialogOpen(false)
      setSelectedUser(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to assign role')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleRemoveRole = async (userId: string, roleId: string) => {
    setIsSubmitting(true)
    try {
      await rbacApi.removeUserRole(userId, roleId)
      await fetchData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to remove role')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleBulkAssign = async (roleId: string) => {
    setIsSubmitting(true)
    try {
      await rbacApi.bulkAssignRole({
        user_ids: Array.from(selectedUserIds),
        role_id: roleId,
      })
      await fetchData()
      setIsBulkDialogOpen(false)
      setSelectedUserIds(new Set())
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to bulk assign role')
    } finally {
      setIsSubmitting(false)
    }
  }

  const toggleUserSelection = (userId: string) => {
    const newSet = new Set(selectedUserIds)
    if (newSet.has(userId)) {
      newSet.delete(userId)
    } else {
      newSet.add(userId)
    }
    setSelectedUserIds(newSet)
  }

  const toggleAllUsers = () => {
    if (selectedUserIds.size === users.length) {
      setSelectedUserIds(new Set())
    } else {
      setSelectedUserIds(new Set(users.map((u) => u.id)))
    }
  }

  const totalPages = Math.ceil(total / limit)

  const getRoleColor = (roleName: string) => {
    const colors: Record<string, string> = {
      'Super Admin': 'from-violet-500 to-purple-500',
      Admin: 'from-blue-500 to-cyan-500',
      Manager: 'from-emerald-500 to-teal-500',
      User: 'from-amber-500 to-orange-500',
      Viewer: 'from-neutral-400 to-neutral-500',
    }
    return colors[roleName] || 'from-neutral-500 to-neutral-600'
  }

  const getRoleBgColor = (roleName: string) => {
    const colors: Record<string, string> = {
      'Super Admin': 'bg-violet-500/10 text-violet-400 border-violet-500/20',
      Admin: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
      Manager: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
      User: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
      Viewer: 'bg-neutral-500/10 text-neutral-400 border-neutral-500/20',
    }
    return colors[roleName] || 'bg-neutral-500/10 text-neutral-400 border-neutral-500/20'
  }

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.05,
        delayChildren: 0.1,
      },
    },
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
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
              <Link to="/dashboard">
                <motion.div
                  whileHover={{ scale: 1.05, x: -2 }}
                  whileTap={{ scale: 0.95 }}
                  className="w-10 h-10 rounded-xl bg-neutral-800 flex items-center justify-center cursor-pointer hover:bg-neutral-700 transition-colors"
                >
                  <ArrowLeft className="w-5 h-5 text-neutral-400" />
                </motion.div>
              </Link>
              <motion.div
                className="w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center"
                whileHover={{ rotate: 5, scale: 1.05 }}
                transition={{ type: 'spring', stiffness: 300, damping: 15 }}
              >
                <Users className="w-6 h-6 text-white" />
              </motion.div>
              <div>
                <h1 className="text-2xl font-bold tracking-tight">User Management</h1>
                <p className="text-sm text-neutral-400">
                  Manage user roles and permissions
                </p>
              </div>
            </div>
            <AnimatePresence>
              {selectedUserIds.size > 0 && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9, x: 20 }}
                  animate={{ opacity: 1, scale: 1, x: 0 }}
                  exit={{ opacity: 0, scale: 0.9, x: 20 }}
                  transition={{ type: 'spring', stiffness: 200, damping: 20 }}
                >
                  <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                    <Button
                      onClick={() => setIsBulkDialogOpen(true)}
                      className="bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white border-0"
                    >
                      <UserCog className="w-4 h-4 mr-2" />
                      Assign Role to {selectedUserIds.size} Users
                    </Button>
                  </motion.div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </motion.div>

      <div className="relative z-10 max-w-7xl mx-auto px-6 py-8">
        {/* Error message */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 flex items-center gap-3"
            >
              <AlertTriangle className="w-5 h-5 flex-shrink-0" />
              {error}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Search and Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6"
        >
          <div className="relative w-full sm:w-80">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-500" />
            <Input
              placeholder="Search users..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value)
                setPage(1)
              }}
              className="pl-11 bg-neutral-900/50 border-neutral-800 text-neutral-50 placeholder:text-neutral-500 focus:border-blue-500/50 focus:ring-blue-500/20"
            />
          </div>
          <div className="flex items-center gap-3 text-sm text-neutral-400">
            <span className="px-3 py-1.5 bg-neutral-800/50 border border-neutral-700 rounded-lg">
              {total} users total
            </span>
          </div>
        </motion.div>

        {/* Users Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="border border-neutral-800 bg-neutral-900/30 backdrop-blur-sm overflow-hidden"
        >
          {isLoading ? (
            <div className="flex items-center justify-center py-20">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
              >
                <Loader2 className="w-8 h-8 text-blue-500" />
              </motion.div>
            </div>
          ) : users.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="text-center py-20"
            >
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.2, type: 'spring', stiffness: 200, damping: 15 }}
                className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-neutral-800 flex items-center justify-center"
              >
                <Users className="w-10 h-10 text-neutral-600" />
              </motion.div>
              <h3 className="text-xl font-semibold mb-2">No users found</h3>
              <p className="text-neutral-500">
                {searchQuery
                  ? 'Try adjusting your search query'
                  : 'No users in the system yet'}
              </p>
            </motion.div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-neutral-800 bg-neutral-900/50">
                      <th className="text-left p-4 w-12">
                        <Checkbox
                          checked={selectedUserIds.size === users.length && users.length > 0}
                          onCheckedChange={toggleAllUsers}
                          className="border-neutral-600 data-[state=checked]:bg-blue-500 data-[state=checked]:border-blue-500"
                        />
                      </th>
                      <th className="text-left p-4 font-medium text-sm text-neutral-400">
                        User
                      </th>
                      <th className="text-left p-4 font-medium text-sm text-neutral-400">
                        Status
                      </th>
                      <th className="text-left p-4 font-medium text-sm text-neutral-400">
                        Roles
                      </th>
                      <th className="text-left p-4 font-medium text-sm text-neutral-400">
                        Joined
                      </th>
                      <th className="text-right p-4 font-medium text-sm text-neutral-400">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <motion.tbody
                    variants={containerVariants}
                    initial="hidden"
                    animate="visible"
                  >
                    {users.map((user) => (
                      <motion.tr
                        key={user.id}
                        variants={itemVariants}
                        className="border-b border-neutral-800/50 last:border-0 hover:bg-neutral-800/30 transition-colors group"
                      >
                        <td className="p-4">
                          <Checkbox
                            checked={selectedUserIds.has(user.id)}
                            onCheckedChange={() => toggleUserSelection(user.id)}
                            className="border-neutral-600 data-[state=checked]:bg-blue-500 data-[state=checked]:border-blue-500"
                          />
                        </td>
                        <td className="p-4">
                          <div className="flex items-center gap-3">
                            <motion.div
                              whileHover={{ scale: 1.1 }}
                              className={`w-10 h-10 rounded-xl bg-gradient-to-br ${getRoleColor(user.roles[0]?.role_name || 'User')} flex items-center justify-center font-semibold text-white text-sm`}
                            >
                              {user.username.charAt(0).toUpperCase()}
                            </motion.div>
                            <div>
                              <p className="font-medium text-neutral-100">{user.username}</p>
                              <p className="text-sm text-neutral-500 flex items-center gap-1">
                                <Mail className="w-3 h-3" />
                                {user.email}
                              </p>
                            </div>
                          </div>
                        </td>
                        <td className="p-4">
                          <div className="flex items-center gap-2">
                            {user.is_active ? (
                              <span className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                                Active
                              </span>
                            ) : (
                              <span className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-neutral-500/10 text-neutral-400 border border-neutral-500/20">
                                Inactive
                              </span>
                            )}
                            {user.is_verified && (
                              <span className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-blue-500/10 text-blue-400 border border-blue-500/20">
                                <Check className="w-3 h-3 mr-1" />
                                Verified
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="p-4">
                          <div className="flex flex-wrap gap-1.5">
                            {user.roles.length === 0 ? (
                              <span className="text-sm text-neutral-500">
                                No roles
                              </span>
                            ) : (
                              user.roles.map((role) => (
                                <motion.span
                                  key={role.role_id}
                                  whileHover={{ scale: 1.05 }}
                                  className={`inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium border ${getRoleBgColor(role.role_name)} group/role cursor-default`}
                                >
                                  <Shield className="w-3 h-3 mr-1" />
                                  {role.role_name}
                                  <motion.button
                                    whileHover={{ scale: 1.2 }}
                                    whileTap={{ scale: 0.9 }}
                                    onClick={() => handleRemoveRole(user.id, role.role_id)}
                                    className="ml-1.5 opacity-0 group-hover/role:opacity-100 transition-opacity hover:text-red-400"
                                    disabled={isSubmitting}
                                  >
                                    <X className="w-3 h-3" />
                                  </motion.button>
                                </motion.span>
                              ))
                            )}
                          </div>
                        </td>
                        <td className="p-4">
                          <p className="text-sm text-neutral-500 flex items-center gap-1.5">
                            <Calendar className="w-3.5 h-3.5" />
                            {new Date(user.created_at).toLocaleDateString()}
                          </p>
                        </td>
                        <td className="p-4 text-right">
                          <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => {
                                setSelectedUser(user)
                                setIsRoleDialogOpen(true)
                              }}
                              className="bg-transparent border-neutral-700 text-neutral-300 hover:bg-neutral-800 hover:text-neutral-100 hover:border-neutral-600"
                            >
                              <Plus className="w-4 h-4 mr-1" />
                              Add Role
                            </Button>
                          </motion.div>
                        </td>
                      </motion.tr>
                    ))}
                  </motion.tbody>
                </table>
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="border-t border-neutral-800 p-4 flex items-center justify-between">
                  <p className="text-sm text-neutral-500">
                    Showing {(page - 1) * limit + 1} to{' '}
                    {Math.min(page * limit, total)} of {total} users
                  </p>
                  <div className="flex items-center gap-2">
                    <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setPage((p) => Math.max(1, p - 1))}
                        disabled={page === 1}
                        className="bg-transparent border-neutral-700 text-neutral-400 hover:bg-neutral-800 hover:text-neutral-100 disabled:opacity-30"
                      >
                        <ChevronLeft className="w-4 h-4" />
                      </Button>
                    </motion.div>
                    <span className="text-sm text-neutral-400 px-3">
                      Page {page} of {totalPages}
                    </span>
                    <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                        disabled={page === totalPages}
                        className="bg-transparent border-neutral-700 text-neutral-400 hover:bg-neutral-800 hover:text-neutral-100 disabled:opacity-30"
                      >
                        <ChevronRight className="w-4 h-4" />
                      </Button>
                    </motion.div>
                  </div>
                </div>
              )}
            </>
          )}
        </motion.div>
      </div>

      <AssignRoleDialog
        open={isRoleDialogOpen}
        onOpenChange={setIsRoleDialogOpen}
        user={selectedUser}
        roles={roles}
        onAssign={handleAssignRole}
        isSubmitting={isSubmitting}
      />

      <BulkAssignDialog
        open={isBulkDialogOpen}
        onOpenChange={setIsBulkDialogOpen}
        roles={roles}
        selectedCount={selectedUserIds.size}
        onAssign={handleBulkAssign}
        isSubmitting={isSubmitting}
      />
    </div>
  )
}

interface AssignRoleDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  user: UserWithRoles | null
  roles: Role[]
  onAssign: (userId: string, roleId: string) => Promise<void>
  isSubmitting: boolean
}

function AssignRoleDialog({
  open,
  onOpenChange,
  user,
  roles,
  onAssign,
  isSubmitting,
}: AssignRoleDialogProps) {
  const [selectedRoleId, setSelectedRoleId] = useState('')

  const availableRoles = roles.filter(
    (role) => !user?.roles.some((r) => r.role_id === role.id)
  )

  const handleSubmit = async () => {
    if (!user || !selectedRoleId) return
    await onAssign(user.id, selectedRoleId)
    setSelectedRoleId('')
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-neutral-900 border-neutral-800 text-neutral-50">
        <DialogClose onClose={() => onOpenChange(false)} />
        <DialogHeader>
          <DialogTitle className="text-neutral-50">Assign Role to User</DialogTitle>
          <DialogDescription className="text-neutral-400">
            Select a role to assign to {user?.username}
          </DialogDescription>
        </DialogHeader>

        <div className="py-4">
          {availableRoles.length === 0 ? (
            <p className="text-center text-neutral-500 py-4">
              This user already has all available roles.
            </p>
          ) : (
            <Select value={selectedRoleId} onValueChange={setSelectedRoleId}>
              <SelectTrigger className="bg-neutral-800 border-neutral-700 text-neutral-50">
                <SelectValue placeholder="Select a role..." />
              </SelectTrigger>
              <SelectContent className="bg-neutral-800 border-neutral-700">
                {availableRoles.map((role) => (
                  <SelectItem key={role.id} value={role.id} className="text-neutral-50 focus:bg-neutral-700 focus:text-neutral-50">
                    <div className="flex items-center gap-2">
                      <Shield className="w-4 h-4" />
                      {role.name}
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
        </div>

        <DialogFooter>
          <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
            <Button 
              variant="outline" 
              onClick={() => onOpenChange(false)}
              className="bg-transparent border-neutral-700 text-neutral-300 hover:bg-neutral-800 hover:text-neutral-100"
            >
              Cancel
            </Button>
          </motion.div>
          <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
            <Button
              onClick={handleSubmit}
              disabled={isSubmitting || !selectedRoleId}
              className="bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white border-0"
            >
              {isSubmitting && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
              Assign Role
            </Button>
          </motion.div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

interface BulkAssignDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  roles: Role[]
  selectedCount: number
  onAssign: (roleId: string) => Promise<void>
  isSubmitting: boolean
}

function BulkAssignDialog({
  open,
  onOpenChange,
  roles,
  selectedCount,
  onAssign,
  isSubmitting,
}: BulkAssignDialogProps) {
  const [selectedRoleId, setSelectedRoleId] = useState('')

  const handleSubmit = async () => {
    if (!selectedRoleId) return
    await onAssign(selectedRoleId)
    setSelectedRoleId('')
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-neutral-900 border-neutral-800 text-neutral-50">
        <DialogClose onClose={() => onOpenChange(false)} />
        <DialogHeader>
          <DialogTitle className="text-neutral-50">Bulk Assign Role</DialogTitle>
          <DialogDescription className="text-neutral-400">
            Assign a role to {selectedCount} selected users
          </DialogDescription>
        </DialogHeader>

        <div className="py-4">
          <Select value={selectedRoleId} onValueChange={setSelectedRoleId}>
            <SelectTrigger className="bg-neutral-800 border-neutral-700 text-neutral-50">
              <SelectValue placeholder="Select a role..." />
            </SelectTrigger>
            <SelectContent className="bg-neutral-800 border-neutral-700">
              {roles.map((role) => (
                <SelectItem key={role.id} value={role.id} className="text-neutral-50 focus:bg-neutral-700 focus:text-neutral-50">
                  <div className="flex items-center gap-2">
                    <Shield className="w-4 h-4" />
                    {role.name}
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <DialogFooter>
          <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
            <Button 
              variant="outline" 
              onClick={() => onOpenChange(false)}
              className="bg-transparent border-neutral-700 text-neutral-300 hover:bg-neutral-800 hover:text-neutral-100"
            >
              Cancel
            </Button>
          </motion.div>
          <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
            <Button
              onClick={handleSubmit}
              disabled={isSubmitting || !selectedRoleId}
              className="bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white border-0"
            >
              {isSubmitting && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
              Assign to {selectedCount} Users
            </Button>
          </motion.div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
