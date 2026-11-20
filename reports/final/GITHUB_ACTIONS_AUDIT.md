# GitHub Actions evidence and current scope

Historical source7d46aea completed these real runs successfully:

| Workflow | Outcome at that source | Run |
| --- | --- | --- |
| Backend | PASS | https://github.com/afrochic/RetailAssistant/actions/runs/44630560678 |
| Frontend | PASS | https://github.com/afrochic/RetailAssistant/actions/runs/44630566673 |
| Docker | PASS | https://github.com/afrochic/RetailAssistant/actions/runs/44630571832 |

The earlier baseline frontend failed Next's internal-link lint rule, which was corrected. These historical runs do not validate the new Client X transformation. Raw metadata dumps revealing the original client-named branch were withdrawn from this snapshot; originals are privately retained. Existing externally hosted logs/history are not scrubbed by this cleanup.

All workflow triggers remain manual. Current validation covers API tests, frontend typecheck/lint/build and Docker configuration/build. The legacy workflow now runs from legacy/flipkart explicitly, with moved dependency paths. Current production workflows retain manual confirmation and environment gates; actual GitHub reviewer protection remains UNVERIFIED. Labelled ranking evaluation remains BLOCKED; it must not produce fabricated passing metrics.

See CLEANUP_VALIDATION.md for current local outcomes and any new branch-run URLs recorded after publication. No production workflow or cloud deployment is part of this cleanup.

## Client X source verification

Exact application/archive source: 5436ed89e1d7b0d2737bc4affb571d6a39c618a8 on cleanup/client-x-submission. Controlled manual, non-production workflows:

| Workflow | Actual outcome | Run |
| --- | --- | --- |
| Backend | PASS | https://github.com/afrochic/RetailAssistant/actions/runs/44692431692 |
| Frontend | PASS | https://github.com/afrochic/RetailAssistant/actions/runs/44692435830 |
| Docker | PASS | https://github.com/afrochic/RetailAssistant/actions/runs/44692439969 |

Minimal current metadata is in ci/client_x_runs.json. The first dispatch referenced the preceding 720ccc1 snapshot before final archive preservation; current validation uses the exact final 5436ed8 source instead. No production workflow, deployment or merge was performed. Review PR: https://github.com/afrochic/RetailAssistant/pull/3 .

PR #3 is ready for review after all three workflows passed; it remains unmerged. No production deployment was performed.
