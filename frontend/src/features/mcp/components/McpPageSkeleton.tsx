import { Skeleton } from '../../../shared/ui'

export function McpPageSkeleton() {
  return (
    <div className="mx-auto grid w-full max-w-6xl gap-10" aria-label="Cargando contenido">
      <div className="grid gap-3">
        <Skeleton className="h-4 w-32" />
        <Skeleton className="h-12 w-72 max-w-full" />
        <Skeleton className="h-5 w-96 max-w-full" />
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {[0, 1, 2].map((item) => (
          <div
            className="grid min-h-52 content-between border-t border-slate-200 py-5"
            key={item}
          >
            <div className="grid gap-4">
              <Skeleton className="h-3 w-16" />
              <Skeleton className="h-7 w-36" />
              <Skeleton className="h-4 w-44" />
            </div>
            <Skeleton className="h-10 w-full" />
          </div>
        ))}
      </div>
    </div>
  )
}
