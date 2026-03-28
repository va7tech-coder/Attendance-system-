export type RecognitionResult = {
  detected: boolean;
  live: boolean;
  blink_detected: boolean;
  name?: string | null;
  confidence?: number | null;
  user_id?: number | null;
  attendance_marked: boolean;
  message: string;
};

export type AttendanceRecord = {
  id: number;
  user_id: number;
  user_name: string;
  attendance_date: string;
  marked_at: string;
};

export type UserRecord = {
  id: number;
  name: string;
  embedding_count: number;
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, init);
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed with ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export async function recognize(imageBase64: string, sessionId: string) {
  return request<RecognitionResult>("/recognize", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      image_base64: imageBase64,
      session_id: sessionId,
      auto_mark_attendance: true
    })
  });
}

export async function getAttendance(limit = 100) {
  return request<AttendanceRecord[]>(`/attendance?limit=${limit}`);
}

export async function getUsers() {
  return request<UserRecord[]>("/users");
}

export async function reloadDataset() {
  return request<{ message: string; embeddings_created: number; cached_embeddings: number }>(
    "/system/reload-dataset",
    { method: "POST" }
  );
}

export async function addUser(name: string, files: File[]) {
  const formData = new FormData();
  formData.append("name", name);
  files.forEach((file) => formData.append("files", file));
  return request<{ id: number; name: string; embedding_count: number; message: string }>(
    "/users",
    {
      method: "POST",
      body: formData
    }
  );
}
