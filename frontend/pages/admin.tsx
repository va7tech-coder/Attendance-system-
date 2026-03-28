import { FormEvent, useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { addUser, getUsers, reloadDataset, type UserRecord } from "@/lib/api";

export default function AdminPage() {
  const [name, setName] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const [users, setUsers] = useState<UserRecord[]>([]);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function refreshUsers() {
    try {
      setUsers(await getUsers());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load users.");
    }
  }

  useEffect(() => {
    refreshUsers();
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setMessage(null);
    try {
      const response = await addUser(name, files);
      setMessage(`${response.message} ${response.name} now has ${response.embedding_count} embeddings.`);
      setName("");
      setFiles([]);
      const fileInput = event.currentTarget.elements.namedItem("files") as HTMLInputElement | null;
      if (fileInput) {
        fileInput.value = "";
      }
      await refreshUsers();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create user.");
    }
  }

  async function handleReload() {
    setError(null);
    setMessage(null);
    try {
      const response = await reloadDataset();
      setMessage(
        `${response.message} ${response.embeddings_created} embeddings imported and ${response.cached_embeddings} cached.`
      );
      await refreshUsers();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to reload dataset.");
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[1.05fr_0.95fr]">
      <Card>
        <p className="text-xs uppercase tracking-[0.28em] text-slateblue">Admin Tools</p>
        <h2 className="mt-2 text-3xl font-semibold">Enroll users and rebuild the recognition index.</h2>

        <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
          <div>
            <label className="mb-2 block text-sm font-medium">User name</label>
            <input
              className="w-full rounded-2xl border border-black/10 bg-white px-4 py-3 outline-none ring-slateblue/40 transition focus:ring-2"
              value={name}
              onChange={(event) => setName(event.target.value)}
              placeholder="Varun"
              required
            />
          </div>
          <div>
            <label className="mb-2 block text-sm font-medium">Training images</label>
            <input
              name="files"
              className="block w-full rounded-2xl border border-dashed border-black/15 bg-sand/60 px-4 py-4 text-sm"
              type="file"
              accept="image/*"
              multiple
              onChange={(event) => setFiles(Array.from(event.target.files ?? []))}
              required
            />
          </div>
          <div className="flex flex-wrap gap-3">
            <Button type="submit">Add User</Button>
            <Button type="button" variant="secondary" onClick={handleReload}>
              Reload Dataset Folder
            </Button>
          </div>
        </form>

        {message ? <p className="mt-4 text-sm text-emerald-700">{message}</p> : null}
        {error ? <p className="mt-4 text-sm text-red-600">{error}</p> : null}
      </Card>

      <Card className="bg-gradient-to-br from-white via-white to-mint">
        <p className="text-xs uppercase tracking-[0.28em] text-slateblue">Current Users</p>
        <h2 className="mt-2 text-2xl font-semibold">Indexed face profiles</h2>
        <div className="mt-6 space-y-3">
          {users.length === 0 ? (
            <p className="text-sm text-ink/65">No enrolled users yet.</p>
          ) : (
            users.map((user) => (
              <div
                key={user.id}
                className="flex items-center justify-between rounded-2xl border border-black/5 bg-white px-4 py-4"
              >
                <div>
                  <p className="font-semibold">{user.name}</p>
                  <p className="text-sm text-ink/65">User ID: {user.id}</p>
                </div>
                <div className="rounded-full bg-ink px-3 py-2 text-xs font-semibold text-shell">
                  {user.embedding_count} embeddings
                </div>
              </div>
            ))
          )}
        </div>
      </Card>
    </div>
  );
}
