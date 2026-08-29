import { useState, type FormEvent } from 'react'

import { Button, TextInput } from '../../../shared/ui'
import type { JsonSchemaObject, JsonSchemaProperty, ToolArguments } from '../types'

type ToolFormProps = {
  inputSchema?: JsonSchemaObject
  isSubmitting: boolean
  onSubmit: (argumentsValue: ToolArguments) => Promise<void>
}

function propertyType(property: JsonSchemaProperty): string {
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

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function schemaProperties(inputSchema: JsonSchemaObject | undefined) {
  return isRecord(inputSchema?.properties) ? inputSchema.properties : {}
}

function isRequiredField(
  inputSchema: JsonSchemaObject | undefined,
  fieldName: string,
) {
  return inputSchema?.required?.includes(fieldName) ?? false
}

export function ToolForm({ inputSchema, isSubmitting, onSubmit }: ToolFormProps) {
  const properties = schemaProperties(inputSchema)
  const fields = Object.entries(properties)
  const [error, setError] = useState<string | null>(null)
  const [values, setValues] = useState<Record<string, string>>(() =>
    Object.fromEntries(
      fields.map(([fieldName, property]) => [
        fieldName,
        defaultValueFor(property),
      ]),
    ),
  )

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)

    try {
      const argumentsValue = fields.reduce<ToolArguments>(
        (nextArguments, [fieldName, property]) => {
          const value = values[fieldName] ?? ''

          if (!isRequiredField(inputSchema, fieldName) && value.trim() === '') {
            return nextArguments
          }

          return {
            ...nextArguments,
            [fieldName]: parseFieldValue(property, value),
          }
        },
        {},
      )

      await onSubmit(argumentsValue)
    } catch (submitError) {
      setError(
        submitError instanceof SyntaxError
          ? 'Hay un campo JSON con formato inválido.'
          : 'No se pudo ejecutar la tool.',
      )
    }
  }

  return (
    <form className="grid gap-4" onSubmit={handleSubmit}>
      {fields.length === 0 ? (
        <p className="m-0 text-sm text-slate-600">
          Esta tool no requiere argumentos.
        </p>
      ) : (
        fields.map(([fieldName, property]) => {
          const type = propertyType(property)
          const isRequired = isRequiredField(inputSchema, fieldName)
          const label = property.title ?? fieldName

          if (property.enum) {
            return (
              <label className="grid gap-1.5" htmlFor={fieldName} key={fieldName}>
                <span className="text-sm font-semibold text-slate-700">
                  {label}
                </span>
                <select
                  className="min-h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950"
                  id={fieldName}
                  name={fieldName}
                  onChange={(event) =>
                    setValues((currentValues) => ({
                      ...currentValues,
                      [fieldName]: event.target.value,
                    }))
                  }
                  required={isRequired}
                  value={values[fieldName] ?? ''}
                >
                  {!isRequired ? <option value="">Sin valor</option> : null}
                  {property.enum.map((option) => (
                    <option key={String(option)} value={String(option)}>
                      {String(option)}
                    </option>
                  ))}
                </select>
                {property.description ? (
                  <span className="text-xs text-slate-500">
                    {property.description}
                  </span>
                ) : null}
              </label>
            )
          }

          if (type === 'array' || type === 'object') {
            return (
              <label className="grid gap-1.5" htmlFor={fieldName} key={fieldName}>
                <span className="text-sm font-semibold text-slate-700">
                  {label}
                </span>
                <textarea
                  className="min-h-28 w-full rounded-md border border-slate-300 bg-white px-3 py-2 font-mono text-sm text-slate-950"
                  id={fieldName}
                  name={fieldName}
                  onChange={(event) =>
                    setValues((currentValues) => ({
                      ...currentValues,
                      [fieldName]: event.target.value,
                    }))
                  }
                  required={isRequired}
                  value={values[fieldName] ?? ''}
                />
                {property.description ? (
                  <span className="text-xs text-slate-500">
                    {property.description}
                  </span>
                ) : null}
              </label>
            )
          }

          return (
            <TextInput
              checked={type === 'boolean' ? values[fieldName] === 'true' : undefined}
              key={fieldName}
              label={label}
              name={fieldName}
              onChange={(event) =>
                setValues((currentValues) => ({
                  ...currentValues,
                  [fieldName]:
                    type === 'boolean'
                      ? String(event.target.checked)
                      : event.target.value,
                }))
              }
              required={isRequired}
              type={
                type === 'boolean'
                  ? 'checkbox'
                  : type === 'integer' || type === 'number'
                    ? 'number'
                    : 'text'
              }
              value={type === 'boolean' ? undefined : (values[fieldName] ?? '')}
            />
          )
        })
      )}

      {error ? <p className="m-0 text-sm text-red-600">{error}</p> : null}

      <Button disabled={isSubmitting} type="submit">
        {isSubmitting ? 'Ejecutando...' : 'Ejecutar tool'}
      </Button>
    </form>
  )
}
