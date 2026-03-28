import { Card } from "@/components/ui/card";
import type { AttendanceRecord } from "@/lib/api";

type Props = {
  title: string;
  records: AttendanceRecord[];
};

export function AttendanceTable({ title, records }: Props) {
  return (
    <Card className="overflow-hidden p-0">
      <div className="border-b border-black/5 px-6 py-5">
        <p className="text-xs uppercase tracking-[0.28em] text-slateblue">Audit Trail</p>
        <h2 className="mt-2 text-2xl font-semibold">{title}</h2>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-sand/80 text-xs uppercase tracking-[0.2em] text-ink/70">
            <tr>
              <th className="px-6 py-4">Name</th>
              <th className="px-6 py-4">Date</th>
              <th className="px-6 py-4">Time</th>
            </tr>
          </thead>
          <tbody>
            {records.length === 0 ? (
              <tr>
                <td className="px-6 py-6 text-ink/60" colSpan={3}>
                  No attendance records yet.
                </td>
              </tr>
            ) : (
              records.map((record) => (
                <tr key={record.id} className="border-t border-black/5">
                  <td className="px-6 py-4 font-medium">{record.user_name}</td>
                  <td className="px-6 py-4">{record.attendance_date}</td>
                  <td className="px-6 py-4">
                    {new Date(record.marked_at).toLocaleTimeString()}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </Card>
  );
}
