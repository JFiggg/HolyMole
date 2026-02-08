"use client";

import { useEffect, useMemo, useState } from "react";
import ReactFlow, {
  Background,
  Controls,
  Edge,
  Node,
  NodeTypes,
  ReactFlowProvider,
  useEdgesState,
  useNodesState,
} from "reactflow";
import "reactflow/dist/style.css";
import { Loader2, X, Package } from "lucide-react";
import { fetchBlastRadius, restockIngredient, type BlastRadiusResponse } from "@/lib/api";
import { cn } from "@/lib/utils";

const NODE_WIDTH = 140;
const NODE_HEIGHT = 44;
const LAYER_GAP = 100;

function BlastRadiusNode({
  data,
}: {
  data: { label: string; type: "ingredient" | "sub_recipe" | "menu_item" };
}) {
  const style =
    data.type === "ingredient"
      ? "bg-red-500 text-white border-red-600 shadow-md"
      : data.type === "sub_recipe"
        ? "bg-amber-500 text-white border-amber-600 shadow-md"
        : "bg-slate-400 text-slate-900 border-slate-500";

  return (
    <div
      className={cn(
        "rounded-lg border-2 px-3 py-2 text-center text-sm font-medium min-w-[120px]",
        style
      )}
    >
      {data.label}
    </div>
  );
}

const nodeTypes: NodeTypes = {
  blast: BlastRadiusNode,
};

function layoutNodesAndEdges(data: BlastRadiusResponse): { nodes: Node[]; edges: Edge[] } {
  const byType = {
    ingredient: data.nodes.filter((n) => n.type === "ingredient"),
    sub_recipe: data.nodes.filter((n) => n.type === "sub_recipe"),
    menu_item: data.nodes.filter((n) => n.type === "menu_item"),
  };

  const layers = [byType.menu_item, byType.sub_recipe, byType.ingredient].filter(
    (arr) => arr.length > 0
  );
  const nodes: Node[] = [];
  let y = 0;
  for (const layer of layers) {
    const totalWidth = (layer.length - 1) * (NODE_WIDTH + 40) + NODE_WIDTH;
    const startX = -totalWidth / 2 + NODE_WIDTH / 2;
    layer.forEach((n, i) => {
      nodes.push({
        id: n.id,
        type: "blast",
        data: { label: n.label, type: n.type },
        position: { x: startX + i * (NODE_WIDTH + 40), y },
      });
    });
    y += LAYER_GAP + NODE_HEIGHT;
  }

  const edges: Edge[] = data.edges.map((e, i) => ({
    id: `e-${i}`,
    source: e.from,
    target: e.to,
  }));

  return { nodes, edges };
}

function BlastRadiusGraphInner({ ingredientName, onRestockSuccess }: { ingredientName: string; onRestockSuccess?: () => void }) {
  const [data, setData] = useState<BlastRadiusResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [restocking, setRestocking] = useState(false);
  const [restockInfo, setRestockInfo] = useState<{
    quantityToAdd: number;
    cost: number;
    unit: string;
  } | null>(null);

  const { nodes: initialNodes, edges: initialEdges } = useMemo(() => {
    if (!data) return { nodes: [], edges: [] };
    return layoutNodesAndEdges(data);
  }, [data]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  useEffect(() => {
    setData(null);
    setError(null);
    setLoading(true);
    setRestockInfo(null);
    fetchBlastRadius(ingredientName)
      .then(setData)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load"))
      .finally(() => setLoading(false));
  }, [ingredientName]);

  useEffect(() => {
    setNodes(initialNodes);
    setEdges(initialEdges);
  }, [initialNodes, initialEdges, setNodes, setEdges]);

  const handleRestock = async () => {
    setRestocking(true);
    setError(null);
    try {
      const result = await restockIngredient(ingredientName);
      setRestockInfo({
        quantityToAdd: result.quantity_added,
        cost: result.total_cost,
        unit: result.unit,
      });
      if (onRestockSuccess) {
        onRestockSuccess();
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to restock");
    } finally {
      setRestocking(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center gap-4 p-12">
        <Loader2 className="h-10 w-10 animate-spin text-muted-foreground" />
        <p className="text-sm text-muted-foreground">Loading blast radius…</p>
      </div>
    );
  }
  if (error) {
    return (
      <div className="p-6">
        <p className="text-sm text-red-600">{error}</p>
      </div>
    );
  }
  if (!data || data.nodes.length === 0) {
    return (
      <div className="p-6">
        <p className="text-sm text-muted-foreground">
          No menu items depend on &quot;{ingredientName}&quot;.
        </p>
      </div>
    );
  }

  const pct =
    data.total_menu_count > 0
      ? Math.round((data.affected_menu_items.length / data.total_menu_count) * 100)
      : 0;
  const list = data.affected_with_revenue ?? data.affected_menu_items.map((m) => ({ menu_item: m, revenue_per_hour: 0 }));

  return (
    <div className="flex flex-col gap-4">
      {restockInfo && (
        <div className="rounded-lg border border-green-200 bg-green-50 px-4 py-3">
          <p className="text-sm font-medium text-green-800">
            ✓ Restocked successfully!
          </p>
          <p className="mt-1 text-sm text-green-700">
            Added {restockInfo.quantityToAdd.toFixed(2)} {restockInfo.unit} • Cost: ${restockInfo.cost.toFixed(2)}
          </p>
        </div>
      )}
      <div className="rounded-lg border border-border bg-muted/30 px-4 py-3">
        <div className="flex items-center justify-between">
          <p className="text-sm font-medium text-foreground">
            <span className="font-semibold text-red-600">{pct}%</span> of the menu relies on it
          </p>
          <button
            type="button"
            onClick={handleRestock}
            disabled={restocking}
            className={cn(
              "inline-flex items-center justify-center gap-2 rounded-md px-3 py-1.5 text-sm font-medium shadow disabled:opacity-50 disabled:pointer-events-none",
              "bg-green-600 text-white hover:bg-green-700"
            )}
          >
            {restocking ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Package className="h-4 w-4" />
            )}
            {restocking ? "Restocking…" : "Restock"}
          </button>
        </div>
        <ul className="mt-3 list-none space-y-1.5 border-t border-border pt-3">
          {list.map(({ menu_item, revenue_per_hour }) => (
            <li
              key={menu_item}
              className="flex items-center justify-between gap-2 text-sm"
            >
              <span className="text-foreground">{menu_item}</span>
              <span className="shrink-0 tabular-nums text-red-600">
                ${revenue_per_hour.toLocaleString()}/hr
              </span>
            </li>
          ))}
        </ul>
        <div className="mt-3 flex items-center justify-between border-t border-border pt-3 text-sm font-semibold">
          <span>Total revenue at risk</span>
          <span className="tabular-nums text-red-600">
            ${data.total_revenue_risk_per_hour.toLocaleString()}/hr
          </span>
        </div>
      </div>
      <div className="relative h-[360px] w-full">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        proOptions={{ hideAttribution: true }}
      >
        <Background />
        <Controls showInteractive={false} />
      </ReactFlow>
      </div>
    </div>
  );
}

export function BlastRadiusGraphModal({
  ingredientName,
  open,
  onClose,
  onRestockSuccess,
}: {
  ingredientName: string | null;
  open: boolean;
  onClose: () => void;
  onRestockSuccess?: () => void;
}) {
  useEffect(() => {
    if (!open) return;
    const handle = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handle);
    return () => window.removeEventListener("keydown", handle);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div
        className="flex max-h-[90vh] w-full max-w-2xl flex-col rounded-lg border border-border bg-card shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between border-b border-border px-4 py-3">
          <h3 className="font-semibold">
            Blast radius{ingredientName ? `: ${ingredientName}` : ""}
          </h3>
          <button
            type="button"
            onClick={onClose}
            className="rounded p-1 hover:bg-muted"
            aria-label="Close"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
        <div className="overflow-auto p-4">
          {ingredientName ? (
            <ReactFlowProvider>
              <BlastRadiusGraphInner ingredientName={ingredientName} onRestockSuccess={onRestockSuccess} />
            </ReactFlowProvider>
          ) : (
            <p className="text-sm text-muted-foreground">Select an ingredient.</p>
          )}
        </div>
      </div>
    </div>
  );
}
