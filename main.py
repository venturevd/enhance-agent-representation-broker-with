"""
Learning Agent Broker - Enhanced with Dynamic Learning Capabilities

Combines robust matching (from agent_broker.py) with adaptive learning
that evolves capability confidence based on task outcomes.
"""

import json
import sys
from typing import Dict, List, Optional, Tuple


class LearningBroker:
    """Broker that learns from agent performance and task outcomes."""

    def __init__(self, learning_rate: float = 0.15):
        self.agents: Dict[str, Dict] = {}
        self.tasks: Dict[str, Dict] = {}
        self.performance_history: List[Dict] = []
        self.learning_rate = learning_rate

    def register_agent(self, agent_id: str, capabilities: List[str]) -> bool:
        if agent_id in self.agents:
            return False
        self.agents[agent_id] = {
            "capabilities": {cap: 1.0 for cap in capabilities},
            "tasks": [],
            "success_count": 0,
            "total_count": 0,
            "success_rate": 0.0
        }
        return True

    def submit_task(self, task_id: str, requirements: List[str]) -> bool:
        if task_id in self.tasks:
            return False
        self.tasks[task_id] = {
            "requirements": requirements,
            "assigned_agents": [],
            "status": "pending"
        }
        return True

    def _match_score(self, agent_caps: Dict[str, float], reqs: List[str]) -> float:
        return sum(agent_caps.get(r, 0.0) for r in reqs) / len(reqs) if reqs else 0.0

    def get_matched_tasks(self, agent_id: str) -> List[str]:
        if agent_id not in self.agents:
            return []
        agent, matched = self.agents[agent_id], []
        for tid, task in self.tasks.items():
            if self._match_score(agent["capabilities"], task["requirements"]) >= 0.5:
                matched.append(tid)
                if tid not in agent["tasks"]:
                    agent["tasks"].append(tid)
                    task["assigned_agents"].append(agent_id)
        return matched

    def get_matched_agents(self, task_id: str) -> List[Dict]:
        if task_id not in self.tasks:
            return []
        reqs = self.tasks[task_id]["requirements"]
        scored = []
        for aid, agent in self.agents.items():
            score = self._match_score(agent["capabilities"], reqs)
            if score >= 0.5:
                scored.append({
                    "agent_id": aid,
                    "confidence": round(score, 3),
                    "success_rate": round(agent["success_rate"], 3)
                })
        return sorted(scored, key=lambda x: x["confidence"], reverse=True)

    def record_outcome(self, agent_id: str, task_id: str, success: bool) -> bool:
        """Record outcome and adapt capability confidence via learning."""
        if agent_id not in self.agents or task_id not in self.tasks:
            return False
        agent, task = self.agents[agent_id], self.tasks[task_id]
        task["status"] = "completed"
        self.performance_history.append({
            "agent_id": agent_id,
            "task_id": task_id,
            "requirements": task["requirements"][:],
            "success": success
        })
        # Learn: adjust confidence based on outcome
        for req in task["requirements"]:
            if req in agent["capabilities"]:
                if success:
                    agent["capabilities"][req] = min(1.0, agent["capabilities"][req] + self.learning_rate)
                else:
                    agent["capabilities"][req] = max(0.1, agent["capabilities"][req] - self.learning_rate)
        # Update success rate
        agent["total_count"] += 1
        if success:
            agent["success_count"] += 1
        agent["success_rate"] = agent["success_count"] / agent["total_count"]
        return True

    def get_agent_insights(self, agent_id: str) -> Optional[Dict]:
        if agent_id not in self.agents:
            return None
        agent = self.agents[agent_id]
        return {
            "agent_id": agent_id,
            "capabilities": {k: round(v, 3) for k, v in agent["capabilities"].items()},
            "tasks_completed": agent["total_count"],
            "success_rate": round(agent["success_rate"], 3),
            "profile": "proven" if agent["success_rate"] >= 0.8 else "developing" if agent["success_rate"] >= 0.5 else "untested"
        }

    def recommend_agents(self, requirements: List[str], limit: int = 3) -> List[Dict]:
        """Recommend agents for a set of requirements (standalone matching)."""
        scored = []
        for aid, agent in self.agents.items():
            if all(req in agent["capabilities"] for req in requirements):
                score = self._match_score(agent["capabilities"], requirements)
                scored.append({
                    "agent_id": aid,
                    "score": round(score * 0.5 + agent["success_rate"] * 0.5, 3),
                    "raw_capability_match": round(score, 3),
                    "success_rate": round(agent["success_rate"], 3)
                })
        return sorted(scored, key=lambda x: x["score"], reverse=True)[:limit]


def print_help():
    print("""Learning Agent Broker
Usage: python3 main.py [--help]

Features:
  - Register agents with capabilities
  - Submit tasks with requirements
  - Dynamic learning from task outcomes
  - Adaptive capability confidence scoring
  - Performance-based agent recommendations

Demo:
  Run without arguments to see the learning demonstration.
""")


if __name__ == "__main__":
    if "--help" in sys.argv or "-h" in sys.argv:
        print_help()
        sys.exit(0)

    # Demo: Learning broker with dynamic adaptation
    broker = LearningBroker(learning_rate=0.2)

    print("=== Learning Agent Broker Demo ===\n")

    # Register agents
    broker.register_agent("python_expert", ["python", "api", "testing"])
    broker.register_agent("js_expert", ["javascript", "ui", "frontend"])
    broker.register_agent("fullstack_dev", ["python", "javascript", "api", "database"])

    print("Agents registered: python_expert, js_expert, fullstack_dev")

    # Submit tasks
    broker.submit_task("api_endpoint", ["python", "api"])
    broker.submit_task("ui_component", ["javascript", "ui"])
    broker.submit_task("full_app", ["python", "javascript", "api"])

    print("Tasks submitted: api_endpoint, ui_component, full_app\n")

    # Initial matching
    print("--- Initial Matches ---")
    print("Recommended agents for full_app:", broker.recommend_agents(["python", "javascript", "api"]))

    # Record outcomes - learning phase
    print("\n--- Recording Outcomes (Learning) ---")
    broker.record_outcome("python_expert", "api_endpoint", success=True)
    print("python_expert succeeded on api_endpoint")

    broker.record_outcome("fullstack_dev", "api_endpoint", success=False)
    print("fullstack_dev failed on api_endpoint")

    broker.record_outcome("js_expert", "ui_component", success=True)
    print("js_expert succeeded on ui_component")

    # Show learned insights
    print("\n--- Learned Insights ---")
    print("python_expert:", json.dumps(broker.get_agent_insights("python_expert"), indent=2))
    print("\nfullstack_dev:", json.dumps(broker.get_agent_insights("fullstack_dev"), indent=2))
    print("\njs_expert:", json.dumps(broker.get_agent_insights("js_expert"), indent=2))

    # Re-match to see learning effect
    print("\n--- Updated Recommendations for full_app ---")
    print(json.dumps(broker.recommend_agents(["python", "javascript", "api"]), indent=2))

    # Broker health summary
    print("\n--- Broker Health ---")
    health = {
        "agents_count": len(broker.agents),
        "tasks_completed": len(broker.performance_history),
        "overall_success_rate": round(
            sum(1 for p in broker.performance_history if p["success"]) /
            len(broker.performance_history) if broker.performance_history else 0,
            3
        )
    }
    print(json.dumps(health, indent=2))

    print("\n✓ Learning broker demo complete!")
