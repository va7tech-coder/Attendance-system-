import { useCallback, useState } from "react";

import { AttendanceTable } from "@/components/attendance-table";
import { CameraPanel } from "@/components/camera-panel";
import { StatusCard } from "@/components/status-card";
import { Card } from "@/components/ui/card";
import type { AttendanceRecord, RecognitionResult } from "@/lib/api";

export default function DashboardPage() {
  const [result, setResult] = useState<RecognitionResult | null>(null);
  const [records, setRecords] = useState<AttendanceRecord[]>([]);
  const [lastMarkedUser, setLastMarkedUser] = useState<string | null>(null);

  const handleRecognition = useCallback((nextResult: RecognitionResult) => {
    setResult(nextResult);
    if (nextResult.attendance_marked && nextResult.name) {
      const matchedName = nextResult.name;
      setLastMarkedUser(matchedName);
      setRecords((current) => [
        {
          id: Date.now(),
          user_id: nextResult.user_id ?? Date.now(),
          user_name: matchedName,
          attendance_date: new Date().toISOString().slice(0, 10),
          marked_at: new Date().toISOString()
        },
        ...current
      ]);
    }
  }, []);

  return (
    <div className="grid gap-6 lg:grid-cols-[1.45fr_0.95fr]">
      <div className="space-y-6">
        <CameraPanel onRecognition={handleRecognition} />
        <AttendanceTable title="Recent Local Session Activity" records={records.slice(0, 5)} />
      </div>
      <div className="space-y-6">
        <StatusCard result={result} lastMarkedUser={lastMarkedUser} />
        <Card className="bg-ink text-shell">
          <p className="text-xs uppercase tracking-[0.28em] text-orange-200">How It Works</p>
          <div className="mt-4 space-y-3 text-sm text-white/80">
            <p>1. Start the camera and align the face inside the guide frame.</p>
            <p>2. The browser sends a frame every 1.5 seconds to the FastAPI backend.</p>
            <p>3. Backend recognition and blink verification run before attendance is marked.</p>
          </div>
        </Card>
      </div>
    </div>
  );
}
