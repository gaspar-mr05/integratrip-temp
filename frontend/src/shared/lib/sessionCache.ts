type CachedValue<T> = {
  cachedAt: number
  value: T
}

export type CacheEntry<T> = {
  cachedAt: number
  isFresh: boolean
  value: T
}

function canUseSessionStorage(): boolean {
  return typeof window !== 'undefined' && 'sessionStorage' in window
}

export function readSessionCache<T>(
  key: string,
  maxAge: number,
  isValue: (value: unknown) => value is T,
): CacheEntry<T> | null {
  if (!canUseSessionStorage()) {
    return null
  }

  try {
    const rawValue = window.sessionStorage.getItem(key)

    if (!rawValue) {
      return null
    }

    const cachedValue: unknown = JSON.parse(rawValue)

    if (
      typeof cachedValue !== 'object' ||
      cachedValue === null ||
      !('cachedAt' in cachedValue) ||
      !('value' in cachedValue) ||
      typeof cachedValue.cachedAt !== 'number' ||
      !isValue(cachedValue.value)
    ) {
      window.sessionStorage.removeItem(key)
      return null
    }

    return {
      cachedAt: cachedValue.cachedAt,
      isFresh: Date.now() - cachedValue.cachedAt < maxAge,
      value: cachedValue.value,
    }
  } catch {
    return null
  }
}

export function writeSessionCache<T>(key: string, value: T): void {
  if (!canUseSessionStorage()) {
    return
  }

  const cachedValue: CachedValue<T> = { cachedAt: Date.now(), value }

  try {
    window.sessionStorage.setItem(key, JSON.stringify(cachedValue))
  } catch {
    // La caché es opcional; la aplicación continúa usando los datos remotos.
  }
}

export function removeSessionCache(key: string): void {
  if (!canUseSessionStorage()) {
    return
  }

  try {
    window.sessionStorage.removeItem(key)
  } catch {
    // La caché es opcional; no hay nada más que limpiar.
  }
}
