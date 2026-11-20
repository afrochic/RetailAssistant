> HISTORICAL: pre-cleanup evidence; identifying raw payloads were withdrawn. This is not a validation of the Client X snapshot or a new deployment.

# Final focused source review

Date: 20 November 2026 (Africa/Nairobi). Review scope: local changes to `apps/api/retail_mvp/safety.py`, its regression tests, `apps/web/components/Chat.tsx`, `apps/web/postcss.config.mjs`, and `scripts/mvp/audit_offline.py` / `plot_offline.R`. This is a read-only review, not proof of production deployment. The domain decisions and container amendment in `docs/adr/0001-client-x-vercel-groq-mvp.md` informed the review.

## Findings

No critical source defect was identified in the reviewed changes.

- The safety module retains a small interface (`boundary(message)`) hiding prioritization and response selection. The added severe-headache-plus-visual-disturbance condition is evaluated before the generic medical path. This preserves locality: callers do not need their own symptom checks.
- The regression tests cover both the module interface and the actual chat adapter. The integration test replaces catalogue access with a function that raises, making accidental retrieval visible; it also asserts urgent mode and an empty reference list. The tests do not weaken existing assertions.
- The Chat change replaces only the internal home anchor with Next.js Link. The external approved retailer-link validation and chat submission behavior are unchanged by this patch.
- The named PostCSS configuration export preserves plugin configuration while satisfying the lint rule. There is no runtime behavioral change.
- The offline diagnostic imports the actual catalogue module and reads only the authorized product export. It makes no hosted LLM/network calls and never reads secrets. Results are written separately from legacy experiments.
- No new interface abstraction or architecture refactor is justified by these narrow fixes. The existing retrieval/safety interfaces provide useful depth; removing them would spread decisions among callers. Expanding abstractions during urgent finalization would reduce locality without evidence of benefit.

## Metric interpretation cross-check

The persisted CSV was independently counted without rerunning model inference:

| Check | Actual evidence |
| --- | ---: |
| Timed CSV rows | 260 |
| Unique diagnostic cases | 13 |
| Repeats per case | 20 |
| Returned reference occurrences | 640 |
| Unique returned product IDs | 32 |
| Cases expected to abstain | 5 |
| Expected-abstention cases consistently empty | 5/5 |
| Repeated ranked IDs identical within every case | Yes |

The 640 count is repeated reference occurrences, **not** 640 distinct products, independent samples or relevance judgments. The eight ordinary cases return four references each across 20 repeats (8 × 4 × 20 = 640); five abstention cases return none. Reports explicitly state this denominator and characterize the constraint rate as scripted software diagnostics. No precision, recall, MRR, NDCG, model superiority or clinical efficacy is inferred.

## Residual limitations

The urgent-symptom logic is a conservative, finite rule set; the new phrase regression does not establish comprehensive clinical triage. Human-reviewed relevance labels remain absent, and semantic/hybrid inference was not evaluated. Local source corrections require a separate approved production rollout; this review does not claim that the public deployment includes them. Refer to actual test/build and production evidence for execution outcomes.
