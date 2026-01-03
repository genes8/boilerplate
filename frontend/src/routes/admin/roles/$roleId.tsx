import { createFileRoute, Link, useParams } from '@tanstack/react-router'
import { useState, useEffect } from 'react'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { RequireRole } from '@/components/RequireRole'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Textarea } from '@/components/ui/textarea'
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
import { rbacApi, Role, Permission, RoleUpdate } from '@/lib/rbac-api'
import {
  Shield,
  ArrowLeft,
  Save,
  Key,
  Loader2,
  AlertTriangle,
  Sparkles,
  Check,
  X,
  Search,
} from 'lucide-react'

export const Route = createFileRoute('/admin/roles/$roleId')({
  component: RoleDetailsPage,
})

function RoleDetailsPage() {
  return (
    <ProtectedRoute>
      <RequireRole
        roles={['Admin', 'Super Admin']}
        fallback={<AccessDenied />}
      >
        <RoleDetailsContent />
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

function RoleDetailsContent() {
  const { roleId } = useParams({ from: '/admin/roles/$roleId' })
  const [role, setRole] = useState<Role | null>(null)
  const [allPermissions, setAllPermissions] = useState<Permission[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isSaving, setIsSaving] = useState(false)
  const [isPermissionDialogOpen, setIsPermissionDialogOpen] = useState(false)

  const [editName, setEditName] = useState('')
  const [editDescription, setEditDescription] = useState('')
  const [hasChanges, setHasChanges] = useState(false)

  const fetchData = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const [roleData, permissionsData] = await Promise.all([
        rbacApi.getRole(roleId),
        rbacApi.getPermissions(),
      ])
      setRole(roleData)
      setAllPermissions(permissionsData)
      setEditName(roleData.name)
      setEditDescription(roleData.description || '')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch role')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [roleId])

  useEffect(() => {
    if (role) {
      const nameChanged = editName !== role.name
      const descChanged = editDescription !== (role.description || '')
      setHasChanges(nameChanged || descChanged)
    }
  }, [editName, editDescription, role])

  const handleSaveRole = async () => {
    if (!role || !hasChanges) return
    setIsSaving(true)
    try {
      const updateData: RoleUpdate = {}
      if (editName !== role.name) updateData.name = editName
      if (editDescription !== (role.description || ''))
        updateData.description = editDescription

      await rbacApi.updateRole(role.id, updateData)
      await fetchData()
      setHasChanges(false)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update role')
    } finally {
      setIsSaving(false)
    }
  }

  const handleAssignPermissions = async (permissionIds: string[]) => {
    if (!role) return
    setIsSaving(true)
    try {
      await rbacApi.assignPermissions(role.id, { permission_ids: permissionIds })
      await fetchData()
      setIsPermissionDialogOpen(false)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to assign permissions')
    } finally {
      setIsSaving(false)
    }
  }

  const handleRemovePermission = async (permissionId: string) => {
    if (!role) return
    setIsSaving(true)
    try {
      await rbacApi.removePermission(role.id, permissionId)
      await fetchData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to remove permission')
    } finally {
      setIsSaving(false)
    }
  }

  const getRoleColor = (roleName: string) => {
    const colors: Record<string, string> = {
      'Super Admin': 'from-violet-500 to-purple-600',
      Admin: 'from-blue-500 to-indigo-600',
      Manager: 'from-emerald-500 to-teal-600',
      User: 'from-amber-500 to-orange-600',
      Viewer: 'from-slate-400 to-slate-600',
    }
    return colors[roleName] || 'from-gray-500 to-gray-600'
  }

  const groupPermissionsByResource = (permissions: Permission[]) => {
    const grouped: Record<string, Permission[]> = {}
    permissions.forEach((p) => {
      if (!grouped[p.resource]) {
        grouped[p.resource] = []
      }
      grouped[p.resource].push(p)
    })
    return grouped
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-white to-slate-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950">
        <Loader2 className="w-8 h-8 animate-spin text-violet-500" />
      </div>
    )
  }

  if (!role) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-white to-slate-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950">
        <Card className="w-full max-w-md border-0 shadow-2xl">
          <CardContent className="pt-6 text-center">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center">
              <AlertTriangle className="w-8 h-8 text-amber-600 dark:text-amber-400" />
            </div>
            <h2 className="text-xl font-bold mb-2">Role Not Found</h2>
            <p className="text-muted-foreground mb-4">
              The role you're looking for doesn't exist.
            </p>
            <Link to="/admin/roles">
              <Button>Back to Roles</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    )
  }

  const groupedPermissions = groupPermissionsByResource(role.permissions || [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950">
      <div className="border-b bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm sticky top-0 z-40">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link to="/admin/roles">
                <Button variant="ghost" size="icon">
                  <ArrowLeft className="w-5 h-5" />
                </Button>
              </Link>
              <div
                className={`w-10 h-10 rounded-xl bg-gradient-to-br ${getRoleColor(role.name)} flex items-center justify-center shadow-lg`}
              >
                <Shield className="w-5 h-5 text-white" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h1 className="text-xl font-bold tracking-tight">{role.name}</h1>
                  {role.is_system && (
                    <Badge variant="secondary">
                      <Sparkles className="w-3 h-3 mr-1" />
                      System
                    </Badge>
                  )}
                </div>
                <p className="text-sm text-muted-foreground">
                  Edit role details and permissions
                </p>
              </div>
            </div>
            <Button
              onClick={handleSaveRole}
              disabled={!hasChanges || isSaving || role.is_system}
              className="bg-gradient-to-r from-violet-500 to-purple-600 hover:from-violet-600 hover:to-purple-700 shadow-lg shadow-violet-500/25"
            >
              {isSaving ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Save className="w-4 h-4 mr-2" />
              )}
              Save Changes
            </Button>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-6 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-600 dark:text-red-400">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-1">
            <Card className="border-0 shadow-lg shadow-slate-200/50 dark:shadow-slate-900/50">
              <CardHeader>
                <CardTitle>Role Details</CardTitle>
                <CardDescription>
                  Basic information about this role
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Role Name</Label>
                  <Input
                    id="name"
                    value={editName}
                    onChange={(e) => setEditName(e.target.value)}
                    disabled={role.is_system}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    value={editDescription}
                    onChange={(e) => setEditDescription(e.target.value)}
                    disabled={role.is_system}
                    rows={4}
                  />
                </div>
                {role.is_system && (
                  <p className="text-sm text-muted-foreground">
                    System roles cannot be modified.
                  </p>
                )}
              </CardContent>
            </Card>
          </div>

          <div className="lg:col-span-2">
            <Card className="border-0 shadow-lg shadow-slate-200/50 dark:shadow-slate-900/50">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="flex items-center gap-2">
                      <Key className="w-5 h-5" />
                      Permissions
                    </CardTitle>
                    <CardDescription>
                      {role.permissions?.length || 0} permissions assigned
                    </CardDescription>
                  </div>
                  {!role.is_system && (
                    <Button
                      variant="outline"
                      onClick={() => setIsPermissionDialogOpen(true)}
                    >
                      Manage Permissions
                    </Button>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                {Object.keys(groupedPermissions).length === 0 ? (
                  <div className="text-center py-8">
                    <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center">
                      <Key className="w-6 h-6 text-slate-400" />
                    </div>
                    <p className="text-muted-foreground">
                      No permissions assigned yet
                    </p>
                  </div>
                ) : (
                  <div className="space-y-6">
                    {Object.entries(groupedPermissions).map(([resource, perms]) => (
                      <div key={resource}>
                        <h4 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-3">
                          {resource}
                        </h4>
                        <div className="flex flex-wrap gap-2">
                          {perms.map((perm) => (
                            <Badge
                              key={perm.id}
                              variant="secondary"
                              className="group cursor-default"
                            >
                              {perm.action}
                              {perm.scope !== 'all' && (
                                <span className="text-muted-foreground ml-1">
                                  ({perm.scope})
                                </span>
                              )}
                              {!role.is_system && (
                                <button
                                  onClick={() => handleRemovePermission(perm.id)}
                                  className="ml-1 opacity-0 group-hover:opacity-100 transition-opacity"
                                  disabled={isSaving}
                                >
                                  <X className="w-3 h-3" />
                                </button>
                              )}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      <PermissionAssignDialog
        open={isPermissionDialogOpen}
        onOpenChange={setIsPermissionDialogOpen}
        allPermissions={allPermissions}
        assignedPermissions={role.permissions || []}
        onSubmit={handleAssignPermissions}
        isSubmitting={isSaving}
      />
    </div>
  )
}

interface PermissionAssignDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  allPermissions: Permission[]
  assignedPermissions: Permission[]
  onSubmit: (permissionIds: string[]) => Promise<void>
  isSubmitting: boolean
}

function PermissionAssignDialog({
  open,
  onOpenChange,
  allPermissions,
  assignedPermissions,
  onSubmit,
  isSubmitting,
}: PermissionAssignDialogProps) {
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    if (open) {
      setSelectedIds(new Set(assignedPermissions.map((p) => p.id)))
    }
  }, [open, assignedPermissions])

  const handleToggle = (id: string) => {
    const newSet = new Set(selectedIds)
    if (newSet.has(id)) {
      newSet.delete(id)
    } else {
      newSet.add(id)
    }
    setSelectedIds(newSet)
  }

  const handleSubmit = async () => {
    await onSubmit(Array.from(selectedIds))
  }

  const filteredPermissions = allPermissions.filter(
    (p) =>
      p.resource.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.action.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const groupedPermissions = filteredPermissions.reduce(
    (acc, p) => {
      if (!acc[p.resource]) acc[p.resource] = []
      acc[p.resource].push(p)
      return acc
    },
    {} as Record<string, Permission[]>
  )

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-hidden flex flex-col">
        <DialogClose onClose={() => onOpenChange(false)} />
        <DialogHeader>
          <DialogTitle>Manage Permissions</DialogTitle>
          <DialogDescription>
            Select the permissions to assign to this role.
          </DialogDescription>
        </DialogHeader>

        <div className="relative mb-4">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder="Search permissions..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>

        <div className="flex-1 overflow-y-auto space-y-6 pr-2">
          {Object.entries(groupedPermissions).map(([resource, perms]) => (
            <div key={resource}>
              <h4 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-3 sticky top-0 bg-background py-1">
                {resource}
              </h4>
              <div className="space-y-2">
                {perms.map((perm) => (
                  <label
                    key={perm.id}
                    className="flex items-center gap-3 p-2 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800/50 cursor-pointer"
                  >
                    <Checkbox
                      checked={selectedIds.has(perm.id)}
                      onCheckedChange={() => handleToggle(perm.id)}
                    />
                    <div className="flex-1">
                      <span className="font-medium">{perm.action}</span>
                      {perm.scope !== 'all' && (
                        <span className="text-muted-foreground ml-2">
                          (scope: {perm.scope})
                        </span>
                      )}
                    </div>
                    {selectedIds.has(perm.id) && (
                      <Check className="w-4 h-4 text-emerald-500" />
                    )}
                  </label>
                ))}
              </div>
            </div>
          ))}
        </div>

        <DialogFooter className="mt-4">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={handleSubmit} disabled={isSubmitting}>
            {isSubmitting && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
            Save Permissions
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
