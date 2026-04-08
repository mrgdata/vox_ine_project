"""
Agent-Based Model: Vote Preference Dynamics Under Immigration Growth
====================================================================
Based on findings from "El futuro de Vox está en Getafe, no en el Barrio Salamanca"
by Manuel Romero (Medium, Dec 2025).

Key Article Findings:
- PSOE (left): dominates low-income, low-immigration areas (~42.1%),
  loses ground as immigration rises in those areas (~36.7%)
- PP (right): dominates high-income areas (~45%), barely affected by immigration
- VOX (far-right): peaks at low-income + high-immigration (16.9%),
  flat in high-income areas (~13.8-13.9%) — wealth is a "shield"
- Foreign-born population concentrates in low-income neighbourhoods
- Foreign-born voters lean more left
- Income of native population stays roughly constant over time
"""

from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np

# ── Configuration ──────────────────────────────────────────────
N_AGENTS = 5_000
N_NEIGHBOURHOODS = 20
N_STEPS = 20  # simulated time steps (years-ish)
INITIAL_FOREIGN_PCT = 0.20  # 20% initial foreign-born (Spain ~2026). Calibrated on INE data.
FOREIGN_GROWTH_RATE = (
    0.02  # +2pp new foreign-born per step. Calibrated on INE data, last 10Y 4~pct annually.
)
NATIVE_INCOME_PREMIUM = (
    0.29  # natives earn ~40% more than foreign-born. Calibrated on INE data, 2026.  # noqa: E501
)
SEED = 42

np.random.seed(SEED)

PARTIES = ["Far-Left", "Left (PSOE)", "Right (PP)", "Far-Right (VOX)"]
PARTY_COLORS = {
    "Far-Left": "#8B008B",
    "Left (PSOE)": "#E63946",
    "Right (PP)": "#1D3557",
    "Far-Right (VOX)": "#6A994E",
}


# ── Data structures ────────────────────────────────────────────
@dataclass
class Neighbourhood:
    id: int
    income_level: float  # 0 (poorest) → 1 (richest)


@dataclass
class Agent:
    id: int
    income: float  # 0 → 1
    is_native: bool
    neighbourhood_id: int


# ── Neighbourhood helpers ──────────────────────────────────────
def create_neighbourhoods(n: int) -> list[Neighbourhood]:
    return [Neighbourhood(id=i, income_level=(i + 0.5) / n) for i in range(n)]


def assign_neighbourhood(
    income: float, is_native: bool, neighbourhoods: list[Neighbourhood]
) -> int:
    """
    Assign an agent to a neighbourhood.
    - Natives cluster near their income peers.
    - Foreign-born cluster in *lower*-income neighbourhoods (article finding).
    """
    n = len(neighbourhoods)
    if is_native:
        probs = np.array([np.exp(-3.0 * (income - nb.income_level) ** 2) for nb in neighbourhoods])
    else:
        # Income match + strong penalty for high-income neighbourhoods
        probs = np.array(
            [
                np.exp(-2.0 * (income - nb.income_level) ** 2) * np.exp(-1.5 * nb.income_level)
                for nb in neighbourhoods
            ]
        )
    probs /= probs.sum()
    return int(np.random.choice(n, p=probs))


def compute_neighbourhood_stats(agents: list[Agent], n_nb: int) -> dict[int, dict]:
    """Return avg income and % foreign-born per neighbourhood."""
    buckets: dict[int, list] = {i: [] for i in range(n_nb)}
    for a in agents:
        buckets[a.neighbourhood_id].append(a)

    stats = {}
    for nid in range(n_nb):
        group = buckets[nid]
        if not group:
            stats[nid] = {"avg_income": 0.5, "pct_foreign": 0.0, "count": 0}
        else:
            stats[nid] = {
                "avg_income": float(np.mean([a.income for a in group])),
                "pct_foreign": float(1.0 - np.mean([a.is_native for a in group])),
                "count": len(group),
            }
    return stats


# ── Vote function ──────────────────────────────────────────────
def vote_preference(agent: Agent, nb_stats: dict[int, dict]) -> str:
    """
    Assign a party preference using a softmax over four utility scores.

    Utility rules (calibrated to reproduce the article's heatmaps):
      1. Personal income  → higher income favours PP, low income favours PSOE
      2. Native/foreign   → foreign lean left; natives slightly lean right/far-right
      3. Neighbourhood foreign % × neighbourhood income →
         KEY: in LOW-income areas, high foreign % boosts VOX for natives
              in HIGH-income areas, effect is negligible ("shield of wealth")
      4. Neighbourhood income reinforces the class-vote pattern
    """
    s = nb_stats[agent.neighbourhood_id]
    nb_inc = s["avg_income"]
    nb_for = s["pct_foreign"]
    inc = agent.income

    #                   Far-Left   Left(PSOE)  Right(PP)  Far-Right(VOX)
    u = np.zeros(4)

    # 1) Personal income
    u[0] += -0.5 + 1.0 * (1 - inc)  # far-left: modest low-income boost
    u[1] += 0.5 + 1.5 * (1 - inc)  # PSOE: strong low-income base
    u[2] += -0.5 + 2.0 * inc  # PP: strong income correlation
    u[3] += -0.3 + 0.3 * (1 - inc)  # VOX: slight low-income lean (post-2019)

    # 2) Native vs foreign-born
    if agent.is_native:
        u[0] += -0.2
        u[1] += -0.1
        u[2] += 0.2
        u[3] += 0.3
    else:
        u[0] += 0.5
        u[1] += 0.4
        u[2] += -0.3
        u[3] += -1.0  # ORIGINAL: -1.5 // 1.0 Good

    # 3) Neighbourhood immigration × income interaction (natives only)
    if agent.is_native:
        # Sensitivity: high in poor areas, near-zero in rich areas
        sensitivity = max(0.0, 1.5 * (1 - nb_inc))
        u[3] += sensitivity * nb_for * 4.0  # VOX gains # ORIGINAL: 3.0 // 5.0 Good
        u[1] -= sensitivity * nb_for * 3.0  # PSOE loses # ORIGINAL: 2.0 // 4.0 Good
        u[2] += sensitivity * nb_for * 0.5  # PP picks up a little

    # 4) Neighbourhood income reinforces class-vote
    u[1] += 0.3 * (1 - nb_inc)
    u[2] += 0.3 * nb_inc

    # Softmax → probabilities → random draw
    u -= u.max()
    probs = np.exp(u) / np.exp(u).sum()
    return str(np.random.choice(PARTIES, p=probs))


# ── Population creation ───────────────────────────────────────
def create_initial_population(
    n: int, neighbourhoods: list[Neighbourhood], foreign_pct: float
) -> list[Agent]:
    agents = []
    for i in range(n):
        is_native = np.random.random() > foreign_pct
        # Foreign-born skew lower income; natives earn ~20% more
        if is_native:
            income_neighbourhood = float(np.clip(np.random.beta(2.5, 2.5), 0, 1))
            income = income_neighbourhood
        else:
            # income of migrants is different than income where migrant lives, but correlated.
            income_neighbourhood = float(np.clip(np.random.beta(2, 6), 0, 1))
            income = float(np.clip(np.random.beta(2.5, 2.5) * (1 - NATIVE_INCOME_PREMIUM), 0, 1))
        nb_id = assign_neighbourhood(income_neighbourhood, is_native, neighbourhoods)
        agents.append(Agent(id=i, income=income, is_native=is_native, neighbourhood_id=nb_id))
    return agents


def add_immigrants(
    agents: list[Agent], n_new: int, neighbourhoods: list[Neighbourhood], next_id: int
) -> list[Agent]:
    """Add new foreign-born agents (income stays constant for natives)."""
    new = []
    for i in range(n_new):
        income = float(np.clip(np.random.beta(2, 4), 0, 1))  # no native premium
        nb_id = assign_neighbourhood(income, False, neighbourhoods)
        new.append(Agent(id=next_id + i, income=income, is_native=False, neighbourhood_id=nb_id))
    return new


# ── Simulation loop ───────────────────────────────────────────
def run_simulation():
    neighbourhoods = create_neighbourhoods(N_NEIGHBOURHOODS)
    agents = create_initial_population(N_AGENTS, neighbourhoods, INITIAL_FOREIGN_PCT)

    results = {p: [] for p in PARTIES}
    foreign_pcts: list[float] = []
    next_id = len(agents)

    for step in range(N_STEPS):
        nb_stats = compute_neighbourhood_stats(agents, N_NEIGHBOURHOODS)

        votes = {p: 0 for p in PARTIES}
        for a in agents:
            votes[vote_preference(a, nb_stats)] += 1

        total = sum(votes.values())
        for p in PARTIES:
            results[p].append(votes[p] / total * 100)

        cur_foreign = 1.0 - np.mean([a.is_native for a in agents])
        foreign_pcts.append(cur_foreign * 100)

        # Grow foreign-born population (income of existing agents unchanged)
        n_new = int(len(agents) * FOREIGN_GROWTH_RATE)
        agents.extend(add_immigrants(agents, n_new, neighbourhoods, next_id))
        next_id += n_new

    return results, foreign_pcts


# ── Plotting ──────────────────────────────────────────────────
def plot_results(results, foreign_pcts):
    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(12, 10), sharex=True, gridspec_kw={"height_ratios": [3, 1]}
    )

    # ── Vote shares ──
    for p in PARTIES:
        ax1.plot(range(N_STEPS), results[p], label=p, color=PARTY_COLORS[p], linewidth=2.5)

    ax1.set_ylabel("Vote Share (%)", fontsize=13)
    ax1.set_title(
        "ABM Simulation: Vote Share Evolution Under Rising Immigration\n"
        "(Based on 'El futuro de Vox está en Getafe, no en el Barrio Salamanca')",
        fontsize=14,
        fontweight="bold",
    )
    ax1.legend(fontsize=11, loc="center left", bbox_to_anchor=(1.01, 0.5))
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 50)

    # ── Foreign-born % ──
    ax2.fill_between(range(N_STEPS), foreign_pcts, alpha=0.3, color="orange")
    ax2.plot(range(N_STEPS), foreign_pcts, color="orange", linewidth=2.5, label="Foreign-born %")
    ax2.set_xlabel("Time Step", fontsize=13)
    ax2.set_ylabel("Foreign-born (%)", fontsize=13)
    ax2.legend(fontsize=11)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("abm_vote_simulation.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("\nPlot saved to abm_vote_simulation.png")


# ── Main ──────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 65)
    print("  ABM: Spanish Vote Dynamics Under Rising Immigration")
    print("=" * 65)

    results, foreign_pcts = run_simulation()

    # Summary table
    hdr = f"{'Step':>5} | {'Foreign%':>8} | {'Far-Left':>9} | {'PSOE':>9} | {'PP':>9} | {'VOX':>9}"
    print(f"\n{hdr}")
    print("-" * len(hdr))
    for i in list(range(0, N_STEPS, 3)) + [N_STEPS - 1]:
        print(
            f"{i:>5} | {foreign_pcts[i]:>7.1f}% |"
            f" {results['Far-Left'][i]:>8.1f}% |"
            f" {results['Left (PSOE)'][i]:>8.1f}% |"
            f" {results['Right (PP)'][i]:>8.1f}% |"
            f" {results['Far-Right (VOX)'][i]:>8.1f}%"
        )

    print(f"\n--- Change: Step 0 → Step {N_STEPS - 1} ---")
    for p in PARTIES:
        delta = results[p][-1] - results[p][0]
        print(f"  {p:>20s}: {delta:+.1f} pp")

    plot_results(results, foreign_pcts)
