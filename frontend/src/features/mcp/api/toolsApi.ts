import { requestJson } from '../../../shared/api'
import type {
  CallServerToolResponse,
  ListServerToolsResponse,
  ToolArguments,
} from '../types'

export function listServerTools(
  serverName: string,
): Promise<ListServerToolsResponse> {
  return requestJson<ListServerToolsResponse>(`/mcp/${serverName}/tools`)
}

export function callServerTool(
  serverName: string,
  toolName: string,
  toolArguments: ToolArguments,
): Promise<CallServerToolResponse> {
  return requestJson<CallServerToolResponse>(
    `/mcp/${serverName}/tools/${toolName}/call`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(toolArguments),
    },
  )
}
