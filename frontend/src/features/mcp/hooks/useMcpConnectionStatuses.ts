import { useEffect, useState } from 'react'

import { getMcpConnectionStatus } from '../api'
import { getCachedConnectionStatus, saveConnectionStatus } from '../mcpCache'
import type { McpConnectionStatus } from '../types'

type McpConnectionStatuses = Record<string, McpConnectionStatus>

function cachedStatuses(serverNames: string[]): McpConnectionStatuses {
  return Object.fromEntries(
    serverNames.flatMap((serverName) => {
      const cachedStatus = getCachedConnectionStatus(serverName)
      return cachedStatus ? [[serverName, cachedStatus.value]] : []
    }),
  )
}

export function useMcpConnectionStatuses(
  serverNames: string[],
): McpConnectionStatuses {
  const [statuses, setStatuses] = useState<McpConnectionStatuses>(() =>
    cachedStatuses(serverNames),
  )

  useEffect(() => {
    let isMounted = true

    const serverNamesToRefresh = serverNames.filter(
      (serverName) => !getCachedConnectionStatus(serverName)?.isFresh,
    )

    if (serverNamesToRefresh.length === 0) {
      return
    }

    Promise.all(
      serverNamesToRefresh.map(async (serverName) => {
        try {
          const response = await getMcpConnectionStatus(serverName)
          saveConnectionStatus(serverName, response.status)
          return [serverName, response.status] as const
        } catch {
          return null
        }
      }),
    ).then((connectionStatuses) => {
      if (!isMounted) {
        return
      }

      const refreshedStatuses = connectionStatuses.filter(
        (status): status is readonly [string, McpConnectionStatus] => status !== null,
      )

      setStatuses((currentStatuses) => ({
        ...currentStatuses,
        ...Object.fromEntries(refreshedStatuses),
      }))
    })

    return () => {
      isMounted = false
    }
  }, [serverNames])

  return statuses
}
