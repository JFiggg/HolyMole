"use client";

import { useEffect, useState } from "react";
import { Database, Loader2, Flame } from "lucide-react";
import { fetchInventory, seedDatabase, simulateRush, type Ingredient } from "@/lib/api";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { BlastRadiusGraphModal } from "@/components/BlastRadiusGraph";
import { cn } from "@/lib/utils";

function formatNum(n: number) {
  return Number.isInteger(n) ? n : n.toFixed(2);
}

/**
 * Traffic light: returns Tailwind classes for the row based on quantity vs par_level.
 * 🔴 CRITICAL: quantity < par_level
 * 🟡 WARNING: quantity >= par_level AND quantity < par_level * 1.5
 * 🟢 HEALTHY: otherwise
 */
function getStatusColor(item: Ingredient): string {
  const { quantity, par_level } = item;
  if (quantity < par_level) {
    return "bg-red-50 hover:bg-red-100 border-l-4 border-l-red-500";
  }
  if (quantity < par_level * 1.5) {
    return "bg-yellow-50 hover:bg-yellow-100 border-l-4 border-l-yellow-500";
  }
  return "bg-white hover:bg-slate-50 border-l-4 border-l-green-500";
}

function isCritical(item: Ingredient): boolean {
  return item.quantity < item.par_level;
}

/**
 * Days on hand: quantity / daily_usage. If daily_usage is 0, returns Infinity (display as "∞").
 */
function getDaysOnHand(item: Ingredient): number | null {
  if (item.daily_usage === 0) return null;
  return item.quantity / item.daily_usage;
}

function formatDaysOnHand(item: Ingredient): { text: string; isLow: boolean } {
  const doh = getDaysOnHand(item);
  if (doh === null) return { text: "∞", isLow: false };
  const rounded = Math.round(doh * 10) / 10;
  return {
    text: `${rounded} Days`,
    isLow: rounded < 2.0,
  };
}

export default function Home() {
  const [inventory, setInventory] = useState<Ingredient[]>([]);
  const [loading, setLoading] = useState(true);
  const [seeding, setSeeding] = useState(false);
  const [simulating, setSimulating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [blastRadiusIngredient, setBlastRadiusIngredient] = useState<string | null>(null);
  const [blastRadiusOpen, setBlastRadiusOpen] = useState(false);

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

  const handleSimulateRush = async () => {
    setSimulating(true);
    setError(null);
    try {
      await simulateRush();
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to simulate rush");
    } finally {
      setSimulating(false);
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
        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={handleSimulateRush}
            disabled={simulating || loading}
            className={cn(
              "inline-flex items-center justify-center gap-2 rounded-md px-4 py-2 text-sm font-medium shadow disabled:opacity-50 disabled:pointer-events-none",
              "bg-amber-500 text-white hover:bg-amber-600"
            )}
          >
            {simulating ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Flame className="h-4 w-4" />
            )}
            {simulating ? "Simulating…" : "🔥 Simulate Rush"}
          </button>
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
        </div>
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
                <TableHead className="text-foreground font-medium text-right">
                  Days On Hand
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {inventory.map((row) => {
                const doh = formatDaysOnHand(row);
                const critical = isCritical(row);
                return (
                  <TableRow
                    key={row.id}
                    className={cn(
                      "border-border",
                      getStatusColor(row),
                      critical && "cursor-pointer"
                    )}
                    onClick={() => {
                      if (critical) {
                        setBlastRadiusIngredient(row.name);
                        setBlastRadiusOpen(true);
                      }
                    }}
                  >
                    <TableCell className="font-medium">{row.name}</TableCell>
                    <TableCell>{row.category}</TableCell>
                    <TableCell className="text-right">
                      {formatNum(row.quantity)}
                    </TableCell>
                    <TableCell className="text-right">
                      <span className="inline-flex items-center gap-2">
                        {doh.text}
                        {doh.isLow && (
                          <span className="text-xs font-medium text-red-600">
                            LOW STOCK
                          </span>
                        )}
                      </span>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        )}
      </section>

      <BlastRadiusGraphModal
        ingredientName={blastRadiusIngredient}
        open={blastRadiusOpen}
        onClose={() => {
          setBlastRadiusOpen(false);
          setBlastRadiusIngredient(null);
        }}
      />
    </main>
  );
}
