import { requestJson } from '../../../shared/api'
import type {
  Conversation,
  ConversationDetail,
  ConversationSummary,
  ConversationTurnResponse,
} from '../types'

export function listConversations(): Promise<ConversationSummary[]> {
  return requestJson<ConversationSummary[]>('/conversations')
}

export function createConversation(): Promise<Conversation> {
  return requestJson<Conversation>('/conversations', {
    method: 'POST',
  })
}

export function getConversation(
  conversationId: string,
): Promise<ConversationDetail> {
  return requestJson<ConversationDetail>(`/conversations/${conversationId}`)
}

export function sendMessage(
  conversationId: string,
  text: string,
): Promise<ConversationTurnResponse> {
  return requestJson<ConversationTurnResponse>(
    `/conversations/${conversationId}/messages`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text }),
    },
  )
}

export function approveConfirmation(
  conversationId: string,
  confirmationId: string,
): Promise<ConversationTurnResponse> {
  return requestJson<ConversationTurnResponse>(
    `/conversations/${conversationId}/confirmations/${confirmationId}/approve`,
    {
      method: 'POST',
    },
  )
}

export function rejectConfirmation(
  conversationId: string,
  confirmationId: string,
): Promise<ConversationTurnResponse> {
  return requestJson<ConversationTurnResponse>(
    `/conversations/${conversationId}/confirmations/${confirmationId}/reject`,
    {
      method: 'POST',
    },
  )
}
