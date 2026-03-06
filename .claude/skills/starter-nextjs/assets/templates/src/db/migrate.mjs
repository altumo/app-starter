import pg from "pg";
import { drizzle } from "drizzle-orm/node-postgres";
import { migrate } from "drizzle-orm/node-postgres/migrator";

const { Pool } = pg;

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

const client = await pool.connect();

try {
  // Acquire advisory lock to prevent concurrent migrations
  await client.query("SELECT pg_advisory_lock(1)");
  console.log("Advisory lock acquired, running migrations...");

  const db = drizzle(pool);
  await migrate(db, { migrationsFolder: "./drizzle" });

  console.log("Migrations applied successfully");
  await client.query("SELECT pg_advisory_unlock(1)");
} catch (err) {
  console.error("Migration failed:", err);
  process.exit(1);
} finally {
  client.release();
  await pool.end();
}
