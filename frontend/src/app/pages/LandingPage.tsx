export function LandingPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-slate-50 px-8">
      <h1 className="text-3xl font-bold text-slate-950">MCP Client</h1>
      <p className="max-w-lg text-center text-sm text-slate-600">
        Bienvenido a la aplicación MCP Client. Esta aplicación permite a los
        usuarios autenticados acceder a las herramientas y funcionalidades del
        sistema MCP. Por favor, inicie sesión para continuar.
      </p>
    </div>
  )
}
