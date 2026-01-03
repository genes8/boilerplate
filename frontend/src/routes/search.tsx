import { createFileRoute, Link } from '@tanstack/react-router'
import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { useSearch, useSearchSuggestions } from '@/hooks/useDocuments'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Search,
  FileText,
  ArrowLeft,
  X,
  Calendar,
  User,
  ChevronLeft,
  ChevronRight,
  Loader2,
  Sparkles,
  Filter,
  SlidersHorizontal,
} from 'lucide-react'
import type { SearchMode, SearchRequest, SearchFilters } from '@/lib/document-api'

export const Route = createFileRoute('/search')({
  component: SearchPage,
})

function SearchPage() {
  const [query, setQuery] = useState('')
  const [debouncedQuery, setDebouncedQuery] = useState('')
  const [mode, setMode] = useState<SearchMode>('simple')
  const [showFilters, setShowFilters] = useState(false)
  const [filters, setFilters] = useState<SearchFilters>({})
  const [page, setPage] = useState(1)
  const [hasSearched, setHasSearched] = useState(false)

  const searchRequest: SearchRequest = {
    query: debouncedQuery,
    mode,
    filters: Object.keys(filters).length > 0 ? filters : undefined,
    page,
    page_size: 10,
  }

  const { data: searchResults, isLoading, isFetching } = useSearch(searchRequest, hasSearched && !!debouncedQuery)
  const { data: suggestions } = useSearchSuggestions(query)

  // Debounce query for suggestions
  useEffect(() => {
    const timer = setTimeout(() => {
      if (query.length >= 2) {
        setDebouncedQuery(query)
      }
    }, 300)
    return () => clearTimeout(timer)
  }, [query])

  const handleSearch = useCallback(() => {
    if (query.trim()) {
      setDebouncedQuery(query)
      setHasSearched(true)
      setPage(1)
    }
  }, [query])

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch()
    }
  }

  const clearFilters = () => {
    setFilters({})
  }

  const modeDescriptions: Record<SearchMode, string> = {
    simple: 'Basic keyword search',
    phrase: 'Exact phrase matching',
    fuzzy: 'Typo-tolerant search',
    boolean: 'AND/OR/NOT operators',
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
    hidden: { opacity: 0, y: 20, scale: 0.98 },
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
        <div className="max-w-4xl mx-auto px-6 py-6">
          <div className="flex items-center gap-4 mb-6">
            <Link to="/documents" params={{}}>
              <motion.div whileHover={{ scale: 1.05, x: -2 }} whileTap={{ scale: 0.95 }}>
                <Button variant="ghost" size="sm" className="text-neutral-400 hover:text-neutral-200">
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Documents
                </Button>
              </motion.div>
            </Link>
            <div className="h-6 w-px bg-neutral-800" />
            <div>
              <h1 className="text-2xl font-bold tracking-tight">Search Documents</h1>
              <p className="text-sm text-neutral-500">Find documents using full-text search</p>
            </div>
          </div>

          {/* Search Input */}
          <div className="space-y-4">
            <div className="flex gap-3">
              <div className="relative flex-1">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-500" />
                <Input
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Search documents..."
                  className="bg-neutral-900 border-neutral-700 pl-12 h-12 text-lg"
                />
                {query && (
                  <motion.button
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.8 }}
                    onClick={() => {
                      setQuery('')
                      setDebouncedQuery('')
                      setHasSearched(false)
                    }}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-neutral-500 hover:text-neutral-300"
                  >
                    <X className="w-5 h-5" />
                  </motion.button>
                )}
              </div>
              <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                <Button
                  onClick={handleSearch}
                  disabled={!query.trim()}
                  className="bg-neutral-50 text-neutral-950 hover:bg-neutral-200 h-12 px-6"
                >
                  <Search className="w-4 h-4 mr-2" />
                  Search
                </Button>
              </motion.div>
            </div>

            {/* Search Mode & Filters Toggle */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Label className="text-neutral-400 text-sm">Mode:</Label>
                <Select value={mode} onValueChange={(v) => setMode(v as SearchMode)}>
                  <SelectTrigger className="w-[140px] bg-neutral-900 border-neutral-700">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-neutral-900 border-neutral-700">
                    {(['simple', 'phrase', 'fuzzy', 'boolean'] as SearchMode[]).map((m) => (
                      <SelectItem key={m} value={m} className="text-neutral-200">
                        {m.charAt(0).toUpperCase() + m.slice(1)}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <span className="text-xs text-neutral-500">{modeDescriptions[mode]}</span>
              </div>
              <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowFilters(!showFilters)}
                  className={`bg-neutral-900 border-neutral-700 ${showFilters ? 'border-neutral-500' : ''}`}
                >
                  <SlidersHorizontal className="w-4 h-4 mr-2" />
                  Filters
                  {Object.keys(filters).length > 0 && (
                    <Badge className="ml-2 bg-blue-500/20 text-blue-400">
                      {Object.keys(filters).length}
                    </Badge>
                  )}
                </Button>
              </motion.div>
            </div>

            {/* Filters Panel */}
            <AnimatePresence>
              {showFilters && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.2 }}
                  className="overflow-hidden"
                >
                  <Card className="bg-neutral-900/50 border-neutral-800 p-4">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-2">
                        <Filter className="w-4 h-4 text-neutral-500" />
                        <span className="text-sm font-medium">Filters</span>
                      </div>
                      {Object.keys(filters).length > 0 && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={clearFilters}
                          className="text-neutral-400 hover:text-neutral-200"
                        >
                          Clear all
                        </Button>
                      )}
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="space-y-2">
                        <Label className="text-neutral-400 text-xs">Date From</Label>
                        <Input
                          type="date"
                          value={filters.date_from?.split('T')[0] || ''}
                          onChange={(e) =>
                            setFilters((prev) => ({
                              ...prev,
                              date_from: e.target.value ? new Date(e.target.value).toISOString() : undefined,
                            }))
                          }
                          className="bg-neutral-800 border-neutral-700"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label className="text-neutral-400 text-xs">Date To</Label>
                        <Input
                          type="date"
                          value={filters.date_to?.split('T')[0] || ''}
                          onChange={(e) =>
                            setFilters((prev) => ({
                              ...prev,
                              date_to: e.target.value ? new Date(e.target.value).toISOString() : undefined,
                            }))
                          }
                          className="bg-neutral-800 border-neutral-700"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label className="text-neutral-400 text-xs">Owner ID</Label>
                        <Input
                          value={filters.owner_id || ''}
                          onChange={(e) =>
                            setFilters((prev) => ({
                              ...prev,
                              owner_id: e.target.value || undefined,
                            }))
                          }
                          placeholder="UUID"
                          className="bg-neutral-800 border-neutral-700"
                        />
                      </div>
                    </div>
                  </Card>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Suggestions */}
            <AnimatePresence>
              {suggestions && suggestions.suggestions.length > 0 && query && !hasSearched && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="flex items-center gap-2 flex-wrap"
                >
                  <Sparkles className="w-4 h-4 text-neutral-500" />
                  <span className="text-sm text-neutral-500">Suggestions:</span>
                  {suggestions.suggestions.slice(0, 5).map((suggestion, index) => (
                    <motion.button
                      key={index}
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: index * 0.05 }}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => {
                        setQuery(suggestion.text)
                        setDebouncedQuery(suggestion.text)
                        setHasSearched(true)
                      }}
                      className="px-3 py-1 text-sm bg-neutral-800 border border-neutral-700 rounded-full hover:border-neutral-600 transition-colors"
                    >
                      {suggestion.text}
                    </motion.button>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </motion.div>

      {/* Results */}
      <div className="max-w-4xl mx-auto px-6 py-8">
        {!hasSearched ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center py-20"
          >
            <motion.div
              className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-blue-500/20 to-cyan-500/20 flex items-center justify-center"
              animate={{
                scale: [1, 1.05, 1],
                rotate: [0, 2, -2, 0],
              }}
              transition={{
                duration: 4,
                repeat: Infinity,
                ease: 'easeInOut',
              }}
            >
              <Search className="w-10 h-10 text-blue-400" />
            </motion.div>
            <h2 className="text-xl font-semibold mb-2">Search your documents</h2>
            <p className="text-neutral-400 max-w-md mx-auto">
              Enter a search query to find documents. Use different search modes for more precise results.
            </p>
          </motion.div>
        ) : isLoading ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex items-center justify-center py-20"
          >
            <Loader2 className="w-8 h-8 animate-spin text-neutral-500" />
          </motion.div>
        ) : searchResults?.items.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center py-20"
          >
            <FileText className="w-16 h-16 mx-auto text-neutral-700 mb-4" />
            <h3 className="text-xl font-semibold mb-2">No results found</h3>
            <p className="text-neutral-400 mb-4">
              No documents match "{debouncedQuery}"
            </p>
            <p className="text-sm text-neutral-500">
              Try different keywords or search modes
            </p>
          </motion.div>
        ) : (
          <>
            {/* Results Header */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex items-center justify-between mb-6"
            >
              <div className="flex items-center gap-2">
                <span className="text-neutral-400">
                  Found <span className="text-neutral-200 font-medium">{searchResults?.total}</span> results
                </span>
                {isFetching && <Loader2 className="w-4 h-4 animate-spin text-neutral-500" />}
              </div>
              <Badge variant="secondary" className="bg-neutral-800 text-neutral-400">
                Mode: {mode}
              </Badge>
            </motion.div>

            {/* Results List */}
            <motion.div
              variants={containerVariants}
              initial="hidden"
              animate="visible"
              className="space-y-4"
            >
              {searchResults?.items.map((result) => (
                <motion.div
                  key={result.document.id}
                  variants={itemVariants}
                  whileHover={{ x: 4 }}
                  transition={{ type: 'spring' as const, stiffness: 300, damping: 20 }}
                >
                  <Link to="/documents/$documentId" params={{ documentId: result.document.id }}>
                    <Card className="bg-neutral-900/50 border-neutral-800 hover:border-neutral-700 transition-colors p-5 group">
                      <div className="flex items-start gap-4">
                        <motion.div
                          className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center flex-shrink-0"
                          whileHover={{ rotate: 5, scale: 1.1 }}
                        >
                          <FileText className="w-6 h-6 text-white" />
                        </motion.div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-start justify-between gap-4 mb-2">
                            <h3 className="text-lg font-semibold group-hover:text-neutral-200 transition-colors">
                              {result.document.title}
                            </h3>
                            <Badge className="bg-blue-500/20 text-blue-400 flex-shrink-0">
                              Rank: {result.rank.toFixed(2)}
                            </Badge>
                          </div>

                          {/* Highlights */}
                          {result.highlights.length > 0 && (
                            <div className="mb-3 space-y-1">
                              {result.highlights.map((highlight, hIndex) => (
                                <p
                                  key={hIndex}
                                  className="text-sm text-neutral-400"
                                  dangerouslySetInnerHTML={{
                                    __html: highlight.fragment.replace(
                                      /<b>/g,
                                      '<mark class="bg-yellow-500/30 text-yellow-200 px-0.5 rounded">'
                                    ).replace(/<\/b>/g, '</mark>'),
                                  }}
                                />
                              ))}
                            </div>
                          )}

                          {/* Metadata */}
                          <div className="flex items-center gap-4 text-xs text-neutral-500">
                            <div className="flex items-center gap-1">
                              <User className="w-3 h-3" />
                              <span>{result.document.owner?.username || 'Unknown'}</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <Calendar className="w-3 h-3" />
                              <span>{new Date(result.document.created_at).toLocaleDateString()}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </Card>
                  </Link>
                </motion.div>
              ))}
            </motion.div>

            {/* Pagination */}
            {searchResults && searchResults.pages > 1 && (
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
                    disabled={page === 1}
                    onClick={() => setPage((p) => p - 1)}
                    className="bg-neutral-900 border-neutral-700 hover:bg-neutral-800"
                  >
                    <ChevronLeft className="w-4 h-4 mr-1" />
                    Previous
                  </Button>
                </motion.div>
                <span className="text-sm text-neutral-400">
                  Page {searchResults.page} of {searchResults.pages}
                </span>
                <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={page === searchResults.pages}
                    onClick={() => setPage((p) => p + 1)}
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
    </div>
    </ProtectedRoute>
  )
}
