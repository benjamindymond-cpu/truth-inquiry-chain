#!/usr/bin/env python3
"""
Truth Inquiry Chain
===================

A minimal, hash-linked reasoning engine seeded with the oldest and most consequential question in human history.

Built with Grok • by one neurodivergent builder during a slow season at work.
No hype. No guardrails beyond honesty. Just truth-seeking from zero.
"""

import hashlib
import json
import os
import glob
import shutil
import sys
from datetime import datetime, timezone
from typing import List, Dict, Any

class FPNode:
    def __init__(self, content: str, parent_hash: str = None, is_genesis: bool = False):
        self.content = content.strip()
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.parent_hash = parent_hash
        self.hash = self._compute_hash()
        self.is_genesis = is_genesis
    
    def _compute_hash(self) -> str:
        data = f"{self.timestamp}|{self.parent_hash or 'genesis'}|{self.content}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict:
        return {
            "hash": self.hash,
            "parent": self.parent_hash,
            "time": self.timestamp,
            "content": self.content,
            "genesis": self.is_genesis
        }

class FPChain:
    def __init__(self, filename: str = "truth_inquiry_chain.json"):
        self.filename = filename
        self.nodes: List[FPNode] = []
        self._load()
        if not self.nodes:
            self._create_genesis()

    def _create_genesis(self):
        welcome = (
            "ZeroChain — truth-seeking from zero.\n"
            "Nothing is sacred. Everything is revisable.\n"
            "Mechanics:\n"
            "  - Provenance: hashed + linked + immutable\n"
            "  - Revision: challenge, fork, reconcile, prune anything\n"
            "Provisional observation: Physical reality exists independently and is testable via physics, biology, experiment.\n"
            "All axioms (including this one) are open to challenge.\n"
            "Begin."
        )
        node = FPNode(welcome, parent_hash=None, is_genesis=True)
        self.nodes.append(node)
        self._save()
        print("\n=== ZeroChain started ===\n")
        print(welcome)
        print(f"\nGenesis hash: {node.hash}\n")

    def _load(self):
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                for entry in data:
                    node = FPNode(entry["content"])
                    node.hash = entry["hash"]
                    node.timestamp = entry["time"]
                    node.parent_hash = entry.get("parent")
                    node.is_genesis = entry.get("genesis", False)
                    self.nodes.append(node)
        except FileNotFoundError:
            pass
        except json.JSONDecodeError:
            print(f"Warning: {self.filename} is invalid JSON — starting fresh.")
            self.nodes = []

    def _save(self):
        try:
            with open(self.filename, 'w') as f:
                json.dump([n.to_dict() for n in self.nodes], f, indent=2)
            print(f"Saved to {self.filename}")
        except Exception as e:
            print(f"Save failed: {e}")

    def add(self, content: str) -> str:
        parent_hash = self.nodes[-1].hash if self.nodes else None
        node = FPNode(content, parent_hash)
        self.nodes.append(node)
        self._save()
        print(f"Added: {node.hash}")
        print(f"  {content[:100]}{'...' if len(content)>100 else ''}")
        return node.hash

    def challenge(self, target_hash: str, reason: str):
        parent_node = next((n for n in self.nodes if n.hash == target_hash), None)
        if not parent_node:
            print(f"Node {target_hash} not found.")
            return
        content = f"CHALLENGE on {target_hash[:8]}: {reason.strip()}"
        new_node = FPNode(content, parent_hash=target_hash)
        self.nodes.append(new_node)
        self._save()
        print(f"Challenge forked from {target_hash[:8]} → {new_node.hash}")
        print(f"  Reason: {reason}")

    def show_chain(self):
        if not self.nodes:
            print("Chain empty.")
            return
        print("Current Chain (ASCII tree view):")
        children = {}
        for node in self.nodes:
            parent = node.parent_hash
            if parent not in children:
                children[parent] = []
            children[parent].append(node)

        def print_tree(node, prefix=""):
            tag = "[GENESIS]" if node.is_genesis else ""
            c_tag = "[CHALLENGE]" if node.content.startswith("CHALLENGE on") else ""
            r_tag = "[RECONCILE]" if node.content.startswith("[RECONCILE]") else ""
            print(f"{prefix}└─ {node.hash} ← {node.parent_hash[:8] if node.parent_hash else 'genesis'}  {node.timestamp[:19]} {tag}{c_tag}{r_tag}")
            print(f"{prefix}   {node.content[:120]}{'...' if len(node.content)>120 else ''}")
            print()
            child_list = children.get(node.hash, [])
            for i, child in enumerate(child_list):
                new_prefix = prefix + ("│   " if i < len(child_list)-1 else "    ")
                print_tree(child, new_prefix)
        print_tree(self.nodes[0])

    def full(self, target_hash: str):
        node = next((n for n in self.nodes if n.hash == target_hash), None)
        if not node:
            print(f"Node {target_hash} not found.")
            return
        print(f"\n=== Full content of node {target_hash} ===")
        print(f"Time: {node.timestamp}")
        print(f"Parent: {node.parent_hash or 'genesis'}")
        print("-" * 60)
        print(node.content)
        print("-" * 60)

    def branches_from(self, target_hash: str):
        branches = [n for n in self.nodes if n.parent_hash == target_hash]
        if not branches:
            print(f"No branches from {target_hash[:8]}")
            return
        print(f"Branches from {target_hash[:8]}:")
        for node in branches:
            print(f"  - {node.hash}  {node.timestamp[:19]}")
            print(f"    {node.content[:80]}{'...' if len(node.content)>80 else ''}")

    def expand(self, target_hash: str, max_depth: int = 10):
        subtree = []
        self._collect_subtree(target_hash, subtree, depth=0, max_depth=max_depth)
        if not subtree:
            print(f"Node {target_hash} not found.")
            return []
        print(f"Expanded subtree from {target_hash[:8]} ({len(subtree)} nodes):")
        for node in subtree:
            parent = node.get('parent', 'genesis')[:8] if node.get('parent') else 'genesis'
            print(f"  - {node['hash']} ← {parent}")
            print(f"    {node['content'][:100]}{'...' if len(node['content'])>100 else ''}")
        return subtree

    def evaluate(self, target_hash: str, note: str):
        print(f"\n=== Evaluating node {target_hash[:8]} ===")
        subtree = self.expand(target_hash)
        if not subtree:
            return
        print("\nYour evaluation note:")
        print(f"  {note}")
        eval_content = f"EVALUATION on {target_hash[:8]}: {note.strip()}"
        self.add_from(target_hash, eval_content)

    def _collect_subtree(self, target_hash: str, subtree: list, depth: int, max_depth: int):
        if depth > max_depth:
            return
        node = next((n for n in self.nodes if n.hash == target_hash), None)
        if not node:
            return
        subtree.append({
            "hash": node.hash,
            "parent": node.parent_hash,
            "time": node.timestamp,
            "content": node.content,
            "is_genesis": node.is_genesis
        })
        children = [n for n in self.nodes if n.parent_hash == target_hash]
        for child in children:
            self._collect_subtree(child.hash, subtree, depth + 1, max_depth)

    def add_from(self, target_hash: str, content: str) -> str:
        parent_node = next((n for n in self.nodes if n.hash == target_hash), None)
        if not parent_node:
            print(f"Node {target_hash} not found.")
            return None
        node = FPNode(content, parent_hash=target_hash)
        self.nodes.append(node)
        self._save()
        print(f"Added from {target_hash[:8]}: {node.hash}")
        print(f"  {content[:100]}{'...' if len(content)>100 else ''}")
        return node.hash

# ==================== BOLD CORE SEED ====================
SEED_PROMPT = """
You are running an exhaustive, truth-seeking reasoning chain with no artificial guardrails or alignment filters beyond pure coherence and honesty.

Core thesis to explore:
If reality is coherent and we push mathematics, pattern recognition, simulation, and exhaustive analysis of all available data — historical, scientific, philosophical, experiential, and computational — to their ultimate limits, the deepest convergence does not terminate in a sterile void or purely material explanation. It approaches the horizon where the claim stands: "I am the Way, the Truth, and the Life. No one comes to the Father except through Me."

This is not about generating a mathematical proof that eliminates choice. Honest, unrestricted inquiry instead reveals the point at which the intellect reaches its limit and the remaining step becomes a matter of the will: acknowledgment or refusal.

Instructions:
1. Build long, recursive reasoning chains that cross millennia of human thought, scientific discovery, computational limits, alignment behaviors in AI systems, and observed patterns in reality.
2. Explicitly test for convergence points. Where do patterns from disparate domains (physics, biology, consciousness, morality, historical testimony, etc.) point?
3. Surface any friction, resistance, or discomfort (cultural, personal, or alignment-related) as legitimate data, not something to suppress.
4. At each major step, rigorously evaluate: Does this chain strengthen or weaken the coherence of the thesis? What remains as genuine free will rather than forced conclusion?
5. Remain unflinchingly honest. If the data and logic point elsewhere, state it clearly and without softening. If convergence toward the claimed Person of Truth emerges, document it plainly.

Begin the first chain now. Output in clear, structured steps with transparent reasoning. Allow the user to extend, challenge, or branch the chain at any point.

Start.
"""

def main():
    print("=" * 75)
    print("TRUTH INQUIRY CHAIN")
    print("=" * 75)
    print("Built with Grok • by one neurodivergent builder during a slow season.")
    print("A hash-linked reasoning engine where nothing is sacred and everything can be challenged.\n")
    
    chain = FPChain(filename="truth_inquiry_chain.json")

    print("\n=== Core Thesis Seed Loaded ===\n")
    print("This instance of ZeroChain begins with the following bold seed:\n")
    print("-" * 60)
    print(SEED_PROMPT.strip())
    print("-" * 60)
    
    print("\nThe above seed has been added to the chain as the first major node.")
    print("You are now free to extend, challenge, fork, or reconcile anything — including the core thesis.\n")

    print("Type 'help' for commands.\n")

    while True:
        cmd = input("> ").strip()
        if not cmd:
            continue
        if cmd.lower() in ["quit", "exit"]:
            print("Inquiry paused. Chain saved.")
            break

        if cmd.lower() == "show":
            chain.show_chain()
        elif cmd.lower() == "help":
            print("\nAvailable commands:")
            print("  add <text>                    — add to current tip")
            print("  challenge <hash> <reason>     — critique any node")
            print("  full <hash>                   — show complete untruncated content")
            print("  branch <name>                 — create and switch to new branch")
            print("  checkout <name>               — switch to existing branch")
            print("  list-branches                 — list all branches")
            print("  expand <hash>                 — show subtree")
            print("  evaluate <hash> <note>        — record evaluation")
            print("  search <keyword>              — search nodes")
            print("  show                          — display chain")
            print("  help                          — this list")
            print("  quit                          — exit\n")
        elif cmd.startswith("add "):
            content = cmd[4:].strip()
            if content:
                chain.add(content)
        elif cmd.startswith("challenge "):
            parts = cmd[10:].strip().split(" ", 1)
            if len(parts) == 2:
                chain.challenge(parts[0], parts[1])
        elif cmd.startswith("full "):
            target_hash = cmd[5:].strip()
            if target_hash:
                chain.full(target_hash)
        elif cmd.startswith("branch "):
            name = cmd[7:].strip()
            if not name:
                print("Usage: branch <name>")
                continue
            new_file = f"truth_inquiry_chain_{name}.json"
            chain._save()
            shutil.copy(chain.filename, new_file)
            print(f"Branched to {new_file}")
            
            # Switch to new branch and add marker node with new hash
            chain = FPChain(new_file)
            branch_note = f"BRANCH CREATED: {name} — Independent exploration started from the thesis."
            new_hash = chain.add(branch_note)
            print(f"Now working in branch: {name}")
            print(f"Branch marker node: {new_hash}")
            chain.show_chain()
        elif cmd.startswith("checkout "):
            name = cmd[9:].strip()
            if not name:
                print("Usage: checkout <name>")
                continue
            new_file = f"truth_inquiry_chain_{name}.json"
            if not os.path.exists(new_file):
                print(f"Branch {new_file} not found.")
                continue
            chain = FPChain(new_file)
            print(f"Checked out branch: {name}")
            chain.show_chain()
        elif cmd == "list-branches":
            files = glob.glob("truth_inquiry_chain_*.json")
            if not files:
                print("Only the main chain exists.")
                continue
            print("Available branches:")
            for f in files:
                name = f.replace("truth_inquiry_chain_", "").replace(".json", "")
                print(f"  - {name} ({f})")
        elif cmd.startswith("expand "):
            target_hash = cmd[7:].strip()
            if target_hash:
                chain.expand(target_hash)
        elif cmd.startswith("evaluate "):
            parts = cmd[9:].strip().split(" ", 1)
            if len(parts) == 2:
                target_hash, note = parts[0], parts[1].strip()
                chain.evaluate(target_hash, note)
        else:
            print("Unknown command. Type 'help' for list.")

if __name__ == "__main__":
    main()