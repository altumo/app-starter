import { drizzle } from "drizzle-orm/node-postgres";
import * as schema from "@/db/schema";

if (!process.env.DATABASE_URL) {
  throw new Error("DATABASE_URL environment variable is not set");
}

const globalForDb = globalThis as unknown as {
  db: ReturnType<typeof drizzle> | undefined;
};

export const db =
  globalForDb.db ?? drizzle(process.env.DATABASE_URL, { schema });

if (process.env.NODE_ENV !== "production") {
  globalForDb.db = db;
}
