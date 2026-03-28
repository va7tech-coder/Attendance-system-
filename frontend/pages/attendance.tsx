import { useEffect, useState } from "react";

import { AttendanceTable } from "@/components/attendance-table";
import { Card } from "@/components/ui/card";
import { getAttendance, type AttendanceRecord } from "@/lib/api";

export default function AttendanceHistoryPage() {
  const [records, setRecords] = useState<AttendanceRecord[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getAttendance()
      .then(setRecords)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load attendance."));
  }, []);

  return (
    <div className="space-y-6">
      <Card className="bg-gradient-to-r from-slateblue to-ink text-shell">
        <p className="text-xs uppercase tracking-[0.28em] text-orange-200">Attendance History</p>
        <h2 className="mt-2 text-3xl font-semibold">Every attendance event, sorted by latest mark.</h2>
      </Card>
      {error ? <p className="text-sm text-red-600">{error}</p> : null}
      <AttendanceTable title="Database Records" records={records} />
    </div>
  );
}
