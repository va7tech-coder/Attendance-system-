import Link from "next/link";
import { Camera, History, Settings } from "lucide-react";
import { PropsWithChildren } from "react";

const links = [
  { href: "/", label: "Dashboard", icon: Camera },
  { href: "/attendance", label: "Attendance History", icon: History },
  { href: "/admin", label: "Admin Panel", icon: Settings }
];

export function Layout({ children }: PropsWithChildren) {
  return (
    <div className="min-h-screen bg-shell bg-hero-grid px-4 py-6 text-ink md:px-8">
      <div className="mx-auto max-w-7xl">
        <header className="mb-8 flex flex-col gap-5 rounded-[32px] border border-black/5 bg-white/70 p-6 shadow-panel backdrop-blur lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="mb-2 text-xs uppercase tracking-[0.35em] text-slateblue">
              Face Recognition Attendance
            </p>
            <h1 className="max-w-2xl font-display text-4xl font-semibold leading-tight md:text-5xl">
              Blink-verified attendance with a camera-native workflow.
            </h1>
          </div>
          <nav className="flex flex-wrap gap-3">
            {links.map(({ href, label, icon: Icon }) => (
              <Link
                key={href}
                href={href}
                className="inline-flex items-center gap-2 rounded-full border border-black/10 bg-white px-4 py-2 text-sm font-medium text-ink transition hover:-translate-y-0.5 hover:bg-sand"
              >
                <Icon className="h-4 w-4" />
                {label}
              </Link>
            ))}
          </nav>
        </header>
        {children}
      </div>
    </div>
  );
}
