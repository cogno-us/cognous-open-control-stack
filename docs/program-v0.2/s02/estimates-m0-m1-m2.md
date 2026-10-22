# Estimates by milestone: M0, M1, M2 (revision r3)

**Proposed planning estimates, not a budget, commitment or authorization.** Unit: conventional-equivalent person-days; I is design and implementation, T developer tests, Q separately owned independent qualification. This page splits the [S01 estimates](../s01/estimates.md) (kept unchanged as history) into three scopes, removes work S01 already delivered, and prices refreeze and requalification separately. Machine-readable mirror: [estimates-m0-m1-m2.json](estimates-m0-m1-m2.json). The figures are not valid as calendar duration or engineering expense: no measured productivity exists, and no AI-concurrency conversion is applied.

## Scopes

| Scope | Buys | I L/C/H | T L/C/H | Q L/C/H | Total L/C/H |
|---|---|---|---|---|---|
| M0 Contract-ready | Remaining P1: ADRs, independent expectations, exact boundaries, M0 gate review | 17/28.5/46.5 | 4.5/9/15 | 7.5/13.5/21 | 29/51/82.5 |
| M1 Minimum vertical slice | One registry-backed governance path (one family through L1 and L2) and one durable Orchestrator path, independently qualified | 39.95/68.9/115 | 23.65/40.4/63.35 | 32.55/54.8/88.15 | 96.15/164.1/266.5 |
| M2 Remainder to full v0.2 | Other rule families, remaining adverse and integrated work, 4.3 remainder, decision packet | 17.05/30.1/51 | 8.35/15.6/25.65 | 17.45/29.2/47.85 | 42.85/74.9/124.5 |
| Adjusted full plan | M0 + M1 + M2 | 74/127.5/212.5 | 36.5/65/104 | 57.5/97.5/157 | 168/290/473.5 |

Refreeze and requalification contingency (separate; not in the rows above):

| Scope | Contingency L/C/H | Basis |
|---|---|---|
| M1 | 10/31/76 | 2/3/5 cascades x 3/5/8 days each, plus 2/4/6 locked components x 2/4/6 days of F3 requalification |
| M2 | 8/23/64 | 2/3/5 cascades x 3/5/8 days each, plus 1/2/4 locked components x 2/4/6 days |

M0 changes no locked component, so it carries no contingency.

Through M1 (M0 + M1, without contingency): 125.15/215.1/349; with M1 contingency about 246.1 central. For comparison, the S01 minimum profile was 160/276.5/449 and the S01 full plan 170/293.5/478. The adjusted full plan is 168/290/473.5: it is lower by 2/3.5/4.5 because S01 residual work for steps 1.1 and 1.6 is removed.

## Changes from S01 estimates

| Change | Reason |
|---|---|
| 1.1 residual only (I 0/0/0.5, Q 0/0.5/1) | S01 delivered the inventory, crosswalk and baseline refresh; only independent review of the inventory claims and small fixes remain |
| 1.6 implementation halved (1/1.5/3) | S01 delivered the comparative source work; the remaining ADR drafts are proposed in [adr-proposals.md](adr-proposals.md) and still need review |
| Minimum profile now includes one reconciled rule family | The S01 minimum excluded 2.2 and so did not address the registry's motivation ([registry-and-effects.md](registry-and-effects.md)) |
| Refreeze is a separate package | The S01 totals excluded it although locked-component changes are on the critical path |
| 4.3(b) moves wholly to M2 | Document-as-limit items are not needed for a vertical slice |

## Allocation of step estimates to M1 and M2 (ASSUMED shares)

Steps 1.1 to 1.7 are wholly M0. The table gives the share of each later step's I, T and Q priced in M1; the rest falls in M2. Shares are planning judgements, not measurements; each can be changed in the JSON and the totals recomputed.

| Step | In M1 | In M2 |
|---|---|---|
| 2.1 | 100% | 0% |
| 2.2 | 35% | 65% |
| 2.3 | 40% | 60% |
| 2.4 | 75% | 25% |
| 2.5 | 50% | 50% |
| 3.1 | 100% | 0% |
| 3.2 | 100% | 0% |
| 3.3 | 100% | 0% |
| 3.4 | 100% | 0% |
| 3.5 | 80% | 19% |
| 3.6 | 70% | 30% |
| 4.1 | 60% | 40% |
| 4.2 | 100% | 0% |
| 4.3a | 30% | 70% |
| 4.3b | 0% | 100% |
| 4.4 | 50% | 50% |
| 4.5 | 50% | 50% |
| 4.6 | 0% | 100% |

The 2.2 and 2.3 shares are the conservative assumption that the M1 family needs part of both.

## Assumptions carried from S01

About 60 net lines per day of gate-critical Python with tests; about 2 pages per day of reviewed contract text; 3 to 5 independent cases per day; one independent reviewer available. These are not measured productivity rates (ASSUMED). Refreeze days per cascade are also assumed: the observed fact is seven PRs in seven repositories per refreeze, not a day count.

## Uncertainties

1. Orchestrator migration scope ([ADR-P05](adr-proposals.md#adr-p05-refund-chain-ownership-and-migration-order)): the S01 1.2 and 3.4 values assumed only the direction is fixed in v0.2. If one scenario's assembly actually moves, 1.2, 3.1 and 3.4 are probably low. Confidence LOW until step 1.2 sets the scope.
2. Registry family choice (step 1.3) swings 2.2, 2.3 and 2.5 and may add locked-component changes.
3. Closing in-scope effect surfaces ([ADR-P08](adr-proposals.md#adr-p08-enforcement-minimum)) can require locked-component changes; the count of such components drives the contingency.
4. Qualification-owned controller work (R14, hash coverage, scope-reduction semantics) is outside these figures and may gate integrated acceptance.
5. Independent qualification effort assumes expectations are frozen before any candidate exists; late freezes cost more.

## Recalibration

S03 replaces assumptions with measured pages, lines and cases per day from the first completed P1 steps and republishes this page as a successor revision; this revision is not edited in place.
