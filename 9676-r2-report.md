Addressed all four review r1 findings for [PolicyEngine US #9676](https://github.com/PolicyEngine/policyengine-us/pull/9676), starting from `b9e7fff948`.

- Updated the PR body with both regression directions, including the grandmother aged 58 with $500/month UC: $234.08628 → $0. Saved paired entitlement records gaining/losing are 0/0 unmodified, 0/1 with grandparents marked, and 2/1 with marks plus bank assets zeroed, in both 2025 and 2026. Actual TANF counts remain 0/0.
- Disclosed the review's three Missouri NPCR changes: the great-grandparent case, integration underpayment case, and adult-parent property expectation. The 623 partner cases retain unchanged expectations. Renamed the NPCR property test to describe current behavior.
- Documented why an explicit parent flag cannot attach a child across tax units. A real parent filing separately remains excluded when their own unit has no dependent child; this legally mandatory membership remains unmodeled.

Ran two YAML files sequentially on Python 3.14.4 / Core 3.32.8: annual parent-input tests **2 passed**, membership tests **17 passed**. Each new case passed:

- Annual override leaves adjacent years using the default.
- January snapshot persists after a child ages out in July.
- Separate-return biological parent retains explicit true while remaining excluded.

`make format` passed before each commit, including lint. Formula ASTs are unchanged; partner files are untouched. No formula change affects the default dataset, and no microsimulations were run. The 12–50 window and interpretation (i) remain unchanged and queued for Max as d1049.

Code/test commit: `02cc448746`. Changes and this report were committed on `mo-tanf-dependent-parent-member` and pushed as a fast-forward; the PR body was updated. No merge or force-push. All writes stayed in the assigned workspace, using local Git metadata at `.r2/git` because the sandbox blocks writes to the caller's repository metadata. Test logs and the body draft are in `.r2/`.
