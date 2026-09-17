import { useEffect, useState } from 'react'

import {
  createConversation as createConversationRequest,
  listConversations,
} from '../api'
import type { Conversation, ConversationSummary } from '../types'

export function useConversations() {
  const [conversations, setConversations] = useState<ConversationSummary[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isCreating, setIsCreating] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    let isMounted = true

    async function loadConversations(): Promise<void> {
      try {
        const loadedConversations = await listConversations()

        if (isMounted) {
          setConversations(loadedConversations)
        }
      } catch (currentError) {
        if (isMounted) {
          setError(
            currentError instanceof Error
              ? currentError
              : new Error('No se pudieron cargar las conversaciones'),
          )
        }
      } finally {
        if (isMounted) {
          setIsLoading(false)
        }
      }
    }

    void loadConversations()

    return () => {
      isMounted = false
    }
  }, [])

  async function createConversation(): Promise<Conversation | null> {
    setIsCreating(true)
    setError(null)

    try {
      const createdConversation = await createConversationRequest()
      setConversations((currentConversations) => [
        createdConversation,
        ...currentConversations,
      ])
      return createdConversation
    } catch (currentError) {
      setError(
        currentError instanceof Error
          ? currentError
          : new Error('No se pudo crear la conversación'),
      )
      return null
    } finally {
      setIsCreating(false)
    }
  }

  return {
    conversations,
    createConversation,
    error,
    isCreating,
    isLoading,
  }
}
