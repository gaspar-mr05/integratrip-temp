import { useState, type FormEvent } from 'react'

import { Button, ErrorMessage } from '../../../shared/ui'
import type { JsonSchemaObject, ToolArguments } from '../types'
import {
  fieldValidationError,
  initialFieldValues,
  isRequiredField,
  schemaFields,
  toolArgumentsFromFields,
} from '../utils/toolSchema'
import { ToolField } from './ToolField'

type ToolFormProps = {
  inputSchema?: JsonSchemaObject
  isSubmitting: boolean
  onSubmit: (argumentsValue: ToolArguments) => Promise<void>
}

export function ToolForm({ inputSchema, isSubmitting, onSubmit }: ToolFormProps) {
  const fields = schemaFields(inputSchema)
  const [error, setError] = useState<string | null>(null)
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({})
  const [values, setValues] = useState<Record<string, string>>(() =>
    initialFieldValues(fields),
  )

  function handleFieldChange(fieldName: string, value: string): void {
    setValues((currentValues) => ({
      ...currentValues,
      [fieldName]: value,
    }))
    setFieldErrors((currentErrors) => {
      const { [fieldName]: _, ...remainingErrors } = currentErrors
      return remainingErrors
    })
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)

    const nextFieldErrors = Object.fromEntries(
      fields.flatMap(([fieldName, property]) => {
        const fieldError = fieldValidationError(
          property,
          values[fieldName] ?? '',
          isRequiredField(inputSchema, fieldName),
        )

        return fieldError ? [[fieldName, fieldError]] : []
      }),
    )

    if (Object.keys(nextFieldErrors).length > 0) {
      setFieldErrors(nextFieldErrors)
      return
    }

    setFieldErrors({})

    try {
      await onSubmit(toolArgumentsFromFields(fields, inputSchema, values))
    } catch (submitError) {
      setError(
        submitError instanceof SyntaxError
          ? 'Hay un campo JSON con formato inválido.'
          : 'No se pudo ejecutar la tool.',
      )
    }
  }

  return (
    <form className="grid gap-6" onSubmit={handleSubmit}>
      {fields.length === 0 ? (
        <p className="m-0 text-sm leading-6 text-slate-600">
          Esta tool no requiere argumentos.
        </p>
      ) : (
        fields.map(([fieldName, property]) => (
          <ToolField
            fieldName={fieldName}
            error={fieldErrors[fieldName]}
            isRequired={isRequiredField(inputSchema, fieldName)}
            key={fieldName}
            onChange={(value) => handleFieldChange(fieldName, value)}
            property={property}
            value={values[fieldName] ?? ''}
          />
        ))
      )}

      {error ? <ErrorMessage message={error} /> : null}

      <Button className="w-full sm:w-fit" disabled={isSubmitting} type="submit">
        {isSubmitting ? 'Ejecutando...' : 'Ejecutar tool'}
      </Button>
    </form>
  )
}
