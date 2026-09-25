import { useEffect, useRef, useState } from 'react'

import { getConversation } from '../api'
import type { Conversation, ConversationDetail } from '../types'
import { normalizeError } from '../utils'
import { useConversationActions } from './useConversationActions'

type UseActiveConversationOptions = {
  onConversationUpdated?: (conversation: Conversation) => void
}

export function useActiveConversation({
  onConversationUpdated,
}: UseActiveConversationOptions = {}) {
  const [activeConversationId, setActiveConversationId] = useState<string | null>(
    null,
  )
  const [activeConversation, setActiveConversation] =
    useState<ConversationDetail | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [loadError, setLoadError] = useState<Error | null>(null)
  const activeConversationIdRef = useRef<string | null>(null)
  const hasPendingConfirmations =
    (activeConversation?.pending_confirmations.length ?? 0) > 0

  function handleConversationUpdated(
    conversationId: string,
    detail: ConversationDetail,
  ): void {
    onConversationUpdated?.(detail.conversation)

    if (activeConversationIdRef.current === conversationId) {
      setActiveConversation(detail)
    }
  }

  const {
    approveConfirmation,
    clearError: clearActionError,
    error: actionError,
    isSending,
    pendingUserMessage,
    processingConfirmationId,
    rejectConfirmation,
    sendMessage,
  } = useConversationActions({
    conversationId: activeConversationId,
    hasPendingConfirmations,
    onConversationUpdated: handleConversationUpdated,
  })

  useEffect(() => {
    if (activeConversationId === null) {
      return
    }

    const conversationId = activeConversationId
    let isCurrentRequest = true

    async function loadConversation(): Promise<void> {
      try {
        const conversation = await getConversation(conversationId)

        if (isCurrentRequest) {
          setActiveConversation(conversation)
        }
      } catch (currentError) {
        if (isCurrentRequest) {
          setLoadError(
            normalizeError(
              currentError,
              'No se pudo cargar la conversación',
            ),
          )
        }
      } finally {
        if (isCurrentRequest) {
          setIsLoading(false)
        }
      }
    }

    void loadConversation()

    return () => {
      isCurrentRequest = false
    }
  }, [activeConversationId])

  function selectConversation(conversationId: string): void {
    if (conversationId === activeConversationIdRef.current) {
      return
    }

    activeConversationIdRef.current = conversationId
    setActiveConversationId(conversationId)
    setActiveConversation(null)
    clearActionError()
    setLoadError(null)
    setIsLoading(true)
  }

  return {
    activeConversation,
    activeConversationId,
    approveConfirmation,
    error: actionError ?? loadError,
    isLoading,
    isSending,
    pendingUserMessage,
    processingConfirmationId,
    rejectConfirmation,
    selectConversation,
    sendMessage,
  }
}
