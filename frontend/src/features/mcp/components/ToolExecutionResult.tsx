import type { CallServerToolResponse } from '../types'
import { resultBlocks } from '../utils/toolResult'
import { ResultData } from './ResultData'
import { ResultText } from './ResultText'

type ToolExecutionResultProps = {
  result: CallServerToolResponse
}

export function ToolExecutionResult({ result }: ToolExecutionResultProps) {
  const blocks = resultBlocks(result.output)

  return (
    <div className="grid gap-3">
      <p className="m-0 text-sm font-semibold tracking-[0.12em] text-slate-500 uppercase">
        Resultado
      </p>
      <div className="max-h-[32rem] min-w-0 overflow-auto rounded-md border border-slate-200 bg-white p-5 sm:p-6">
        <div className="grid gap-6">
          {blocks.map((block, index) =>
            block.kind === 'text' ? (
              <ResultText key={index} text={block.value} />
            ) : (
              <ResultData data={block.value} key={index} />
            ),
          )}
        </div>
      </div>
    </div>
  )
}
