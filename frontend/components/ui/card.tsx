import * as React from "react";

import { cn } from "@/lib/utils";

export function Card({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "rounded-[28px] border border-black/5 bg-white/85 p-6 shadow-panel backdrop-blur",
        className
      )}
      {...props}
    />
  );
}
