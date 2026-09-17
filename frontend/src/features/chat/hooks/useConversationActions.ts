import { useRef, useState } from 'react'

import {
  approveConfirmation as approveConfirmationRequest,
  getConversation,
  rejectConfirmation as rejectConfirmationRequest,
  sendMessage as sendMessageRequest,
} from '../api'
import type { ConversationDetail, ConversationTurnResponse } from '../types'
import { normalizeError } from '../utils'

type ConversationRequest = (
  conversationId: string,
) => Promise<ConversationTurnResponse>

type ConfirmationRequest = (
  conversationId: string,
  confirmationId: string,
) => Promise<ConversationTurnResponse>

type ConversationMutation =
  | { type: 'idle' }
  | { type: 'sending' }
  | { confirmationId: string; type: 'confirmation' }

type ConversationActionError = {
  conversationId: string
  error: Error
}

type PendingUserMessage = {
  conversationId: string
  text: string
}

type UseConversationActionsOptions = {
  conversationId: string | null
  hasPendingConfirmations: boolean
  onConversationUpdated: (
    conversationId: string,
    detail: ConversationDetail,
  ) => void
}

const idleMutation: ConversationMutation = { type: 'idle' }

export function useConversationActions({
  conversationId,
  hasPendingConfirmations,
  onConversationUpdated,
}: UseConversationActionsOptions) {
  const [actionError, setActionError] =
    useState<ConversationActionError | null>(null)
  const [mutation, setMutation] =
    useState<ConversationMutation>(idleMutation)
  const [pendingUserMessage, setPendingUserMessage] =
    useState<PendingUserMessage | null>(null)
  const mutationRef = useRef<ConversationMutation>(idleMutation)

  function startMutation(nextMutation: ConversationMutation): boolean {
    if (mutationRef.current.type !== 'idle') {
      return false
    }

    mutationRef.current = nextMutation
    setMutation(nextMutation)
    setActionError(null)
    return true
  }

  function finishMutation(): void {
    mutationRef.current = idleMutation
    setMutation(idleMutation)
  }

  function clearError(): void {
    setActionError(null)
  }

  async function executeMutation(
    nextMutation: ConversationMutation,
    request: ConversationRequest,
    fallbackMessage: string,
    optimisticUserText?: string,
  ): Promise<boolean> {
    if (conversationId === null || !startMutation(nextMutation)) {
      return false
    }

    if (optimisticUserText !== undefined) {
      setPendingUserMessage({
        conversationId,
        text: optimisticUserText,
      })
    }

    try {
      await request(conversationId)
      const detail = await getConversation(conversationId)

      onConversationUpdated(conversationId, detail)
      return true
    } catch (currentError) {
      setActionError({
        conversationId,
        error: normalizeError(currentError, fallbackMessage),
      })
      return false
    } finally {
      setPendingUserMessage(null)
      finishMutation()
    }
  }

  async function sendMessage(text: string): Promise<boolean> {
    const normalizedText = text.trim()

    if (normalizedText.length === 0 || hasPendingConfirmations) {
      return false
    }

    return executeMutation(
      { type: 'sending' },
      (currentConversationId) =>
        sendMessageRequest(currentConversationId, normalizedText),
      'No se pudo enviar el mensaje',
      normalizedText,
    )
  }

  function processConfirmation(
    confirmationId: string,
    action: ConfirmationRequest,
    fallbackErrorMessage: string,
  ): Promise<boolean> {
    return executeMutation(
      { confirmationId, type: 'confirmation' },
      (currentConversationId) =>
        action(currentConversationId, confirmationId),
      fallbackErrorMessage,
    )
  }

  function approveConfirmation(confirmationId: string): Promise<boolean> {
    return processConfirmation(
      confirmationId,
      approveConfirmationRequest,
      'No se pudo aprobar la confirmación',
    )
  }

  function rejectConfirmation(confirmationId: string): Promise<boolean> {
    return processConfirmation(
      confirmationId,
      rejectConfirmationRequest,
      'No se pudo rechazar la confirmación',
    )
  }

  return {
    approveConfirmation,
    clearError,
    error:
      actionError?.conversationId === conversationId ? actionError.error : null,
    isSending: mutation.type === 'sending',
    processingConfirmationId:
      mutation.type === 'confirmation' ? mutation.confirmationId : null,
    pendingUserMessage:
      pendingUserMessage?.conversationId === conversationId
        ? pendingUserMessage.text
        : null,
    rejectConfirmation,
    sendMessage,
  }
}
