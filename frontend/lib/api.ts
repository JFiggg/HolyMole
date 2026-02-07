const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface Ingredient {
  id: number;
  name: string;
  category: string;
  quantity: number;
  unit: string;
  par_level: number;
  daily_usage: number;
}

export async function fetchInventory(): Promise<Ingredient[]> {
  const res = await fetch(`${API_BASE}/inventory`);
  if (!res.ok) throw new Error("Failed to fetch inventory");
  return res.json();
}

export async function seedDatabase(): Promise<{ status: string; message: string }> {
  const res = await fetch(`${API_BASE}/seed`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to seed database");
  return res.json();
}

export async function simulateRush(): Promise<{ status: string; message: string; updated?: { name: string; quantity: number }[] }> {
  const res = await fetch(`${API_BASE}/simulate-rush`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to simulate rush");
  return res.json();
}
