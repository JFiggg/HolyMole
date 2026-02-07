"use client";

import { useEffect, useState } from "react";
import { Database, Loader2 } from "lucide-react";
import { fetchInventory, seedDatabase, type Ingredient } from "@/lib/api";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { cn } from "@/lib/utils";

function formatNum(n: number) {
  return Number.isInteger(n) ? n : n.toFixed(2);
}

export default function Home() {
  const [inventory, setInventory] = useState<Ingredient[]>([]);
  const [loading, setLoading] = useState(true);
  const [seeding, setSeeding] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchInventory();
      setInventory(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load inventory");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleSeed = async () => {
    setSeeding(true);
    setError(null);
    try {
      await seedDatabase();
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to seed");
    } finally {
      setSeeding(false);
    }
  };

  return (
    <main className="max-w-5xl mx-auto p-6 md:p-10">
      <header className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Holy Mole</h1>
          <p className="text-muted-foreground text-sm mt-0.5">
            Inventory — Tex-Mex
          </p>
        </div>
        <button
          type="button"
          onClick={handleSeed}
          disabled={seeding || loading}
          className={cn(
            "inline-flex items-center justify-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow hover:bg-primary/90 disabled:opacity-50 disabled:pointer-events-none",
            "bg-zinc-900 text-white hover:bg-zinc-800"
          )}
        >
          {seeding ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Database className="h-4 w-4" />
          )}
          {seeding ? "Seeding…" : "Seed data"}
        </button>
      </header>

      {error && (
        <div className="mb-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
          {error}
        </div>
      )}

      <section className="rounded-lg border border-border bg-card text-card-foreground shadow-sm">
        <div className="p-4 border-b border-border">
          <h2 className="font-semibold">Inventory</h2>
          <p className="text-muted-foreground text-sm">
            All ingredients from the database
          </p>
        </div>
        {loading ? (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : inventory.length === 0 ? (
          <div className="py-16 text-center text-muted-foreground text-sm">
            No ingredients. Click &quot;Seed data&quot; to load Tex-Mex items.
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow className="border-border hover:bg-transparent">
                <TableHead className="text-foreground font-medium">Name</TableHead>
                <TableHead className="text-foreground font-medium">
                  Category
                </TableHead>
                <TableHead className="text-foreground font-medium text-right">
                  Quantity
                </TableHead>
                <TableHead className="text-foreground font-medium">Unit</TableHead>
                <TableHead className="text-foreground font-medium text-right">
                  Unit cost
                </TableHead>
                <TableHead className="text-foreground font-medium text-right">
                  Par level
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {inventory.map((row) => (
                <TableRow key={row.id}>
                  <TableCell className="font-medium">{row.name}</TableCell>
                  <TableCell>{row.category}</TableCell>
                  <TableCell className="text-right">
                    {formatNum(row.quantity)}
                  </TableCell>
                  <TableCell>{row.unit}</TableCell>
                  <TableCell className="text-right">
                    ${formatNum(row.unit_cost)}
                  </TableCell>
                  <TableCell className="text-right">
                    {formatNum(row.par_level)}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </section>
    </main>
  );
}
