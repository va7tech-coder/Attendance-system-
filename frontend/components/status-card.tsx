import { CheckCircle2, Eye, ScanFace, TriangleAlert } from "lucide-react";

import { Card } from "@/components/ui/card";
import type { RecognitionResult } from "@/lib/api";

type Props = {
  result: RecognitionResult | null;
  lastMarkedUser: string | null;
};

export function StatusCard({ result, lastMarkedUser }: Props) {
  const title = result?.name ?? "Waiting for a face";
  const confidence = result?.confidence ? `${Math.round(result.confidence * 100)}%` : "--";

  return (
    <Card className="h-full bg-gradient-to-br from-white via-white to-sand">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-slateblue">Recognition Status</p>
          <h2 className="mt-2 text-2xl font-semibold">{title}</h2>
        </div>
        {result?.attendance_marked ? (
          <CheckCircle2 className="h-10 w-10 text-emerald-500" />
        ) : result?.detected ? (
          <ScanFace className="h-10 w-10 text-slateblue" />
        ) : (
          <TriangleAlert className="h-10 w-10 text-orange-500" />
        )}
      </div>

      <div className="space-y-4 text-sm text-ink/80">
        <div className="flex items-center justify-between rounded-2xl bg-ink px-4 py-3 text-shell">
          <span>Confidence</span>
          <strong>{confidence}</strong>
        </div>
        <div className="flex items-center justify-between rounded-2xl bg-mint px-4 py-3">
          <span className="inline-flex items-center gap-2">
            <Eye className="h-4 w-4" />
            Blink / Liveness
          </span>
          <strong>{result?.blink_detected ? "Confirmed" : "Pending"}</strong>
        </div>
        <div className="rounded-2xl border border-black/5 bg-white px-4 py-4">
          <p className="mb-1 text-xs uppercase tracking-[0.25em] text-slateblue">Backend Message</p>
          <p>{result?.message ?? "Start the camera and hold still for recognition."}</p>
        </div>
        <div className="rounded-2xl border border-dashed border-black/10 px-4 py-4">
          <p className="mb-1 text-xs uppercase tracking-[0.25em] text-slateblue">Last Marked</p>
          <p className="text-lg font-semibold">{lastMarkedUser ?? "No attendance marked yet"}</p>
        </div>
      </div>
    </Card>
  );
}
