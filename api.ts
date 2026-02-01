import { getOutbox, clearOutbox, getMeta, setMeta } from "./db";

const API = import.meta.env.VITE_API_URL || "";

export async function login(username: string, password: string) {
  const res = await fetch(`${API}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password })
  });
  if (!res.ok) throw new Error("Login failed");
  return await res.json(); // {token}
}

export async function fetchSettings(token: string) {
  const res = await fetch(`${API}/meta/settings`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  if (!res.ok) throw new Error("Settings fetch failed");
  return await res.json();
}

export async function fetchUnits(token: string) {
  const res = await fetch(`${API}/meta/units`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  if (!res.ok) throw new Error("Units fetch failed");
  return await res.json();
}

export async function fetchItems(token: string) {
  const res = await fetch(`${API}/items`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  if (!res.ok) throw new Error("Items fetch failed");
  return await res.json();
}

export async function createItem(token: string, body: any) {
  const res = await fetch(`${API}/items`, {
    method: "POST",
    headers: { "Content-Type":"application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify(body)
  });
  if (!res.ok) throw new Error("Create item failed");
  return await res.json();
}

export async function updateItem(token: string, id: string, body: any) {
  const res = await fetch(`${API}/items/${id}`, {
    method: "PUT",
    headers: { "Content-Type":"application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify(body)
  });
  if (!res.ok) throw new Error("Update item failed");
  return await res.json();
}

export async function pushSync(token: string, deviceId: string) {
  const events = await getOutbox();
  if (!events.length) return { inserted: 0 };

  const res = await fetch(`${API}/sync/push`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify({ device_id: deviceId, events })
  });

  if (!res.ok) return { inserted: 0 };
  const data = await res.json();
  await clearOutbox(events.map((e: any) => e.client_event_id));
  return data;
}

export async function pullSync(token: string) {
  const since = (await getMeta("last_pull")) || "1970-01-01T00:00:00Z";
  const res = await fetch(`${API}/sync/pull?since=${encodeURIComponent(since)}`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  if (!res.ok) return [];
  const data = await res.json();
  const events = data.events || [];
  const last = events.length ? events[events.length - 1].created_at : since;
  await setMeta("last_pull", last);
  return events;
}

export function uuidv4() {
  return crypto.randomUUID();
}
