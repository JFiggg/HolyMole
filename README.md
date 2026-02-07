# Holy Mole
### Inventory Risk Intelligence for High-Volume Kitchens

> **"Don't just count stock. Calculate the *cost* of missing stock."**

**Holy Mole** is not a standard inventory tracker. It is a **risk engine** that uses Graph Theory (Directed Acyclic Graphs) to visualize the hidden dependencies between raw ingredients and menu revenue.

When a restaurant runs out of eggs, they don't just lose eggs—they lose the ability to sell Mayo, Aioli, Breakfast Tacos, and the Spicy Chicken Sandwich. **Holy Mole** calculates this "Blast Radius" in real-time, showing the exact revenue at risk per hour.

---

## Key Features

* **Real-Time Inventory Tracking:** Live monitoring of stock levels with calculated "Days-On-Hand" (DOH) metrics.
* **The "Blast Radius" Visualizer:** A **Directed Acyclic Graph (DAG)** that maps Ingredients -> Sub-recipes -> Menu Items.
* **Revenue-at-Risk Ticker:** Instantly calculates financial loss ($/hr) based on blocked menu items.
* **"Friday Night Rush" Simulation:** A built-in chaos engineering tool that simulates rapid stock depletion to demonstrate the system's reaction.
* **Auto-Reorder:** One-click reordering that resolves stockouts and updates the dependency graph instantly.

---

## Tech Stack

### Frontend
* **Framework:** Next.js 14 (App Router)
* **Styling:** Tailwind CSS + shadcn/ui
* **Visualization:** React Flow (Graph Rendering)
* **Icons:** Lucide React

### Backend
* **API:** FastAPI (Python)
* **Database:** SQLite (Lightweight, local file)
* **ORM:** SQLAlchemy
* **Algorithms:** Recursive DFS (Depth-First Search) for dependency traversal.

---

## Installation & Setup

### 1. Clone the Repository
```bash
git clone [https://github.com/yourusername/holy-mole.git](https://github.com/yourusername/holy-mole.git)
cd holy-mole
