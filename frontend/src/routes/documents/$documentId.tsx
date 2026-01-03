import { createFileRoute, Link, useNavigate } from '@tanstack/react-router'
import { useState, useEffect } from 'react'
import { motion } from 'motion/react'
import { useDocument, useUpdateDocument, useDeleteDocument } from '@/hooks/useDocuments'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  FileText,
  ArrowLeft,
  Save,
  Trash2,
  Edit,
  X,
  Calendar,
  User,
  Clock,
  Loader2,
  Check,
} from 'lucide-react'

export const Route = createFileRoute('/documents/$documentId')({
  component: DocumentDetailPage,
})

function DocumentDetailPage() {
  const { documentId } = Route.useParams()
  const navigate = useNavigate()
  const { data: document, isLoading, error } = useDocument(documentId)
  const updateMutation = useUpdateDocument()
  const deleteMutation = useDeleteDocument()

  const [isEditing, setIsEditing] = useState(false)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [editedTitle, setEditedTitle] = useState('')
  const [editedContent, setEditedContent] = useState('')
  const [showSaved, setShowSaved] = useState(false)

  useEffect(() => {
    if (document) {
      setEditedTitle(document.title)
      setEditedContent(document.content || '')
    }
  }, [document])

  const handleSave = async () => {
    await updateMutation.mutateAsync({
      id: documentId,
      data: {
        title: editedTitle,
        content: editedContent,
      },
    })
    setIsEditing(false)
    setShowSaved(true)
    setTimeout(() => setShowSaved(false), 2000)
  }

  const handleDelete = async () => {
    await deleteMutation.mutateAsync(documentId)
    navigate({ to: '/documents' })
  }

  const handleCancel = () => {
    if (document) {
      setEditedTitle(document.title)
      setEditedContent(document.content || '')
    }
    setIsEditing(false)
  }

  if (isLoading) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-neutral-950 text-neutral-50 flex items-center justify-center">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex items-center gap-3"
          >
            <Loader2 className="w-6 h-6 animate-spin text-neutral-500" />
            <span className="text-neutral-400">Loading document...</span>
          </motion.div>
        </div>
      </ProtectedRoute>
    )
  }

  if (error || !document) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-neutral-950 text-neutral-50 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center"
        >
          <FileText className="w-16 h-16 mx-auto text-neutral-700 mb-4" />
          <h2 className="text-xl font-semibold mb-2">Document not found</h2>
          <p className="text-neutral-400 mb-6">The document you're looking for doesn't exist.</p>
          <Link to="/documents" params={{}}>
            <Button className="bg-neutral-50 text-neutral-950 hover:bg-neutral-200">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Documents
            </Button>
            </Link>
          </motion.div>
        </div>
      </ProtectedRoute>
    )
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
        <div className="max-w-4xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link to="/documents" params={{}}>
                <motion.div
                  whileHover={{ scale: 1.05, x: -2 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Button variant="ghost" size="sm" className="text-neutral-400 hover:text-neutral-200">
                    <ArrowLeft className="w-4 h-4 mr-2" />
                    Back
                  </Button>
                </motion.div>
              </Link>
              <div className="h-6 w-px bg-neutral-800" />
              <motion.div
                className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center"
                whileHover={{ rotate: 5, scale: 1.1 }}
                transition={{ type: 'spring' as const, stiffness: 300, damping: 15 }}
              >
                <FileText className="w-5 h-5 text-white" />
              </motion.div>
              <div>
                <h1 className="font-semibold">{isEditing ? 'Editing Document' : 'Document Details'}</h1>
                <p className="text-sm text-neutral-500">
                  Created {new Date(document.created_at).toLocaleDateString()}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              {showSaved && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                  className="flex items-center gap-1 text-emerald-400 text-sm"
                >
                  <Check className="w-4 h-4" />
                  Saved
                </motion.div>
              )}
              {isEditing ? (
                <>
                  <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                    <Button
                      variant="ghost"
                      onClick={handleCancel}
                      className="text-neutral-400 hover:text-neutral-200"
                    >
                      <X className="w-4 h-4 mr-2" />
                      Cancel
                    </Button>
                  </motion.div>
                  <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                    <Button
                      onClick={handleSave}
                      disabled={updateMutation.isPending}
                      className="bg-neutral-50 text-neutral-950 hover:bg-neutral-200"
                    >
                      {updateMutation.isPending ? (
                        <Loader2 className="w-4 h-4 animate-spin mr-2" />
                      ) : (
                        <Save className="w-4 h-4 mr-2" />
                      )}
                      Save
                    </Button>
                  </motion.div>
                </>
              ) : (
                <>
                  <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                    <Button
                      variant="outline"
                      onClick={() => setIsEditing(true)}
                      className="bg-neutral-900 border-neutral-700 hover:bg-neutral-800"
                    >
                      <Edit className="w-4 h-4 mr-2" />
                      Edit
                    </Button>
                  </motion.div>
                  <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                    <Button
                      variant="ghost"
                      onClick={() => setDeleteDialogOpen(true)}
                      className="text-red-400 hover:text-red-300 hover:bg-red-500/10"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </motion.div>
                </>
              )}
            </div>
          </div>
        </div>
      </motion.div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-6 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          {isEditing ? (
            <div className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="title" className="text-neutral-300">Title</Label>
                <Input
                  id="title"
                  value={editedTitle}
                  onChange={(e) => setEditedTitle(e.target.value)}
                  className="bg-neutral-900 border-neutral-700 text-lg font-semibold h-12"
                  placeholder="Document title"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="content" className="text-neutral-300">Content</Label>
                <Textarea
                  id="content"
                  value={editedContent}
                  onChange={(e) => setEditedContent(e.target.value)}
                  className="bg-neutral-900 border-neutral-700 min-h-[400px] resize-y"
                  placeholder="Document content..."
                />
              </div>
            </div>
          ) : (
            <>
              {/* Title */}
              <motion.h1
                className="text-3xl font-bold mb-6"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 }}
              >
                {document.title}
              </motion.h1>

              {/* Metadata */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.3 }}
                className="flex flex-wrap items-center gap-4 mb-8"
              >
                <Badge variant="secondary" className="bg-neutral-800 text-neutral-300">
                  <User className="w-3 h-3 mr-1" />
                  {document.owner?.username || 'Unknown'}
                </Badge>
                <Badge variant="secondary" className="bg-neutral-800 text-neutral-300">
                  <Calendar className="w-3 h-3 mr-1" />
                  Created {new Date(document.created_at).toLocaleDateString()}
                </Badge>
                <Badge variant="secondary" className="bg-neutral-800 text-neutral-300">
                  <Clock className="w-3 h-3 mr-1" />
                  Updated {new Date(document.updated_at).toLocaleDateString()}
                </Badge>
              </motion.div>

              {/* Content */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
              >
                <Card className="bg-neutral-900/50 border-neutral-800 p-6">
                  {document.content ? (
                    <div className="prose prose-invert max-w-none">
                      <p className="text-neutral-300 whitespace-pre-wrap leading-relaxed">
                        {document.content}
                      </p>
                    </div>
                  ) : (
                    <p className="text-neutral-500 italic">No content</p>
                  )}
                </Card>
              </motion.div>

              {/* Metadata JSON */}
              {Object.keys(document.meta).length > 0 && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5 }}
                  className="mt-6"
                >
                  <h3 className="text-sm font-medium text-neutral-400 mb-3">Metadata</h3>
                  <Card className="bg-neutral-900/50 border-neutral-800 p-4">
                    <pre className="text-sm text-neutral-400 overflow-x-auto">
                      {JSON.stringify(document.meta, null, 2)}
                    </pre>
                  </Card>
                </motion.div>
              )}
            </>
          )}
        </motion.div>
      </div>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent className="bg-neutral-900 border-neutral-800 text-neutral-50">
          <DialogHeader>
            <DialogTitle>Delete Document</DialogTitle>
            <DialogDescription className="text-neutral-400">
              Are you sure you want to delete "{document.title}"? This action cannot be undone.
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
