import type { PendingConfirmation } from '../types'
import { ConfirmationCard } from './ConfirmationCard'

type PendingConfirmationsProps = {
  pendingConfirmations: readonly PendingConfirmation[]
  processingConfirmationId: string | null
  onApprove: (confirmationId: string) => void
  onReject: (confirmationId: string) => void
}

export function PendingConfirmations({
  pendingConfirmations,
  processingConfirmationId,
  onApprove,
  onReject,
}: PendingConfirmationsProps) {
  if (pendingConfirmations.length === 0) {
    return null
  }

  const isAnyConfirmationProcessing = processingConfirmationId !== null

  return (
    <section aria-label="Confirmaciones pendientes">
      <ul className="m-0 grid list-none gap-4 p-0">
        {pendingConfirmations.map((confirmation) => (
          <li key={confirmation.id}>
            <ConfirmationCard
              isDisabled={isAnyConfirmationProcessing}
              isProcessing={processingConfirmationId === confirmation.id}
              onApprove={() => onApprove(confirmation.id)}
              onReject={() => onReject(confirmation.id)}
              pendingConfirmation={confirmation}
            />
          </li>
        ))}
      </ul>
    </section>
  )
}
