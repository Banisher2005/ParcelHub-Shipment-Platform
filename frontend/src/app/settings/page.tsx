export default function SettingsPage() {
  return (
    <div className="min-h-screen bg-background gradient-mesh">
      {/* Header */}
      <header className="border-b border-border/40 bg-background/80 backdrop-blur-xl sticky top-0 z-40">
        <div className="mx-auto flex max-w-3xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <a
              href="/"
              className="text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              ← Back
            </a>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-3xl px-6 py-8">
        <h1 className="text-2xl font-bold text-foreground">Settings</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Configure your ParcelHub preferences.
        </p>

        <div className="mt-8 space-y-8">
          {/* Tracking Provider */}
          <section className="rounded-xl border border-border/40 bg-card/60 p-6 backdrop-blur-sm">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
              Tracking Provider
            </h2>
            <p className="mt-2 text-sm text-muted-foreground/80">
              Currently using the <span className="text-primary font-medium">mock provider</span> for development.
              Configure your 17TRACK API key in the backend <code className="text-xs bg-muted px-1.5 py-0.5 rounded">.env</code> file.
            </p>
          </section>

          {/* Notifications (future) */}
          <section className="rounded-xl border border-border/40 bg-card/60 p-6 backdrop-blur-sm opacity-60">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
              Notifications
            </h2>
            <p className="mt-2 text-sm text-muted-foreground/80">
              Push notifications and email alerts — coming soon.
            </p>
          </section>

          {/* Account (future) */}
          <section className="rounded-xl border border-border/40 bg-card/60 p-6 backdrop-blur-sm opacity-60">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
              Account
            </h2>
            <p className="mt-2 text-sm text-muted-foreground/80">
              Multi-user accounts and team sharing — coming soon.
            </p>
          </section>
        </div>
      </main>
    </div>
  );
}
