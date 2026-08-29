import type { JsonSchemaObject, JsonSchemaProperty, ToolArguments } from '../types'

export type ToolSchemaField = [string, JsonSchemaProperty]

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function hasValue(value: string): boolean {
  return value.trim() !== ''
}

export function schemaFields(inputSchema: JsonSchemaObject | undefined): ToolSchemaField[] {
  return isRecord(inputSchema?.properties)
    ? Object.entries(inputSchema.properties)
    : []
}

export function propertyType(property: JsonSchemaProperty): string {
  return Array.isArray(property.type)
    ? property.type[0]
    : (property.type ?? 'string')
}

function defaultValueFor(property: JsonSchemaProperty): string {
  if (property.default === undefined) {
    return propertyType(property) === 'boolean' ? 'false' : ''
  }

  return typeof property.default === 'string'
    ? property.default
    : JSON.stringify(property.default)
}

function exampleValueFor(property: JsonSchemaProperty): unknown {
  if (property.examples?.[0] !== undefined) {
    return property.examples[0]
  }

  if (property.example !== undefined) {
    return property.example
  }

  if (property.default !== undefined) {
    return property.default
  }

  const type = propertyType(property)

  if (type === 'array') {
    return property.items ? [exampleValueFor(property.items)] : []
  }

  if (type === 'object') {
    return Object.fromEntries(
      Object.entries(property.properties ?? {}).map(([name, nestedProperty]) => [
        name,
        exampleValueFor(nestedProperty),
      ]),
    )
  }

  if (type === 'integer') {
    return property.minimum ?? 1
  }

  if (type === 'number') {
    return property.minimum ?? 1.5
  }

  if (type === 'boolean') {
    return true
  }

  if (property.format === 'date') {
    return '2026-01-31'
  }

  if (property.format === 'date-time') {
    return '2026-01-31T12:00:00Z'
  }

  if (property.format === 'email') {
    return 'nombre@ejemplo.com'
  }

  if (property.format === 'uri' || property.format === 'url') {
    return 'https://ejemplo.com'
  }

  return 'Texto de ejemplo'
}

export function fieldExample(property: JsonSchemaProperty): string | null {
  const type = propertyType(property)

  if (type === 'boolean' || property.enum) {
    return null
  }

  const example = exampleValueFor(property)
  return typeof example === 'string' ? example : JSON.stringify(example, null, 2)
}

export function fieldExpectation(property: JsonSchemaProperty): string {
  const type = propertyType(property)

  if (type === 'array') {
    return 'Ingresa una lista en formato JSON.'
  }

  if (type === 'object') {
    return 'Ingresa un objeto en formato JSON.'
  }

  if (type === 'integer') {
    return 'Ingresa un número entero.'
  }

  if (type === 'number') {
    return 'Ingresa un número.'
  }

  if (type === 'boolean') {
    return 'Activa la opción si corresponde.'
  }

  if (property.format === 'date') {
    return 'Formato esperado: AAAA-MM-DD.'
  }

  if (property.format === 'date-time') {
    return 'Formato esperado: fecha y hora ISO 8601.'
  }

  if (property.format === 'email') {
    return 'Formato esperado: correo electrónico.'
  }

  if (property.format === 'uri' || property.format === 'url') {
    return 'Formato esperado: URL completa.'
  }

  return 'Ingresa texto.'
}

export function initialFieldValues(
  fields: ToolSchemaField[],
): Record<string, string> {
  return Object.fromEntries(
    fields.map(([fieldName, property]) => [fieldName, defaultValueFor(property)]),
  )
}

export function isRequiredField(
  inputSchema: JsonSchemaObject | undefined,
  fieldName: string,
): boolean {
  return inputSchema?.required?.includes(fieldName) ?? false
}

function parsedJsonValue(value: string): unknown {
  try {
    return JSON.parse(value)
  } catch {
    return undefined
  }
}

export function fieldValidationError(
  property: JsonSchemaProperty,
  value: string,
  isRequired: boolean,
): string | null {
  if (!hasValue(value)) {
    return isRequired ? 'Este campo es obligatorio.' : null
  }

  const type = propertyType(property)

  if (type === 'integer' && !/^-?\d+$/.test(value)) {
    return 'Ingresa un número entero válido.'
  }

  if (type === 'number' && !Number.isFinite(Number(value))) {
    return 'Ingresa un número válido.'
  }

  if (type === 'integer' || type === 'number') {
    const numericValue = Number(value)

    if (property.minimum !== undefined && numericValue < property.minimum) {
      return `El valor mínimo es ${property.minimum}.`
    }

    if (property.maximum !== undefined && numericValue > property.maximum) {
      return `El valor máximo es ${property.maximum}.`
    }
  }

  if (type === 'string') {
    if (
      property.format === 'date-time' &&
      Number.isNaN(Date.parse(value))
    ) {
      return 'Ingresa una fecha y hora ISO 8601 válida.'
    }

    if (property.minLength !== undefined && value.length < property.minLength) {
      return `Debe tener al menos ${property.minLength} caracteres.`
    }

    if (property.maxLength !== undefined && value.length > property.maxLength) {
      return `Debe tener como máximo ${property.maxLength} caracteres.`
    }

    if (property.pattern) {
      try {
        if (!new RegExp(property.pattern).test(value)) {
          return 'El formato no cumple el patrón requerido.'
        }
      } catch {
        return null
      }
    }
  }

  if (type === 'array' || type === 'object') {
    const parsedValue = parsedJsonValue(value)

    if (parsedValue === undefined) {
      return 'El contenido debe ser JSON válido.'
    }

    if (type === 'array' && !Array.isArray(parsedValue)) {
      return 'El contenido debe ser una lista JSON.'
    }

    if (type === 'object' && !isRecord(parsedValue)) {
      return 'El contenido debe ser un objeto JSON.'
    }
  }

  return null
}

function parseFieldValue(property: JsonSchemaProperty, value: string): unknown {
  const type = propertyType(property)

  if (type === 'boolean') {
    return value === 'true'
  }

  if (type === 'integer') {
    return Number.parseInt(value, 10)
  }

  if (type === 'number') {
    return Number(value)
  }

  if (type === 'array' || type === 'object') {
    return value.trim() === '' ? undefined : JSON.parse(value)
  }

  return value
}

export function toolArgumentsFromFields(
  fields: ToolSchemaField[],
  inputSchema: JsonSchemaObject | undefined,
  values: Record<string, string>,
): ToolArguments {
  return fields.reduce<ToolArguments>((argumentsValue, [fieldName, property]) => {
    const value = values[fieldName] ?? ''

    if (!isRequiredField(inputSchema, fieldName) && !hasValue(value)) {
      return argumentsValue
    }

    return {
      ...argumentsValue,
      [fieldName]: parseFieldValue(property, value),
    }
  }, {})
}
