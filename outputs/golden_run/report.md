# Lab 16 Benchmark Report

## Metadata
- Dataset: hotpot_golden.json
- Mode: live
- Records: 40
- Agents: react, reflexion

## Summary
| Metric | ReAct | Reflexion | Delta |
|---|---:|---:|---:|
| EM | 0.8 | 1.0 | 0.2 |
| Avg attempts | 1 | 1.2 | 0.2 |
| Avg token estimate | 322.95 | 478.2 | 155.25 |
| Avg latency (ms) | 200 | 356 | 156 |

## Failure modes
```json
{
  "none": 36,
  "wrong_final_answer": 4
}
```

## Extensions implemented
- structured_evaluator
- reflection_memory
- benchmark_report_json
- mock_mode_for_autograding

## Discussion
Reflexion helps when the first attempt stops after the first hop or drifts to a wrong second-hop entity. The tradeoff is higher attempts, token cost, and latency. In a real report, students should explain when the reflection memory was useful, which failure modes remained, and whether evaluator quality limited gains.
