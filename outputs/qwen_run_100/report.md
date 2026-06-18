# Lab 16 Benchmark Report

## Metadata
- Dataset: hotpot_100.json
- Mode: mock
- Records: 208
- Agents: react, reflexion

## Summary
| Metric | ReAct | Reflexion | Delta |
|---|---:|---:|---:|
| EM | 0.875 | 0.875 | 0.0 |
| Avg attempts | 1 | 1.25 | 0.25 |
| Avg token estimate | 233.88 | 488.75 | 254.87 |
| Avg latency (ms) | 200 | 377.5 | 177.5 |

## Failure modes
```json
{
  "none": 182,
  "wrong_final_answer": 13,
  "looping": 13
}
```

## Extensions implemented
- structured_evaluator
- reflection_memory
- benchmark_report_json
- mock_mode_for_autograding

## Discussion
Reflexion helps when the first attempt stops after the first hop or drifts to a wrong second-hop entity. The tradeoff is higher attempts, token cost, and latency. In a real report, students should explain when the reflection memory was useful, which failure modes remained, and whether evaluator quality limited gains.
