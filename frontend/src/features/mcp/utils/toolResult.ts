export type ToolResultBlock =
  | { kind: 'data'; value: unknown }
  | { kind: 'text'; value: string }

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function isEmptyDisplayValue(value: unknown): boolean {
  if (value === null || value === undefined) {
    return true
  }

  if (typeof value === 'string') {
    return value.trim() === ''
  }

  if (Array.isArray(value)) {
    return value.length === 0
  }

  if (isRecord(value)) {
    return Object.keys(value).length === 0
  }

  return false
}

function textBlocksFromContent(value: unknown): ToolResultBlock[] {
  if (!Array.isArray(value)) {
    return []
  }

  return value.flatMap((content) =>
    isRecord(content) && typeof content.text === 'string' && content.text.trim() !== ''
      ? [{ kind: 'text' as const, value: content.text }]
      : [],
  )
}

function isEmptyContent(value: unknown): boolean {
  return (
    Array.isArray(value) &&
    (value.length === 0 ||
      value.every(
        (content) =>
          isRecord(content) &&
          typeof content.text === 'string' &&
          content.text.trim() === '',
      ))
  )
}

export function resultBlocks(output: unknown): ToolResultBlock[] {
  if (isEmptyDisplayValue(output)) {
    return []
  }

  if (!isRecord(output)) {
    return [{ kind: 'data', value: output }]
  }

  const textBlocks = textBlocksFromContent(output.content)

  if (textBlocks.length > 0) {
    return textBlocks
  }

  if ('structuredContent' in output) {
    return isEmptyDisplayValue(output.structuredContent)
      ? []
      : [{ kind: 'data', value: output.structuredContent }]
  }

  if (isEmptyContent(output.content)) {
    return []
  }

  return [{ kind: 'data', value: output }]
}

export function structuredText(value: string): unknown | null {
  const trimmedValue = value.trim()

  if (!trimmedValue.startsWith('{') && !trimmedValue.startsWith('[')) {
    return null
  }

  try {
    return JSON.parse(trimmedValue) as unknown
  } catch {
    return null
  }
}

export function displayName(value: string): string {
  return value
    .replace(/([a-z])([A-Z])/g, '$1 $2')
    .replace(/[_-]/g, ' ')
    .replace(/^./, (character) => character.toUpperCase())
}

export function isRecordList(value: unknown): value is Record<string, unknown>[] {
  return Array.isArray(value) && value.length > 0 && value.every(isRecord)
}

export function displayValue(value: unknown): string {
  if (value === null || value === undefined) {
    return '—'
  }

  if (typeof value === 'boolean') {
    return value ? 'Sí' : 'No'
  }

  if (Array.isArray(value)) {
    return `${value.length} elementos`
  }

  if (isRecord(value)) {
    return 'Información disponible'
  }

  return String(value)
}
