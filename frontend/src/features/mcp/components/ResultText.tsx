import { structuredText } from '../utils/toolResult'
import { ResultData } from './ResultData'

type ResultTextProps = {
  text: string
}

export function ResultText({ text }: ResultTextProps) {
  const data = structuredText(text)

  if (data !== null) {
    return <ResultData data={data} />
  }

  return (
    <p className="m-0 whitespace-pre-wrap break-words text-[0.95rem] leading-7 text-slate-700">
      {text}
    </p>
  )
}
