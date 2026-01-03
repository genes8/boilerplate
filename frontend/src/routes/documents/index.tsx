import { createFileRoute, Link } from '@tanstack/react-router'
import { useState } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { useDocuments, useDeleteDocument, useCreateDocument } from '@/hooks/useDocuments'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  FileText,
  Plus,
  Trash2,
  Edit,
  Search,
  ChevronLeft,
  ChevronRight,
  Calendar,
  User,
  Grid3X3,
  List,
  ArrowUpDown,
  Loader2,
} from 'lucide-react'
import type { DocumentListParams, DocumentCreate } from '@/lib/document-api'

export const Route = createFileRoute('/documents/')({
  component: DocumentsPage,
})

function DocumentsPage() {
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [params, setParams] = useState<DocumentListParams>({
    page: 1,
    page_size: 12,
    sort_by: 'created_at',
    sort_order: 'desc',
  })
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [documentToDelete, setDocumentToDelete] = useState<string | null>(null)
  const [newDocument, setNewDocument] = useState<DocumentCreate>({
    title: '',
    content: '',
    meta: {},
  })

  const { data, isLoading, error } = useDocuments(params)
  const createMutation = useCreateDocument()
  const deleteMutation = useDeleteDocument()

  const handleCreate = async () => {
    if (!newDocument.title.trim()) return
    await createMutation.mutateAsync(newDocument)
    setCreateDialogOpen(false)
    setNewDocument({ title: '', content: '', meta: {} })
  }

  const handleDelete = async () => {
    if (!documentToDelete) return
    await deleteMutation.mutateAsync(documentToDelete)
    setDeleteDialogOpen(false)
    setDocumentToDelete(null)
  }

  const toggleSort = (field: 'created_at' | 'updated_at' | 'title') => {
    setParams((prev) => ({
      ...prev,
      sort_by: field,
      sort_order: prev.sort_by === field && prev.sort_order === 'desc' ? 'asc' : 'desc',
    }))
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
    exit: {
      opacity: 0,
      scale: 0.9,
      transition: { duration: 0.2 },
    },
  }

  return (
    <ProtectedRoute>
    <div className="min-h-screen bg-neutral-950 text-neutral-50">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="border-b border-neutral-800 bg-neutral-900/50 backdrop-blur-xl sticky top-0 z-40"
      >
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <motion.h1
                className="text-3xl font-bold tracking-tight"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1 }}
              >
                Documents
              </motion.h1>
              <motion.p
                className="text-neutral-400 mt-1"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 }}
              >
                Manage and search your documents
              </motion.p>
            </div>

            <motion.div
              className="flex items-center gap-3"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
            >
              {/* Search Link */}
              <Link to="/search" params={{}}>
                <Button
                  variant="outline"
                  className="bg-neutral-900 border-neutral-700 hover:bg-neutral-800 hover:border-neutral-600"
                >
                  <Search className="w-4 h-4 mr-2" />
                  Search
                </Button>
              </Link>

              {/* View Toggle */}
              <div className="flex items-center border border-neutral-700 rounded-lg overflow-hidden">
                <motion.button
                  whileHover={{ backgroundColor: 'rgba(255,255,255,0.1)' }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setViewMode('grid')}
                  className={`p-2 transition-colors ${
                    viewMode === 'grid' ? 'bg-neutral-800' : 'bg-transparent'
                  }`}
                >
                  <Grid3X3 className="w-4 h-4" />
                </motion.button>
                <motion.button
                  whileHover={{ backgroundColor: 'rgba(255,255,255,0.1)' }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setViewMode('list')}
                  className={`p-2 transition-colors ${
                    viewMode === 'list' ? 'bg-neutral-800' : 'bg-transparent'
                  }`}
                >
                  <List className="w-4 h-4" />
                </motion.button>
              </div>

              {/* Create Button */}
              <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                <Button
                  onClick={() => setCreateDialogOpen(true)}
                  className="bg-neutral-50 text-neutral-950 hover:bg-neutral-200"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  New Document
                </Button>
              </motion.div>
            </motion.div>
          </div>

          {/* Sort Controls */}
          <motion.div
            className="flex items-center gap-2 mt-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            <span className="text-sm text-neutral-500">Sort by:</span>
            {(['created_at', 'updated_at', 'title'] as const).map((field) => (
              <motion.button
                key={field}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => toggleSort(field)}
                className={`px-3 py-1.5 text-sm rounded-lg border transition-colors flex items-center gap-1 ${
                  params.sort_by === field
                    ? 'border-neutral-500 bg-neutral-800 text-neutral-200'
                    : 'border-neutral-700 bg-transparent text-neutral-400 hover:border-neutral-600'
                }`}
              >
                {field === 'created_at' ? 'Created' : field === 'updated_at' ? 'Updated' : 'Title'}
                {params.sort_by === field && (
                  <ArrowUpDown className={`w-3 h-3 ${params.sort_order === 'asc' ? 'rotate-180' : ''}`} />
                )}
              </motion.button>
            ))}
          </motion.div>
        </div>
      </motion.div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {isLoading ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex items-center justify-center py-20"
          >
            <Loader2 className="w-8 h-8 animate-spin text-neutral-500" />
          </motion.div>
        ) : error ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center py-20"
          >
            <p className="text-red-400">Error loading documents</p>
          </motion.div>
        ) : data?.items.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center py-20"
          >
            <FileText className="w-16 h-16 mx-auto text-neutral-700 mb-4" />
            <h3 className="text-xl font-semibold mb-2">No documents yet</h3>
            <p className="text-neutral-400 mb-6">Create your first document to get started</p>
            <Button
              onClick={() => setCreateDialogOpen(true)}
              className="bg-neutral-50 text-neutral-950 hover:bg-neutral-200"
            >
              <Plus className="w-4 h-4 mr-2" />
              Create Document
            </Button>
          </motion.div>
        ) : (
          <>
            {/* Document Grid/List */}
            <AnimatePresence mode="wait">
              {viewMode === 'grid' ? (
                <motion.div
                  key="grid"
                  variants={containerVariants}
                  initial="hidden"
                  animate="visible"
                  exit="hidden"
                  className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
                >
                  {data?.items.map((doc) => (
                    <motion.div
                      key={doc.id}
                      variants={itemVariants}
                      layout
                      whileHover={{ y: -4, scale: 1.01 }}
                      transition={{ type: 'spring', stiffness: 300, damping: 20 }}
                    >
                      <Card className="bg-neutral-900/50 border-neutral-800 hover:border-neutral-700 transition-colors overflow-hidden group">
                        <Link to="/documents/$documentId" params={{ documentId: doc.id }}>
                          <div className="p-5">
                            <div className="flex items-start justify-between mb-3">
                              <motion.div
                                className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center"
                                whileHover={{ rotate: 5, scale: 1.1 }}
                              >
                                <FileText className="w-5 h-5 text-white" />
                              </motion.div>
                              <Badge variant="secondary" className="bg-neutral-800 text-neutral-400">
                                {new Date(doc.created_at).toLocaleDateString()}
                              </Badge>
                            </div>
                            <h3 className="text-lg font-semibold mb-2 line-clamp-1 group-hover:text-neutral-200 transition-colors">
                              {doc.title}
                            </h3>
                            <p className="text-sm text-neutral-400 line-clamp-2 mb-4">
                              {doc.content || 'No content'}
                            </p>
                            <div className="flex items-center gap-2 text-xs text-neutral-500">
                              <User className="w-3 h-3" />
                              <span>{doc.owner?.username || 'Unknown'}</span>
                            </div>
                          </div>
                        </Link>
                        <div className="border-t border-neutral-800 px-5 py-3 flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                          <Link to="/documents/$documentId" params={{ documentId: doc.id }}>
                            <Button variant="ghost" size="sm" className="text-neutral-400 hover:text-neutral-200">
                              <Edit className="w-4 h-4" />
                            </Button>
                          </Link>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-red-400 hover:text-red-300 hover:bg-red-500/10"
                            onClick={(e) => {
                              e.preventDefault()
                              setDocumentToDelete(doc.id)
                              setDeleteDialogOpen(true)
                            }}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </Card>
                    </motion.div>
                  ))}
                </motion.div>
              ) : (
                <motion.div
                  key="list"
                  variants={containerVariants}
                  initial="hidden"
                  animate="visible"
                  exit="hidden"
                  className="space-y-2"
                >
                  {data?.items.map((doc) => (
                    <motion.div
                      key={doc.id}
                      variants={itemVariants}
                      layout
                      whileHover={{ x: 4 }}
                      transition={{ type: 'spring', stiffness: 300, damping: 20 }}
                    >
                      <Card className="bg-neutral-900/50 border-neutral-800 hover:border-neutral-700 transition-colors">
                        <Link to="/documents/$documentId" params={{ documentId: doc.id }}>
                          <div className="p-4 flex items-center gap-4">
                            <motion.div
                              className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center flex-shrink-0"
                              whileHover={{ rotate: 5, scale: 1.1 }}
                            >
                              <FileText className="w-5 h-5 text-white" />
                            </motion.div>
                            <div className="flex-1 min-w-0">
                              <h3 className="font-semibold truncate">{doc.title}</h3>
                              <p className="text-sm text-neutral-400 truncate">
                                {doc.content || 'No content'}
                              </p>
                            </div>
                            <div className="flex items-center gap-4 text-sm text-neutral-500">
                              <div className="flex items-center gap-1">
                                <User className="w-3 h-3" />
                                <span>{doc.owner?.username || 'Unknown'}</span>
                              </div>
                              <div className="flex items-center gap-1">
                                <Calendar className="w-3 h-3" />
                                <span>{new Date(doc.created_at).toLocaleDateString()}</span>
                              </div>
                            </div>
                            <div className="flex items-center gap-1">
                              <Button variant="ghost" size="sm" className="text-neutral-400 hover:text-neutral-200">
                                <Edit className="w-4 h-4" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                className="text-red-400 hover:text-red-300 hover:bg-red-500/10"
                                onClick={(e) => {
                                  e.preventDefault()
                                  setDocumentToDelete(doc.id)
                                  setDeleteDialogOpen(true)
                                }}
                              >
                                <Trash2 className="w-4 h-4" />
                              </Button>
                            </div>
                          </div>
                        </Link>
                      </Card>
                    </motion.div>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>

            {/* Pagination */}
            {data && data.pages > 1 && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.3 }}
                className="flex items-center justify-center gap-4 mt-8"
              >
                <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={params.page === 1}
                    onClick={() => setParams((prev) => ({ ...prev, page: (prev.page || 1) - 1 }))}
                    className="bg-neutral-900 border-neutral-700 hover:bg-neutral-800"
                  >
                    <ChevronLeft className="w-4 h-4 mr-1" />
                    Previous
                  </Button>
                </motion.div>
                <span className="text-sm text-neutral-400">
                  Page {data.page} of {data.pages}
                </span>
                <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={params.page === data.pages}
                    onClick={() => setParams((prev) => ({ ...prev, page: (prev.page || 1) + 1 }))}
                    className="bg-neutral-900 border-neutral-700 hover:bg-neutral-800"
                  >
                    Next
                    <ChevronRight className="w-4 h-4 ml-1" />
                  </Button>
                </motion.div>
              </motion.div>
            )}
          </>
        )}
      </div>

      {/* Create Document Dialog */}
      <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
        <DialogContent className="bg-neutral-900 border-neutral-800 text-neutral-50">
          <DialogHeader>
            <DialogTitle>Create New Document</DialogTitle>
            <DialogDescription className="text-neutral-400">
              Add a new document to your collection
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="title">Title</Label>
              <Input
                id="title"
                value={newDocument.title}
                onChange={(e) => setNewDocument((prev) => ({ ...prev, title: e.target.value }))}
                placeholder="Document title"
                className="bg-neutral-800 border-neutral-700"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="content">Content</Label>
              <Textarea
                id="content"
                value={newDocument.content || ''}
                onChange={(e) => setNewDocument((prev) => ({ ...prev, content: e.target.value }))}
                placeholder="Document content..."
                rows={6}
                className="bg-neutral-800 border-neutral-700"
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setCreateDialogOpen(false)}
              className="bg-neutral-800 border-neutral-700"
            >
              Cancel
            </Button>
            <Button
              onClick={handleCreate}
              disabled={!newDocument.title.trim() || createMutation.isPending}
              className="bg-neutral-50 text-neutral-950 hover:bg-neutral-200"
            >
              {createMutation.isPending ? (
                <Loader2 className="w-4 h-4 animate-spin mr-2" />
              ) : (
                <Plus className="w-4 h-4 mr-2" />
              )}
              Create
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent className="bg-neutral-900 border-neutral-800 text-neutral-50">
          <DialogHeader>
            <DialogTitle>Delete Document</DialogTitle>
            <DialogDescription className="text-neutral-400">
              Are you sure you want to delete this document? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setDeleteDialogOpen(false)}
              className="bg-neutral-800 border-neutral-700"
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDelete}
              disabled={deleteMutation.isPending}
              className="bg-red-600 hover:bg-red-700"
            >
              {deleteMutation.isPending ? (
                <Loader2 className="w-4 h-4 animate-spin mr-2" />
              ) : (
                <Trash2 className="w-4 h-4 mr-2" />
              )}
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
    </ProtectedRoute>
  )
}
