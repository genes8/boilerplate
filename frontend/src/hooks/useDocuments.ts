/**
 * TanStack Query hooks for document management.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  documentApi,
  type Document,
  type DocumentCreate,
  type DocumentUpdate,
  type DocumentListParams,
  type SearchRequest,
} from '@/lib/document-api';

// Query keys
export const documentKeys = {
  all: ['documents'] as const,
  lists: () => [...documentKeys.all, 'list'] as const,
  list: (params?: DocumentListParams) => [...documentKeys.lists(), params] as const,
  details: () => [...documentKeys.all, 'detail'] as const,
  detail: (id: string) => [...documentKeys.details(), id] as const,
  search: (query: string) => [...documentKeys.all, 'search', query] as const,
  suggestions: (query: string) => [...documentKeys.all, 'suggestions', query] as const,
};

// Hooks
export function useDocuments(params?: DocumentListParams) {
  return useQuery({
    queryKey: documentKeys.list(params),
    queryFn: () => documentApi.getDocuments(params),
  });
}

export function useDocument(id: string) {
  return useQuery({
    queryKey: documentKeys.detail(id),
    queryFn: () => documentApi.getDocument(id),
    enabled: !!id,
  });
}

export function useCreateDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: DocumentCreate) => documentApi.createDocument(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: documentKeys.lists() });
    },
  });
}

export function useUpdateDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: DocumentUpdate }) =>
      documentApi.updateDocument(id, data),
    onSuccess: (updatedDoc: Document) => {
      queryClient.invalidateQueries({ queryKey: documentKeys.lists() });
      queryClient.setQueryData(documentKeys.detail(updatedDoc.id), updatedDoc);
    },
  });
}

export function useDeleteDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => documentApi.deleteDocument(id),
    onSuccess: (_data, id) => {
      queryClient.invalidateQueries({ queryKey: documentKeys.lists() });
      queryClient.removeQueries({ queryKey: documentKeys.detail(id) });
    },
  });
}

export function useSearch(request: SearchRequest, enabled = true) {
  return useQuery({
    queryKey: documentKeys.search(JSON.stringify(request)),
    queryFn: () => documentApi.searchDocuments(request),
    enabled: enabled && !!request.query,
  });
}

export function useSearchSuggestions(query: string, limit?: number) {
  return useQuery({
    queryKey: documentKeys.suggestions(query),
    queryFn: () => documentApi.getSuggestions(query, limit),
    enabled: query.length >= 2,
    staleTime: 30000, // 30 seconds
  });
}
