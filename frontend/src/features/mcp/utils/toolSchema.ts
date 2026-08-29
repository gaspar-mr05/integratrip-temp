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

function valueMatchesStringConstraints(
  property: JsonSchemaProperty,
  value: string,
): boolean {
  if (property.minLength !== undefined && value.length < property.minLength) {
    return false
  }

  if (property.maxLength !== undefined && value.length > property.maxLength) {
    return false
  }

  if (!property.pattern) {
    return true
  }

  try {
    return new RegExp(property.pattern).test(value)
  } catch {
    return false
  }
}

function formattedStringExample(property: JsonSchemaProperty): string | undefined {
  const examplesByFormat: Record<string, string> = {
    date: '2026-01-31',
    'date-time': '2026-01-31T12:00:00Z',
    email: 'nombre@ejemplo.com',
    hostname: 'ejemplo.com',
    ipv4: '192.0.2.1',
    ipv6: '2001:db8::1',
    time: '12:00:00',
    uri: 'https://ejemplo.com',
    url: 'https://ejemplo.com',
    uuid: '123e4567-e89b-12d3-a456-426614174000',
  }

  const example = property.format ? examplesByFormat[property.format] : undefined

  if (!example || !valueMatchesStringConstraints(property, example)) {
    return undefined
  }

  return example
}

function descriptionExample(property: JsonSchemaProperty): string | undefined {
  const description = property.description

  if (!description) {
    return undefined
  }

  const explicitExample = description.match(
    /(?:e\.g\.|eg|example|ej\.|ejemplo)\s*:?\s*["'`]?([^"',;.)\s`]+)/i,
  )?.[1]

  if (explicitExample && valueMatchesStringConstraints(property, explicitExample)) {
    return explicitExample
  }

  if (/yyyy-mm-dd/i.test(description)) {
    const example = '2026-01-31'
    return valueMatchesStringConstraints(property, example) ? example : undefined
  }

  if (/\biata\b/i.test(description)) {
    const example = 'SCL'
    return valueMatchesStringConstraints(property, example) ? example : undefined
  }

  return undefined
}

function numericExample(property: JsonSchemaProperty): number | undefined {
  const type = propertyType(property)
  const minimum = property.minimum
  const maximum = property.maximum

  if (minimum !== undefined && maximum !== undefined && minimum > maximum) {
    return undefined
  }

  if (type === 'integer') {
    const lowerBound = minimum === undefined ? Number.NEGATIVE_INFINITY : Math.ceil(minimum)
    const upperBound = maximum === undefined ? Number.POSITIVE_INFINITY : Math.floor(maximum)

    if (lowerBound > upperBound) {
      return undefined
    }

    const example = Math.min(Math.max(1, lowerBound), upperBound)
    return Number.isFinite(example) ? example : undefined
  }

  return Math.min(
    Math.max(1.5, minimum ?? Number.NEGATIVE_INFINITY),
    maximum ?? Number.POSITIVE_INFINITY,
  )
}

function objectExample(property: JsonSchemaProperty): Record<string, unknown> | undefined {
  if (!isRecord(property.properties)) {
    return undefined
  }

  const entries: [string, unknown][] = []

  for (const [name, nestedProperty] of Object.entries(property.properties)) {
    const example = exampleValueFor(nestedProperty)

    if (example !== undefined) {
      entries.push([name, example])
    } else if (property.required?.includes(name)) {
      return undefined
    }
  }

  return entries.length > 0 ? Object.fromEntries(entries) : undefined
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

  if (property.const !== undefined) {
    return property.const
  }

  if (property.enum?.[0] !== undefined) {
    return property.enum[0]
  }

  const type = propertyType(property)

  if (type === 'array') {
    const itemExample = property.items ? exampleValueFor(property.items) : undefined
    return itemExample === undefined ? undefined : [itemExample]
  }

  if (type === 'object') {
    return objectExample(property)
  }

  if (type === 'integer' || type === 'number') {
    return numericExample(property)
  }

  if (type === 'boolean') {
    return true
  }

  if (type === 'string') {
    return formattedStringExample(property) ?? descriptionExample(property)
  }

  return undefined
}

export function fieldExample(property: JsonSchemaProperty): string | null {
  const type = propertyType(property)

  if (type === 'boolean' || property.enum) {
    return null
  }

  const example = exampleValueFor(property)
  if (example === undefined) {
    return null
  }

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

  if (property.format === 'hostname') {
    return 'Formato esperado: nombre de host.'
  }

  if (property.format === 'ipv4') {
    return 'Formato esperado: dirección IPv4.'
  }

  if (property.format === 'ipv6') {
    return 'Formato esperado: dirección IPv6.'
  }

  if (property.format === 'time') {
    return 'Formato esperado: hora.'
  }

  if (property.format === 'uri' || property.format === 'url') {
    return 'Formato esperado: URL completa.'
  }

  if (property.format === 'uuid') {
    return 'Formato esperado: UUID.'
  }

  if (property.pattern) {
    return `Debe cumplir el patrón: ${property.pattern}.`
  }

  if (property.description && /\biata\b/i.test(property.description)) {
    return 'Formato esperado: código IATA.'
  }

  if (property.description && /yyyy-mm-dd/i.test(property.description)) {
    return 'Formato esperado: AAAA-MM-DD.'
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
