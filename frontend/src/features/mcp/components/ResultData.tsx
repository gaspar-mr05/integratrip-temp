import { displayName, displayValue, isRecordList } from '../utils/toolResult'

type ResultDataProps = {
  data: unknown
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function tableColumns(rows: Record<string, unknown>[]): string[] {
  return [...new Set(rows.flatMap((row) => Object.keys(row)))]
}

export function ResultData({ data }: ResultDataProps) {
  if (isRecordList(data)) {
    const columns = tableColumns(data)

    return (
      <div className="max-w-full overflow-x-auto">
        <table className="min-w-full border-collapse text-left text-sm">
          <thead className="border-b border-slate-200 text-xs font-semibold tracking-[0.08em] text-slate-500 uppercase">
            <tr>
              {columns.map((column) => (
                <th className="whitespace-nowrap px-3 py-3 first:pl-0 last:pr-0" key={column} scope="col">
                  {displayName(column)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-slate-700">
            {data.map((row, index) => (
              <tr key={index}>
                {columns.map((column) => {
                  const value = row[column]

                  return (
                    <td className="max-w-72 px-3 py-3 align-top leading-6 break-words first:pl-0 last:pr-0" key={column}>
                      {Array.isArray(value) || isRecord(value) ? (
                        <ResultData data={value} />
                      ) : (
                        displayValue(value)
                      )}
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    )
  }

  if (Array.isArray(data)) {
    return (
      <ul className="m-0 grid list-none gap-2 p-0 text-[0.95rem] leading-7 text-slate-700">
        {data.map((item, index) => (
          <li className="border-l-2 border-blue-200 pl-3" key={index}>
            {displayValue(item)}
          </li>
        ))}
      </ul>
    )
  }

  if (isRecord(data)) {
    return (
      <div className="grid gap-6">
        {Object.entries(data).map(([name, value]) => (
          <section className="grid gap-2" key={name}>
            <h3 className="m-0 text-sm font-semibold text-slate-800">
              {displayName(name)}
            </h3>
            <ResultData data={value} />
          </section>
        ))}
      </div>
    )
  }

  return <p className="m-0 text-[0.95rem] leading-7 text-slate-700">{displayValue(data)}</p>
}
