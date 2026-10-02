export function SectionPlaceholder({ title, description, limitation }: {
  title: string; description: string; limitation: string;
}) {
  return <section>
    <h1 className="text-3xl font-semibold tracking-tight">{title}</h1>
    <p className="mt-3 max-w-2xl text-[var(--muted)]">{description}</p>
    <div className="mt-6 rounded-xl border border-dashed border-[var(--line)] bg-[var(--surface)] p-8">
      <p className="text-sm font-semibold text-[var(--sage-ink)]">Planned within V1 · Not implemented yet</p>
      <p className="mt-3 max-w-2xl text-sm leading-6 text-[var(--muted)]">{limitation}</p>
    </div>
  </section>;
}
