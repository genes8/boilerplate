import { createFileRoute, Link } from '@tanstack/react-router'
import { useState, useEffect } from 'react'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { RequireRole } from '@/components/RequireRole'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
  DialogClose,
} from '@/components/ui/dialog'
import { rbacApi, Role, RoleCreate } from '@/lib/rbac-api'
import { motion, AnimatePresence } from 'motion/react'
import {
  Shield,
  Plus,
  Pencil,
  Trash2,
  Key,
  ChevronRight,
  Search,
  Loader2,
  AlertTriangle,
  Sparkles,
  ArrowLeft,
} from 'lucide-react'

export const Route = createFileRoute('/admin/roles/')({
  component: RolesPage,
})

function RolesPage() {
  return (
    <ProtectedRoute>
      <RequireRole
        roles={['Admin', 'Super Admin']}
        fallback={<AccessDenied />}
      >
        <RolesContent />
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

function RolesContent() {
  const [roles, setRoles] = useState<Role[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const [selectedRole, setSelectedRole] = useState<Role | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const fetchRoles = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await rbacApi.getRoles()
      setRoles(response.items)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch roles')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchRoles()
  }, [])

  const handleCreateRole = async (data: RoleCreate) => {
    setIsSubmitting(true)
    try {
      await rbacApi.createRole(data)
      await fetchRoles()
      setIsCreateDialogOpen(false)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create role')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleDeleteRole = async () => {
    if (!selectedRole) return
    setIsSubmitting(true)
    try {
      await rbacApi.deleteRole(selectedRole.id)
      await fetchRoles()
      setIsDeleteDialogOpen(false)
      setSelectedRole(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete role')
    } finally {
      setIsSubmitting(false)
    }
  }

  const filteredRoles = roles.filter(
    (role) =>
      role.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      role.description?.toLowerCase().includes(searchQuery.toLowerCase())
  )

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
                className="w-12 h-12 rounded-2xl bg-gradient-to-br from-violet-500 to-purple-500 flex items-center justify-center"
                whileHover={{ rotate: 5, scale: 1.05 }}
                transition={{ type: 'spring', stiffness: 300, damping: 15 }}
              >
                <Shield className="w-6 h-6 text-white" />
              </motion.div>
              <div>
                <h1 className="text-2xl font-bold tracking-tight">Role Management</h1>
                <p className="text-sm text-neutral-400">
                  Manage roles and their permissions
                </p>
              </div>
            </div>
            <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
              <Button
                onClick={() => setIsCreateDialogOpen(true)}
                className="bg-gradient-to-r from-violet-500 to-purple-500 hover:from-violet-600 hover:to-purple-600 text-white border-0"
              >
                <Plus className="w-4 h-4 mr-2" />
                Create Role
              </Button>
            </motion.div>
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

        {/* Search */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-8"
        >
          <div className="relative w-full sm:w-80">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-500" />
            <Input
              placeholder="Search roles..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-11 bg-neutral-900/50 border-neutral-800 text-neutral-50 placeholder:text-neutral-500 focus:border-violet-500/50 focus:ring-violet-500/20"
            />
          </div>
          <div className="flex items-center gap-3 text-sm text-neutral-400">
            <span className="px-3 py-1.5 bg-neutral-800/50 border border-neutral-700 rounded-lg">
              {filteredRoles.length} roles
            </span>
          </div>
        </motion.div>

        {isLoading ? (
          <div className="flex items-center justify-center py-20">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
            >
              <Loader2 className="w-8 h-8 text-violet-500" />
            </motion.div>
          </div>
        ) : filteredRoles.length === 0 ? (
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
              <Shield className="w-10 h-10 text-neutral-600" />
            </motion.div>
            <h3 className="text-xl font-semibold mb-2">No roles found</h3>
            <p className="text-neutral-500 mb-6">
              {searchQuery
                ? 'Try adjusting your search query'
                : 'Create your first role to get started'}
            </p>
            {!searchQuery && (
              <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                <Button
                  onClick={() => setIsCreateDialogOpen(true)}
                  className="bg-gradient-to-r from-violet-500 to-purple-500 hover:from-violet-600 hover:to-purple-600"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Create Role
                </Button>
              </motion.div>
            )}
          </motion.div>
        ) : (
          <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="visible"
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
          >
            {filteredRoles.map((role) => (
              <motion.div
                key={role.id}
                variants={itemVariants}
                whileHover={{ y: -4, scale: 1.02 }}
                transition={{ type: 'spring', stiffness: 300, damping: 20 }}
                className="group relative"
              >
                <div className="relative border border-neutral-800 bg-neutral-900/50 backdrop-blur-sm overflow-hidden hover:border-neutral-700 transition-colors">
                  {/* Top gradient bar */}
                  <div className={`absolute top-0 left-0 right-0 h-1 bg-gradient-to-r ${getRoleColor(role.name)}`} />
                  
                  {/* Hover gradient effect */}
                  <motion.div
                    className={`absolute inset-0 bg-gradient-to-br ${getRoleColor(role.name)} opacity-0 group-hover:opacity-5 transition-opacity duration-500`}
                  />

                  <div className="relative p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <motion.div
                          whileHover={{ rotate: 5, scale: 1.1 }}
                          transition={{ type: 'spring', stiffness: 300, damping: 15 }}
                          className={`w-12 h-12 rounded-xl bg-gradient-to-br ${getRoleColor(role.name)} flex items-center justify-center`}
                        >
                          <Shield className="w-6 h-6 text-white" />
                        </motion.div>
                        <div>
                          <h3 className="text-lg font-semibold text-neutral-100">{role.name}</h3>
                          {role.is_system && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-violet-500/10 text-violet-400 border border-violet-500/20 mt-1">
                              <Sparkles className="w-3 h-3 mr-1" />
                              System
                            </span>
                          )}
                        </div>
                      </div>
                    </div>

                    <p className="text-sm text-neutral-500 mb-4 line-clamp-2">
                      {role.description || 'No description provided'}
                    </p>

                    <div className="flex items-center gap-4 text-sm text-neutral-500 mb-5">
                      <div className="flex items-center gap-1.5">
                        <Key className="w-4 h-4" />
                        <span>{role.permissions?.length || 0} permissions</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <Link to="/admin/roles/$roleId" params={{ roleId: role.id }} className="flex-1">
                        <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                          <Button
                            variant="outline"
                            className="w-full bg-transparent border-neutral-700 text-neutral-300 hover:bg-neutral-800 hover:text-neutral-100 hover:border-neutral-600 group/btn"
                          >
                            <Pencil className="w-4 h-4 mr-2" />
                            Edit
                            <ChevronRight className="w-4 h-4 ml-auto opacity-0 group-hover/btn:opacity-100 transition-opacity" />
                          </Button>
                        </motion.div>
                      </Link>
                      {!role.is_system && (
                        <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                          <Button
                            variant="outline"
                            size="icon"
                            className="bg-transparent border-neutral-700 text-red-400 hover:bg-red-500/10 hover:border-red-500/30 hover:text-red-400"
                            onClick={() => {
                              setSelectedRole(role)
                              setIsDeleteDialogOpen(true)
                            }}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </motion.div>
                      )}
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </motion.div>
        )}
      </div>

      <CreateRoleDialog
        open={isCreateDialogOpen}
        onOpenChange={setIsCreateDialogOpen}
        onSubmit={handleCreateRole}
        isSubmitting={isSubmitting}
      />

      <DeleteRoleDialog
        open={isDeleteDialogOpen}
        onOpenChange={setIsDeleteDialogOpen}
        role={selectedRole}
        onConfirm={handleDeleteRole}
        isSubmitting={isSubmitting}
      />
    </div>
  )
}

interface CreateRoleDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSubmit: (data: RoleCreate) => Promise<void>
  isSubmitting: boolean
}

function CreateRoleDialog({
  open,
  onOpenChange,
  onSubmit,
  isSubmitting,
}: CreateRoleDialogProps) {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    await onSubmit({ name, description: description || undefined })
    setName('')
    setDescription('')
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-neutral-900 border-neutral-800 text-neutral-50">
        <DialogClose onClose={() => onOpenChange(false)} />
        <DialogHeader>
          <DialogTitle className="text-neutral-50">Create New Role</DialogTitle>
          <DialogDescription className="text-neutral-400">
            Add a new role to your organization. You can assign permissions after
            creation.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="name" className="text-neutral-300">Role Name</Label>
              <Input
                id="name"
                placeholder="e.g., Editor, Moderator"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                className="bg-neutral-800 border-neutral-700 text-neutral-50 placeholder:text-neutral-500"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="description" className="text-neutral-300">Description</Label>
              <Textarea
                id="description"
                placeholder="Describe what this role can do..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={3}
                className="bg-neutral-800 border-neutral-700 text-neutral-50 placeholder:text-neutral-500"
              />
            </div>
          </div>
          <DialogFooter>
            <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
              <Button
                type="button"
                variant="outline"
                onClick={() => onOpenChange(false)}
                className="bg-transparent border-neutral-700 text-neutral-300 hover:bg-neutral-800 hover:text-neutral-100"
              >
                Cancel
              </Button>
            </motion.div>
            <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
              <Button
                type="submit"
                disabled={isSubmitting || !name.trim()}
                className="bg-gradient-to-r from-violet-500 to-purple-500 hover:from-violet-600 hover:to-purple-600 text-white border-0"
              >
                {isSubmitting && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                Create Role
              </Button>
            </motion.div>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

interface DeleteRoleDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  role: Role | null
  onConfirm: () => Promise<void>
  isSubmitting: boolean
}

function DeleteRoleDialog({
  open,
  onOpenChange,
  role,
  onConfirm,
  isSubmitting,
}: DeleteRoleDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-neutral-900 border-neutral-800 text-neutral-50">
        <DialogClose onClose={() => onOpenChange(false)} />
        <DialogHeader>
          <DialogTitle className="text-red-400">Delete Role</DialogTitle>
          <DialogDescription className="text-neutral-400">
            Are you sure you want to delete the role "{role?.name}"? This action
            cannot be undone. All users with this role will lose their associated
            permissions.
          </DialogDescription>
        </DialogHeader>
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
              variant="destructive"
              onClick={onConfirm}
              disabled={isSubmitting}
              className="bg-red-500/20 text-red-400 border border-red-500/30 hover:bg-red-500/30"
            >
              {isSubmitting && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
              Delete Role
            </Button>
          </motion.div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
