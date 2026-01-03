import { createFileRoute, Link, useParams } from '@tanstack/react-router'
import { useState, useEffect } from 'react'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { RequireRole } from '@/components/RequireRole'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
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
import { motion, AnimatePresence } from 'motion/react'
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
            <Button className="bg-gradient-to-r from-violet-500 to-purple-500 hover:from-violet-600 hover:to-purple-600">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Return to Dashboard
            </Button>
          </motion.div>
        </Link>
      </motion.div>
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
      setAllPermissions(permissionsData.items)
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
      'Super Admin': 'from-violet-500 to-purple-500',
      Admin: 'from-blue-500 to-cyan-500',
      Manager: 'from-emerald-500 to-teal-500',
      User: 'from-amber-500 to-orange-500',
      Viewer: 'from-neutral-400 to-neutral-500',
    }
    return colors[roleName] || 'from-neutral-500 to-neutral-600'
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

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2,
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

  if (isLoading) {
    return (
      <div className="min-h-screen bg-neutral-950 flex items-center justify-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
        >
          <Loader2 className="w-8 h-8 text-violet-500" />
        </motion.div>
      </div>
    )
  }

  if (!role) {
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
            className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-amber-500/10 flex items-center justify-center"
          >
            <AlertTriangle className="w-8 h-8 text-amber-400" />
          </motion.div>
          <h2 className="text-xl font-bold mb-2">Role Not Found</h2>
          <p className="text-neutral-400 mb-6">
            The role you're looking for doesn't exist.
          </p>
          <Link to="/admin/roles">
            <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
              <Button className="bg-gradient-to-r from-violet-500 to-purple-500 hover:from-violet-600 hover:to-purple-600">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Roles
              </Button>
            </motion.div>
          </Link>
        </motion.div>
      </div>
    )
  }

  const groupedPermissions = groupPermissionsByResource(role.permissions || [])

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
              <Link to="/admin/roles">
                <motion.div
                  whileHover={{ scale: 1.05, x: -2 }}
                  whileTap={{ scale: 0.95 }}
                  className="w-10 h-10 rounded-xl bg-neutral-800 flex items-center justify-center cursor-pointer hover:bg-neutral-700 transition-colors"
                >
                  <ArrowLeft className="w-5 h-5 text-neutral-400" />
                </motion.div>
              </Link>
              <motion.div
                className={`w-12 h-12 rounded-2xl bg-gradient-to-br ${getRoleColor(role.name)} flex items-center justify-center`}
                whileHover={{ rotate: 5, scale: 1.05 }}
                transition={{ type: 'spring', stiffness: 300, damping: 15 }}
              >
                <Shield className="w-6 h-6 text-white" />
              </motion.div>
              <div>
                <div className="flex items-center gap-3">
                  <h1 className="text-2xl font-bold tracking-tight">{role.name}</h1>
                  {role.is_system && (
                    <span className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-violet-500/10 text-violet-400 border border-violet-500/20">
                      <Sparkles className="w-3 h-3 mr-1" />
                      System
                    </span>
                  )}
                </div>
                <p className="text-sm text-neutral-400">
                  Edit role details and permissions
                </p>
              </div>
            </div>
            <AnimatePresence>
              {hasChanges && !role.is_system && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9, x: 20 }}
                  animate={{ opacity: 1, scale: 1, x: 0 }}
                  exit={{ opacity: 0, scale: 0.9, x: 20 }}
                  transition={{ type: 'spring', stiffness: 200, damping: 20 }}
                >
                  <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                    <Button
                      onClick={handleSaveRole}
                      disabled={isSaving}
                      className="bg-gradient-to-r from-violet-500 to-purple-500 hover:from-violet-600 hover:to-purple-600 text-white border-0"
                    >
                      {isSaving ? (
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      ) : (
                        <Save className="w-4 h-4 mr-2" />
                      )}
                      Save Changes
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

        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="grid grid-cols-1 lg:grid-cols-3 gap-8"
        >
          {/* Role Details Card */}
          <motion.div variants={itemVariants} className="lg:col-span-1">
            <div className="border border-neutral-800 bg-neutral-900/50 backdrop-blur-sm overflow-hidden">
              <div className="p-6 border-b border-neutral-800">
                <h2 className="text-lg font-semibold text-neutral-100">Role Details</h2>
                <p className="text-sm text-neutral-500 mt-1">
                  Basic information about this role
                </p>
              </div>
              <div className="p-6 space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="name" className="text-neutral-300">Role Name</Label>
                  <Input
                    id="name"
                    value={editName}
                    onChange={(e) => setEditName(e.target.value)}
                    disabled={role.is_system}
                    className="bg-neutral-800 border-neutral-700 text-neutral-50 placeholder:text-neutral-500 disabled:opacity-50"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="description" className="text-neutral-300">Description</Label>
                  <Textarea
                    id="description"
                    value={editDescription}
                    onChange={(e) => setEditDescription(e.target.value)}
                    disabled={role.is_system}
                    rows={4}
                    className="bg-neutral-800 border-neutral-700 text-neutral-50 placeholder:text-neutral-500 disabled:opacity-50"
                  />
                </div>
                {role.is_system && (
                  <p className="text-sm text-neutral-500">
                    System roles cannot be modified.
                  </p>
                )}
              </div>
            </div>
          </motion.div>

          {/* Permissions Card */}
          <motion.div variants={itemVariants} className="lg:col-span-2">
            <div className="border border-neutral-800 bg-neutral-900/50 backdrop-blur-sm overflow-hidden">
              <div className="p-6 border-b border-neutral-800">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <motion.div
                      whileHover={{ rotate: 5, scale: 1.1 }}
                      transition={{ type: 'spring', stiffness: 300, damping: 15 }}
                      className="w-10 h-10 rounded-xl bg-neutral-800 flex items-center justify-center"
                    >
                      <Key className="w-5 h-5 text-neutral-400" />
                    </motion.div>
                    <div>
                      <h2 className="text-lg font-semibold text-neutral-100">Permissions</h2>
                      <p className="text-sm text-neutral-500">
                        {role.permissions?.length || 0} permissions assigned
                      </p>
                    </div>
                  </div>
                  {!role.is_system && (
                    <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                      <Button
                        variant="outline"
                        onClick={() => setIsPermissionDialogOpen(true)}
                        className="bg-transparent border-neutral-700 text-neutral-300 hover:bg-neutral-800 hover:text-neutral-100 hover:border-neutral-600"
                      >
                        Manage Permissions
                      </Button>
                    </motion.div>
                  )}
                </div>
              </div>
              <div className="p-6">
                {Object.keys(groupedPermissions).length === 0 ? (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="text-center py-12"
                  >
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ delay: 0.2, type: 'spring', stiffness: 200, damping: 15 }}
                      className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-neutral-800 flex items-center justify-center"
                    >
                      <Key className="w-8 h-8 text-neutral-600" />
                    </motion.div>
                    <p className="text-neutral-500">
                      No permissions assigned yet
                    </p>
                  </motion.div>
                ) : (
                  <div className="space-y-6">
                    {Object.entries(groupedPermissions).map(([resource, perms], resourceIndex) => (
                      <motion.div
                        key={resource}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 * resourceIndex }}
                      >
                        <h4 className="text-sm font-semibold text-neutral-400 uppercase tracking-wider mb-3">
                          {resource}
                        </h4>
                        <div className="flex flex-wrap gap-2">
                          {perms.map((perm) => (
                            <motion.span
                              key={perm.id}
                              whileHover={{ scale: 1.05 }}
                              className="inline-flex items-center px-3 py-1.5 rounded-md text-sm font-medium bg-neutral-800 text-neutral-300 border border-neutral-700 group/perm cursor-default"
                            >
                              {perm.action}
                              {perm.scope !== 'all' && (
                                <span className="text-neutral-500 ml-1">
                                  ({perm.scope})
                                </span>
                              )}
                              {!role.is_system && (
                                <motion.button
                                  whileHover={{ scale: 1.2 }}
                                  whileTap={{ scale: 0.9 }}
                                  onClick={() => handleRemovePermission(perm.id)}
                                  className="ml-2 opacity-0 group-hover/perm:opacity-100 transition-opacity hover:text-red-400"
                                  disabled={isSaving}
                                >
                                  <X className="w-3.5 h-3.5" />
                                </motion.button>
                              )}
                            </motion.span>
                          ))}
                        </div>
                      </motion.div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        </motion.div>
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
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-hidden flex flex-col bg-neutral-900 border-neutral-800 text-neutral-50">
        <DialogClose onClose={() => onOpenChange(false)} />
        <DialogHeader>
          <DialogTitle className="text-neutral-50">Manage Permissions</DialogTitle>
          <DialogDescription className="text-neutral-400">
            Select the permissions to assign to this role.
          </DialogDescription>
        </DialogHeader>

        <div className="relative mb-4">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-500" />
          <Input
            placeholder="Search permissions..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-11 bg-neutral-800 border-neutral-700 text-neutral-50 placeholder:text-neutral-500"
          />
        </div>

        <div className="flex-1 overflow-y-auto space-y-6 pr-2">
          {Object.entries(groupedPermissions).map(([resource, perms]) => (
            <div key={resource}>
              <h4 className="text-sm font-semibold text-neutral-400 uppercase tracking-wider mb-3 sticky top-0 bg-neutral-900 py-1">
                {resource}
              </h4>
              <div className="space-y-2">
                {perms.map((perm) => (
                  <motion.label
                    key={perm.id}
                    whileHover={{ x: 4, backgroundColor: 'rgba(255,255,255,0.02)' }}
                    className="flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-colors"
                  >
                    <Checkbox
                      checked={selectedIds.has(perm.id)}
                      onCheckedChange={() => handleToggle(perm.id)}
                      className="border-neutral-600 data-[state=checked]:bg-violet-500 data-[state=checked]:border-violet-500"
                    />
                    <div className="flex-1">
                      <span className="font-medium text-neutral-200">{perm.action}</span>
                      {perm.scope !== 'all' && (
                        <span className="text-neutral-500 ml-2">
                          (scope: {perm.scope})
                        </span>
                      )}
                    </div>
                    {selectedIds.has(perm.id) && (
                      <Check className="w-4 h-4 text-emerald-400" />
                    )}
                  </motion.label>
                ))}
              </div>
            </div>
          ))}
        </div>

        <DialogFooter className="mt-4">
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
              disabled={isSubmitting}
              className="bg-gradient-to-r from-violet-500 to-purple-500 hover:from-violet-600 hover:to-purple-600 text-white border-0"
            >
              {isSubmitting && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
              Save Permissions
            </Button>
          </motion.div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
