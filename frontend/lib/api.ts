const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type Ingredient = {
  id: number;
  name: string;
  category: string;
  quantity: number;
  unit: string;
  unit_cost: number;
  par_level: number;
};

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
