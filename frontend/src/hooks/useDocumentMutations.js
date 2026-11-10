import { useMutation, useQueryClient } from '@tanstack/react-query'
import {
  correctDocument,
  deleteDocument,
  downloadAllDocuments,
  purgeDocumentFile,
  reprocessDocument,
} from '../api/documents'
import { documentKeys } from './useDocumentsQueries'

export function useCorrectDocument(id) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ field, value }) => correctDocument(id, field, value),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: documentKeys.detail(id) })
    },
  })
}

export function useReprocessDocument(id) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: () => reprocessDocument(id),
    // onSettled, not onSuccess: after a 409 (already processing) the cached doc
    // may be stale ('failed'), so refetch to resume polling the running job.
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: documentKeys.detail(id) })
      queryClient.invalidateQueries({ queryKey: documentKeys.summary })
    },
  })
}

export function usePurgeDocumentFile(id) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: () => purgeDocumentFile(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: documentKeys.detail(id) })
    },
  })
}

export function useDeleteDocument(id) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: () => deleteDocument(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents', 'list'] })
    },
  })
}

export function useDownloadAllDocumentsMutation() {
  return useMutation({
    mutationFn: (documentIds) => downloadAllDocuments(documentIds),
  })
}
