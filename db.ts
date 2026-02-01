import { openDB } from "idb";

export const dbPromise = openDB("store3729", 1, {
  upgrade(db) {
    db.createObjectStore("outbox", { keyPath: "client_event_id" });
    db.createObjectStore("meta", { keyPath: "key" });
  },
});

export async function queueEvent(evt: any) {
  const db = await dbPromise;
  await db.put("outbox", evt);
}

export async function getOutbox() {
  const db = await dbPromise;
  return await db.getAll("outbox");
}

export async function clearOutbox(ids: string[]) {
  const db = await dbPromise;
  const tx = db.transaction("outbox", "readwrite");
  for (const id of ids) await tx.store.delete(id);
  await tx.done;
}

export async function setMeta(key: string, value: any) {
  const db = await dbPromise;
  await db.put("meta", { key, value });
}

export async function getMeta(key: string) {
  const db = await dbPromise;
  return (await db.get("meta", key))?.value;
}
