# Evaluation

## Methodology

```
Question
    │
    ▼
Hybrid Retrieval        ← BM25 + Pinecone + RRF
    │
    ▼
Claude Answer           ← Anthropic Claude Sonnet
    │
    ▼
Metric Calculation      ← token-overlap heuristics
```

## Metrics

### Faithfulness

Measures whether the generated answer content is supported by the retrieved context.

Calculated using context–answer token overlap heuristic.

### Answer Relevancy

Measures whether the generated answer addresses the user's original question.

Calculated using question–answer token overlap heuristic.

### Context Precision

Measures whether the retrieved chunks are useful for producing the final answer.

Calculated as average token overlap between each retrieved chunk and the question.