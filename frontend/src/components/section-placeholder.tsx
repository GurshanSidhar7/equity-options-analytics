export function SectionPlaceholder({ title, description, limitation }: {
  title: string; description: string; limitation: string;
}) {
  return <section>
    <h1 className="text-3xl font-semibold tracking-tight">{title}</h1>
    <p className="mt-3 max-w-2xl text-slate-600">{description}</p>
    <div className="mt-6 rounded-xl border border-dashed border-slate-300 bg-white p-8">
      <p className="text-sm font-semibold text-cyan-800">Planned within V1 · Not implemented yet</p>
      <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600">{limitation}</p>
    </div>
  </section>;
}
