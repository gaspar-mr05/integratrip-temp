import { useEffect, useState } from 'react'

import { getConversation } from '../api'
import type { ConversationDetail } from '../types'

export function useActiveConversation() {
  const [activeConversationId, setActiveConversationId] = useState<string | null>(
    null,
  )

  const [activeConversation, setActiveConversation] =
    useState<ConversationDetail | null>(null)

  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    if (activeConversationId === null) {
      return
    }

    const conversationId = activeConversationId
    let isMounted = true

    async function loadConversation(): Promise<void> {
      try {
        const conversation = await getConversation(conversationId)

        if (isMounted) {
          setActiveConversation(conversation)
        }
      } catch (currentError) {
        if (isMounted) {
          setError(
            currentError instanceof Error
              ? currentError
              : new Error('No se pudo cargar la conversación'),
          )
        }
      } finally {
        if (isMounted) {
          setIsLoading(false)
        }
      }
    }

    void loadConversation()

    return () => {
      isMounted = false
    }
  }, [activeConversationId])

  function selectConversation(conversationId: string): void {
    if (conversationId === activeConversationId) {
      return
    }

    setActiveConversationId(conversationId)
    setActiveConversation(null)
    setError(null)
    setIsLoading(true)
  }

  return {
    activeConversation,
    activeConversationId,
    error,
    isLoading,
    selectConversation,
  }
}
