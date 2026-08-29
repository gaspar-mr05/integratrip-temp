import { useEffect, useState } from 'react'

import { getMcpConnectionStatus } from '../api'
import type { McpConnectionStatus } from '../types'

type McpConnectionStatuses = Record<string, McpConnectionStatus>

export function useMcpConnectionStatuses(
  serverNames: string[],
): McpConnectionStatuses {
  const [statuses, setStatuses] = useState<McpConnectionStatuses>({})

  useEffect(() => {
    let isMounted = true

    Promise.all(
      serverNames.map(async (serverName) => {
        try {
          const response = await getMcpConnectionStatus(serverName)
          return [serverName, response.status] as const
        } catch {
          return [serverName, 'disconnected'] as const
        }
      }),
    ).then((connectionStatuses) => {
      if (!isMounted) {
        return
      }

      setStatuses(Object.fromEntries(connectionStatuses))
    })

    return () => {
      isMounted = false
    }
  }, [serverNames])

  return statuses
}
