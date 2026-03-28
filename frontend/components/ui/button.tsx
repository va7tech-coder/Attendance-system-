import * as React from "react";
import { Slot } from "@radix-ui/react-slot";

import { cn } from "@/lib/utils";

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  asChild?: boolean;
  variant?: "primary" | "secondary" | "ghost";
};

export function Button({
  asChild = false,
  className,
  variant = "primary",
  ...props
}: ButtonProps) {
  const Comp = asChild ? Slot : "button";
  return (
    <Comp
      className={cn(
        "inline-flex items-center justify-center rounded-full px-4 py-2 text-sm font-semibold transition focus:outline-none focus:ring-2 focus:ring-slateblue/40 disabled:cursor-not-allowed disabled:opacity-60",
        variant === "primary" &&
          "bg-ink text-shell shadow-panel hover:-translate-y-0.5 hover:bg-slateblue",
        variant === "secondary" &&
          "bg-sand text-ink hover:bg-[#ffe7b0]",
        variant === "ghost" &&
          "border border-black/10 bg-white/70 text-ink hover:bg-white",
        className
      )}
      {...props}
    />
  );
}
