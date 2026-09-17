export type ConversationSummary = {
  id: string
  title: string
  created_at: string
  updated_at: string
}

export type Conversation = {
  id: string
  title: string
  created_at: string
  updated_at: string
  user_id: string
}

export type MessageRole = 'user' | 'model' | 'tool'

export type FunctionCall = {
  id: string
  name: string
  arguments_json: string
}

export type FunctionResult = {
  id: string
  name: string
  result_json: string
  is_error: boolean
}

export type ChatMessage = {
  id: string
  conversation_id: string
  sequence: number
  role: MessageRole
  text: string
  function_calls: FunctionCall[]
  function_results: FunctionResult[]
  created_at: string
}

export type PendingConfirmation = {
  id: string
  conversation_id: string
  model_message_id: string
  function_call_id: string
  llm_name: string
  arguments_json: Record<string, unknown>
  status: 'pending'
}

export type ConversationDetail = {
  conversation: Conversation
  messages: ChatMessage[]
  pending_confirmations: PendingConfirmation[]
}

export type ConversationTurnResponse = {
  text: string
  pending_confirmations: PendingConfirmation[]
}
