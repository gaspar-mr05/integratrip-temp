import { TextInput } from '../../../shared/ui'
import type { JsonSchemaProperty } from '../types'
import { fieldExample, fieldExpectation, propertyType } from '../utils/toolSchema'
import { FieldHint } from './FieldHint'

type ToolFieldProps = {
  error?: string
  fieldName: string
  isRequired: boolean
  onChange: (value: string) => void
  property: JsonSchemaProperty
  value: string
}

function inputType(property: JsonSchemaProperty): string {
  if (property.format === 'date' || property.format === 'email') {
    return property.format
  }

  if (property.format === 'uri' || property.format === 'url') {
    return 'url'
  }

  const type = propertyType(property)
  return type === 'integer' || type === 'number' ? 'number' : 'text'
}

export function ToolField({
  error,
  fieldName,
  isRequired,
  onChange,
  property,
  value,
}: ToolFieldProps) {
  const type = propertyType(property)
  const label = property.title ?? fieldName
  const example = fieldExample(property)
  const hintId = `${fieldName}-help`
  const hasError = error !== undefined
  const controlClassName = hasError
    ? 'border-red-500 hover:border-red-600 focus:border-red-600 focus:ring-red-100'
    : ''

  const hint = (
    <FieldHint
      description={property.description}
      error={error}
      example={example}
      expectation={fieldExpectation(property)}
      id={hintId}
      isRequired={isRequired}
      onUseExample={example ? () => onChange(example) : null}
    />
  )

  if (property.enum) {
    return (
      <div className="grid gap-2">
        <label className="text-sm font-medium text-slate-700" htmlFor={fieldName}>
          {label}
        </label>
        <select
          aria-describedby={hintId}
          aria-invalid={hasError}
          className={`min-h-11 w-full rounded-md border border-slate-300 bg-white px-3 text-slate-950 outline-none transition-colors hover:border-slate-400 focus:border-blue-600 focus:ring-2 focus:ring-blue-100 ${controlClassName}`.trim()}
          id={fieldName}
          name={fieldName}
          onChange={(event) => onChange(event.target.value)}
          required={isRequired}
          value={value}
        >
          {!isRequired ? <option value="">Sin valor</option> : null}
          {property.enum.map((option) => (
            <option key={String(option)} value={String(option)}>
              {String(option)}
            </option>
          ))}
        </select>
        {hint}
      </div>
    )
  }

  if (type === 'array' || type === 'object') {
    return (
      <div className="grid gap-2">
        <label className="text-sm font-medium text-slate-700" htmlFor={fieldName}>
          {label}
        </label>
        <textarea
          aria-describedby={hintId}
          aria-invalid={hasError}
          className={`min-h-32 w-full resize-y rounded-md border border-slate-300 bg-white px-3 py-2.5 font-mono text-sm leading-6 text-slate-950 outline-none transition-colors placeholder:text-slate-400 hover:border-slate-400 focus:border-blue-600 focus:ring-2 focus:ring-blue-100 ${controlClassName}`.trim()}
          id={fieldName}
          name={fieldName}
          onChange={(event) => onChange(event.target.value)}
          placeholder={example ?? undefined}
          required={isRequired}
          value={value}
        />
        {hint}
      </div>
    )
  }

  if (type === 'boolean') {
    return (
      <div className="grid gap-2">
        <TextInput
          aria-describedby={hintId}
          aria-invalid={hasError}
          checked={value === 'true'}
          inputClassName={controlClassName}
          label={label}
          name={fieldName}
          onChange={(event) => onChange(String(event.target.checked))}
          type="checkbox"
        />
        {hint}
      </div>
    )
  }

  return (
    <div className="grid gap-2">
      <TextInput
        aria-describedby={hintId}
        aria-invalid={hasError}
        inputClassName={controlClassName}
        label={label}
        max={property.maximum}
        maxLength={property.maxLength}
        min={property.minimum}
        minLength={property.minLength}
        name={fieldName}
        onChange={(event) => onChange(event.target.value)}
        pattern={property.pattern}
        placeholder={example ?? undefined}
        required={isRequired}
        step={type === 'integer' ? 1 : undefined}
        type={inputType(property)}
        value={value}
      />
      {hint}
    </div>
  )
}
