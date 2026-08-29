import { Skeleton } from '../../../shared/ui'

export function ToolsListSkeleton() {
  return (
    <div className="grid gap-2 pt-1" aria-label="Cargando tools">
      <Skeleton className="h-4 w-3/4" />
      <Skeleton className="h-4 w-2/3" />
      <Skeleton className="h-4 w-4/5" />
    </div>
  )
}
