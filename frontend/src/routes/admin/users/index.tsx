import { createFileRoute, Link } from '@tanstack/react-router'
import { useState, useEffect } from 'react'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { RequireRole } from '@/components/RequireRole'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
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
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-white to-slate-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950">
      <Card className="w-full max-w-md border-0 shadow-2xl">
        <CardContent className="pt-6 text-center">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
            <AlertTriangle className="w-8 h-8 text-red-600 dark:text-red-400" />
          </div>
          <h2 className="text-xl font-bold mb-2">Access Denied</h2>
          <p className="text-muted-foreground mb-4">
            You don't have permission to access this page.
          </p>
          <Link to="/dashboard">
            <Button>Return to Dashboard</Button>
          </Link>
        </CardContent>
      </Card>
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
      'Super Admin': 'bg-violet-100 text-violet-800 dark:bg-violet-900/30 dark:text-violet-400',
      Admin: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
      Manager: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400',
      User: 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400',
      Viewer: 'bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-400',
    }
    return colors[roleName] || 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-400'
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950">
      <div className="border-b bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm sticky top-0 z-40">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-blue-500/25">
                <Users className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold tracking-tight">User Management</h1>
                <p className="text-sm text-muted-foreground">
                  Manage user roles and permissions
                </p>
              </div>
            </div>
            {selectedUserIds.size > 0 && (
              <Button
                onClick={() => setIsBulkDialogOpen(true)}
                className="bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 shadow-lg shadow-blue-500/25"
              >
                <UserCog className="w-4 h-4 mr-2" />
                Assign Role to {selectedUserIds.size} Users
              </Button>
            )}
          </div>
        </div>
      </div>

      <div className="container mx-auto px-6 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-600 dark:text-red-400">
            {error}
          </div>
        )}

        <div className="mb-6">
          <div className="relative max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Search users by email or username..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value)
                setPage(1)
              }}
              className="pl-10"
            />
          </div>
        </div>

        <Card className="border-0 shadow-lg shadow-slate-200/50 dark:shadow-slate-900/50">
          <CardHeader className="border-b">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Users</CardTitle>
                <CardDescription>
                  {total} users total
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            {isLoading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
              </div>
            ) : users.length === 0 ? (
              <div className="text-center py-12">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center">
                  <Users className="w-8 h-8 text-slate-400" />
                </div>
                <h3 className="text-lg font-semibold mb-2">No users found</h3>
                <p className="text-muted-foreground">
                  {searchQuery
                    ? 'Try adjusting your search query'
                    : 'No users in the system yet'}
                </p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b bg-slate-50/50 dark:bg-slate-800/50">
                      <th className="text-left p-4 w-12">
                        <Checkbox
                          checked={selectedUserIds.size === users.length && users.length > 0}
                          onCheckedChange={toggleAllUsers}
                        />
                      </th>
                      <th className="text-left p-4 font-medium text-sm text-muted-foreground">
                        User
                      </th>
                      <th className="text-left p-4 font-medium text-sm text-muted-foreground">
                        Status
                      </th>
                      <th className="text-left p-4 font-medium text-sm text-muted-foreground">
                        Roles
                      </th>
                      <th className="text-left p-4 font-medium text-sm text-muted-foreground">
                        Joined
                      </th>
                      <th className="text-right p-4 font-medium text-sm text-muted-foreground">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map((user) => (
                      <tr
                        key={user.id}
                        className="border-b last:border-0 hover:bg-slate-50/50 dark:hover:bg-slate-800/50 transition-colors"
                      >
                        <td className="p-4">
                          <Checkbox
                            checked={selectedUserIds.has(user.id)}
                            onCheckedChange={() => toggleUserSelection(user.id)}
                          />
                        </td>
                        <td className="p-4">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-slate-200 to-slate-300 dark:from-slate-700 dark:to-slate-600 flex items-center justify-center font-semibold text-slate-600 dark:text-slate-300">
                              {user.username.charAt(0).toUpperCase()}
                            </div>
                            <div>
                              <p className="font-medium">{user.username}</p>
                              <p className="text-sm text-muted-foreground flex items-center gap-1">
                                <Mail className="w-3 h-3" />
                                {user.email}
                              </p>
                            </div>
                          </div>
                        </td>
                        <td className="p-4">
                          <div className="flex items-center gap-2">
                            {user.is_active ? (
                              <Badge variant="success">Active</Badge>
                            ) : (
                              <Badge variant="secondary">Inactive</Badge>
                            )}
                            {user.is_verified && (
                              <Badge variant="info">
                                <Check className="w-3 h-3 mr-1" />
                                Verified
                              </Badge>
                            )}
                          </div>
                        </td>
                        <td className="p-4">
                          <div className="flex flex-wrap gap-1">
                            {user.roles.length === 0 ? (
                              <span className="text-sm text-muted-foreground">
                                No roles
                              </span>
                            ) : (
                              user.roles.map((role) => (
                                <Badge
                                  key={role.role_id}
                                  className={`${getRoleColor(role.role_name)} group`}
                                >
                                  <Shield className="w-3 h-3 mr-1" />
                                  {role.role_name}
                                  <button
                                    onClick={() =>
                                      handleRemoveRole(user.id, role.role_id)
                                    }
                                    className="ml-1 opacity-0 group-hover:opacity-100 transition-opacity"
                                    disabled={isSubmitting}
                                  >
                                    <X className="w-3 h-3" />
                                  </button>
                                </Badge>
                              ))
                            )}
                          </div>
                        </td>
                        <td className="p-4">
                          <p className="text-sm text-muted-foreground flex items-center gap-1">
                            <Calendar className="w-3 h-3" />
                            {new Date(user.created_at).toLocaleDateString()}
                          </p>
                        </td>
                        <td className="p-4 text-right">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setSelectedUser(user)
                              setIsRoleDialogOpen(true)
                            }}
                          >
                            <Plus className="w-4 h-4 mr-1" />
                            Add Role
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>

          {totalPages > 1 && (
            <div className="border-t p-4 flex items-center justify-between">
              <p className="text-sm text-muted-foreground">
                Showing {(page - 1) * limit + 1} to{' '}
                {Math.min(page * limit, total)} of {total} users
              </p>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                >
                  <ChevronLeft className="w-4 h-4" />
                </Button>
                <span className="text-sm">
                  Page {page} of {totalPages}
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                >
                  <ChevronRight className="w-4 h-4" />
                </Button>
              </div>
            </div>
          )}
        </Card>
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
      <DialogContent>
        <DialogClose onClose={() => onOpenChange(false)} />
        <DialogHeader>
          <DialogTitle>Assign Role to User</DialogTitle>
          <DialogDescription>
            Select a role to assign to {user?.username}
          </DialogDescription>
        </DialogHeader>

        <div className="py-4">
          {availableRoles.length === 0 ? (
            <p className="text-center text-muted-foreground py-4">
              This user already has all available roles.
            </p>
          ) : (
            <Select value={selectedRoleId} onValueChange={setSelectedRoleId}>
              <SelectTrigger>
                <SelectValue placeholder="Select a role..." />
              </SelectTrigger>
              <SelectContent>
                {availableRoles.map((role) => (
                  <SelectItem key={role.id} value={role.id}>
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
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={isSubmitting || !selectedRoleId}
          >
            {isSubmitting && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
            Assign Role
          </Button>
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
      <DialogContent>
        <DialogClose onClose={() => onOpenChange(false)} />
        <DialogHeader>
          <DialogTitle>Bulk Assign Role</DialogTitle>
          <DialogDescription>
            Assign a role to {selectedCount} selected users
          </DialogDescription>
        </DialogHeader>

        <div className="py-4">
          <Select value={selectedRoleId} onValueChange={setSelectedRoleId}>
            <SelectTrigger>
              <SelectValue placeholder="Select a role..." />
            </SelectTrigger>
            <SelectContent>
              {roles.map((role) => (
                <SelectItem key={role.id} value={role.id}>
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
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={isSubmitting || !selectedRoleId}
          >
            {isSubmitting && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
            Assign to {selectedCount} Users
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
