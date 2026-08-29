import { readSessionCache, removeSessionCache, writeSessionCache, type CacheEntry } from '../../shared/lib/sessionCache'
import type { McpConnectionStatus, McpTool } from './types'

const CONNECTION_STATUS_CACHE_TTL = 15 * 1000
const TOOLS_CACHE_TTL = 5 * 60 * 1000
const connectionStatusCache = new Map<string, CacheEntry<McpConnectionStatus>>()
const toolsCache = new Map<string, CacheEntry<McpTool[]>>()

function withFreshness<T>(entry: CacheEntry<T>, maxAge: number): CacheEntry<T> {
  return {
    ...entry,
    isFresh: Date.now() - entry.cachedAt < maxAge,
  }
}

function connectionStatusKey(serverName: string): string {
  return `integratrip:mcp:${serverName}:status`
}

function toolsKey(serverName: string): string {
  return `integratrip:mcp:${serverName}:tools`
}

function isConnectionStatus(value: unknown): value is McpConnectionStatus {
  return value === 'connected' || value === 'disconnected'
}

function isTools(value: unknown): value is McpTool[] {
  return Array.isArray(value)
}

export function getCachedConnectionStatus(
  serverName: string,
): CacheEntry<McpConnectionStatus> | null {
  const memoryValue = connectionStatusCache.get(serverName)

  if (memoryValue) {
    return withFreshness(memoryValue, CONNECTION_STATUS_CACHE_TTL)
  }

  const storageValue = readSessionCache(
    connectionStatusKey(serverName),
    CONNECTION_STATUS_CACHE_TTL,
    isConnectionStatus,
  )

  if (storageValue) {
    connectionStatusCache.set(serverName, storageValue)
  }

  return storageValue
}

export function saveConnectionStatus(
  serverName: string,
  status: McpConnectionStatus,
): void {
  const entry = { cachedAt: Date.now(), isFresh: true, value: status }
  connectionStatusCache.set(serverName, entry)
  writeSessionCache(connectionStatusKey(serverName), status)
}

export function getCachedTools(serverName: string): CacheEntry<McpTool[]> | null {
  const memoryValue = toolsCache.get(serverName)

  if (memoryValue) {
    return withFreshness(memoryValue, TOOLS_CACHE_TTL)
  }

  const storageValue = readSessionCache(
    toolsKey(serverName),
    TOOLS_CACHE_TTL,
    isTools,
  )

  if (storageValue) {
    toolsCache.set(serverName, storageValue)
  }

  return storageValue
}

export function saveTools(serverName: string, tools: McpTool[]): void {
  const entry = { cachedAt: Date.now(), isFresh: true, value: tools }
  toolsCache.set(serverName, entry)
  writeSessionCache(toolsKey(serverName), tools)
}

export function invalidateMcpServerCache(serverName: string): void {
  connectionStatusCache.delete(serverName)
  toolsCache.delete(serverName)
  removeSessionCache(connectionStatusKey(serverName))
  removeSessionCache(toolsKey(serverName))
}
