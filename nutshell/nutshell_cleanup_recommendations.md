# Nutshell Repository Management & Velocity Plan

**Date:** February 17, 2026

**Status:** Rough Draft for Review

## 1. Executive Summary: The "Success Tax"

The Nutshell repository is currently experiencing a "Success Tax." High community engagement has resulted in **76 open issues** and **65 open PRs**. While this signals a healthy ecosystem, the volume has exceeded the capacity of our manual triage processes.

The goal of this plan is to transition from **Individual Approval** to **Process-Based Confidence**, allowing us to increase velocity while maintaining the stability required for financial software.

---

## 2. Current State Snapshot (Feb 2026)

| Metric | Current Value | Strategic Impact |
| --- | --- | --- |
| **Total Open PRs** | 65 | High cognitive load; 32% are "Drafts" creating noise. |
| **Total Open Issues** | 76 | Significant protocol history mixed with actionable bugs. |
| **Oldest Item** | #52 (1,200 days) | Protocol-level debt (Max secret size) needs a final "mergable" path. |
| **Stale Rate** | ~60% | Items >180 days old risk bit-rotting and contributor churn. |

---

## 3. Proposed Branch Management: "Confidence Gates"

To decouple **Merge Confidence** from **Release Confidence**, we will adopt a staged pipeline. This allows us to merge code into `main` faster while keeping production releases conservative.

### The Pipeline

1. **`main` (The Alpha Stream):**

* **Target:** Merges happen here once CI passes + 1 Peer Review.
* **Purpose:** Feeds a "Canary Mint" for real-world integration testing.

1. **`release/vX.X` (The Beta Stream):**

* **Target:** Stabilized features cherry-picked from `main`.
* **Purpose:** Monthly beta tags for integrators and early adopters.

1. **`stable` (Production):**

* **Target:** Quarterly "Golden" releases.
* **Purpose:** Verified, high-uptime releases for production mint operators.

---

## 4. Triage & Archive Strategy (The Cleanup)

We will execute a "Three-Bucket" triage to clear the backlog within 30 days.

### Bucket A: The "Fast-Track" (Merge within 7 days)

Items that are low-risk, high-value, or fix active bugs.

* **Priority PRs:** #892 (Keyset rotation fix), #786 (Max fee flag), #811 (Nut-11 refactor).
* **Action:** Direct maintainer review and merge.

### Bucket B: The "Archive" (Move to Discussions/Wiki)

Items that are valuable ideas but lack an active implementation path.

* **Target:** All "Draft" PRs >6 months old (e.g., #287, #335).
* **Action:** Close with a "Thank You" comment and move the core concept to **GitHub Discussions** under a "Feature Backlog" category.

### Bucket C: The "Revive" (Status Check)

Items critical to the protocol that have stalled.

* **Target:** #491 (Keyset rotation), #574 (Pydantic 2.0).
* **Action:** Comment requesting a status update; if no response in 14 days, convert to a "Help Wanted" issue.

---

## 5. Automation & Infrastructure

To sustain this velocity, we will implement the following "Silent Partners":

* **Automated Triage Bot:** Automatically labels incoming PRs by scope (`mint`, `wallet`, `protocol`).
* **Friendly Stale Workflow:** Pings contributors at 60 days, gently moves to archive at 90 days.
* **CI Force Multipliers:** Parallelize the `pytest` suite and re-enable `LIGHTNING=True` integration tests as a merge requirement.

---

## 6. Immediate Next Steps

* **[ ] Labeling Blitz:** This week, ensure every open issue has a `priority` and `scope` tag.
* **[ ] The "Draft" Purge:** Close and archive the 21 stagnant Draft PRs.
* **[ ] Public Roadmap:** Publish a "Monthly Focus" issue so contributors know where to point their energy.
