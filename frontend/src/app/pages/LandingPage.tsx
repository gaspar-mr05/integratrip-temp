export function LandingPage() {
  return (
    <section className="mx-auto grid min-h-[calc(100svh-9.5rem)] w-full max-w-7xl content-center gap-12 sm:min-h-[calc(100svh-11.5rem)] lg:grid-cols-[minmax(0,1.25fr)_minmax(18rem,.75fr)] lg:gap-24">
      <div className="grid content-center gap-7">
        <p className="m-0 text-sm font-semibold tracking-[0.16em] text-blue-700 uppercase">
          Plataforma de integración
        </p>
        <h1 className="m-0 max-w-3xl text-5xl font-semibold tracking-[-0.055em] text-slate-950 sm:text-6xl lg:text-7xl">
          Herramientas conectadas con imaginación y esfuerzo.
        </h1>
        <p className="m-0 max-w-xl text-base leading-7 text-slate-600 sm:text-lg">
          IntegraTrip reúne los servicios MCP para que puedas consultar y
          ejecutar sus herramientas desde un solo lugar.
        </p>
      </div>

      <div className="self-center border-l-2 border-blue-700 pl-6 sm:pl-8">
        <p className="m-0 text-sm leading-6 text-slate-500">
          Inicia sesión para acceder a tus conexiones, explorar las tools
          disponibles y trabajar con cada servicio de forma segura.
        </p>
        <div className="mt-8 flex items-center gap-3 text-sm font-medium text-slate-700">
          <span className="size-2 rounded-full bg-blue-600" />
          Acceso protegido mediante OAuth
        </div>
      </div>
    </section>
  )
}
