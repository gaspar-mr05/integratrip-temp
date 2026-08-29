import { Skeleton } from '../../../shared/ui'

export function ToolFormSkeleton() {
  return (
    <div className="grid gap-6" aria-label="Cargando formulario">
      {[0, 1, 2].map((item) => (
        <div className="grid gap-2" key={item}>
          <Skeleton className="h-4 w-28" />
          <Skeleton className="h-11 w-full" />
          <Skeleton className="h-3 w-3/5" />
        </div>
      ))}
      <Skeleton className="h-10 w-36" />
    </div>
  )
}
