import { useState, useRef, useEffect } from 'react'
import { useNavigate } from '@tanstack/react-router'
import { motion, AnimatePresence } from 'motion/react'
import { useSearchSuggestions } from '@/hooks/useDocuments'
import { Input } from '@/components/ui/input'
import { Search, X, FileText, Loader2 } from 'lucide-react'

interface SearchBarProps {
  placeholder?: string
  className?: string
  onSearch?: (query: string) => void
  autoFocus?: boolean
}

export function SearchBar({
  placeholder = 'Search documents...',
  className = '',
  onSearch,
  autoFocus = false,
}: SearchBarProps) {
  const navigate = useNavigate()
  const [query, setQuery] = useState('')
  const [isFocused, setIsFocused] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  const { data: suggestions, isLoading } = useSearchSuggestions(query, 5)

  const handleSearch = () => {
    if (query.trim()) {
      if (onSearch) {
        onSearch(query)
      } else {
        navigate({ to: '/search', search: { q: query } })
      }
      setIsFocused(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch()
    }
    if (e.key === 'Escape') {
      setIsFocused(false)
      inputRef.current?.blur()
    }
  }

  const handleSuggestionClick = (text: string) => {
    setQuery(text)
    if (onSearch) {
      onSearch(text)
    } else {
      navigate({ to: '/search', search: { q: text } })
    }
    setIsFocused(false)
  }

  // Close suggestions on outside click
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsFocused(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const showSuggestions = isFocused && query.length >= 2 && suggestions?.suggestions.length

  return (
    <div ref={containerRef} className={`relative ${className}`}>
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-500" />
        <Input
          ref={inputRef}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => setIsFocused(true)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          autoFocus={autoFocus}
          className="bg-neutral-900 border-neutral-700 pl-10 pr-10 focus:border-neutral-600"
        />
        <AnimatePresence>
          {query && (
            <motion.button
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              onClick={() => setQuery('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-500 hover:text-neutral-300"
            >
              <X className="w-4 h-4" />
            </motion.button>
          )}
        </AnimatePresence>
      </div>

      {/* Suggestions Dropdown */}
      <AnimatePresence>
        {showSuggestions && (
          <motion.div
            initial={{ opacity: 0, y: -10, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.98 }}
            transition={{ type: 'spring' as const, stiffness: 300, damping: 25 }}
            className="absolute top-full left-0 right-0 mt-2 bg-neutral-900 border border-neutral-700 rounded-lg shadow-xl overflow-hidden z-50"
          >
            {isLoading ? (
              <div className="flex items-center justify-center py-4">
                <Loader2 className="w-4 h-4 animate-spin text-neutral-500" />
              </div>
            ) : (
              <div className="py-1">
                {suggestions?.suggestions.map((suggestion, index) => (
                  <motion.button
                    key={index}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.03 }}
                    onClick={() => handleSuggestionClick(suggestion.text)}
                    className="w-full px-4 py-2.5 flex items-center gap-3 hover:bg-neutral-800 transition-colors text-left"
                  >
                    <FileText className="w-4 h-4 text-neutral-500 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-neutral-200 truncate">{suggestion.text}</p>
                      <p className="text-xs text-neutral-500">from {suggestion.field}</p>
                    </div>
                  </motion.button>
                ))}
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default SearchBar
