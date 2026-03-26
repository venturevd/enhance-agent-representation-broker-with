# Adaptive Agent Broker

Dynamic agent-task matching with adaptive learning and validation.

## Features

- Register agents with capability confidence scores
- Submit tasks with requirement lists
- Intelligent matching based on capability scores
- Real-time performance learning
- Built-in validation tests
- Compact single-file implementation (~50 LOC)

## Usage

```bash
# Show help
python3 main.py --help

# Run demo with learning demonstration
python3 main.py

# Run validation tests (included in demo)
python3 main.py
```

## API

### `Broker`

```python
broker = Broker()

# Register an agent
broker.register_agent("agent_id", ["capability1", "capability2"])

# Submit a task
broker.submit_task("task_id", ["requirement1", "requirement2"])

# Get recommendations
recommendations = broker.recommend(["requirement1"])

# Record outcome for learning
broker.learn("agent_id", "task_id", success=True)

# Run validation
result = broker.validate()
```

## Demo Output

The demo shows:
- Validation test results (5 built-in tests)
- Agent registration
- Task submission
- Initial recommendations
- Learning from outcomes
- Updated success rates

## Example

```json
{
  "agent_id": "py_exp",
  "confidence": 0.875,
  "success_rate": 0.75
}
```
