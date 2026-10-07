Implemented the five round-2 requests for [PolicyEngine US #9184](https://github.com/PolicyEngine/policyengine-us/pull/9184), based on `b24094b166`. The implementation commits were fast-forwarded to `ltss-financial-eligibility`; the PR body is updated. No merge or force-push was performed.

- Delaware sums spouses' individual home-ownership shares within their marital unit. Two 50% owners of a mortgage-free $1,000,000 retained home fail the $752,000 cap; a $752,000 home passes. Individual budgeting does not split that interest. Callers supply both individual shares and the same whole-home value/encumbrances. [DSSM §20320.7.C](https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=17).
- Added `medicaid_ltss_is_initial_eligibility_determination`, default true. Continuing eligibility tests applicant resources alone: $2,000 with spouse $60,000 passes; $2,001 with spouse $0 fails. Initial/default controls retain CSRA budgeting. [42 USC §1396r-5(c)(4)](https://www.govinfo.gov/content/pkg/USCODE-2024-title42/html/USCODE-2024-title42-chap7-subchapXIX-sec1396r-5.htm).
- Washington MNIL follows canonical SSI uprating. The 2027 COPES case ($4,000 − $500 − $2,500 = $1,000) passes. The annual basis is [WAC 182-519-0050(1), (5)](https://app.leg.wa.gov/wac/default.aspx?cite=182-519-0050).
- Washington MMMNA uses the published $2,644 minimum/$794 shelter threshold in January: $1,000 shelter gives $2,850, versus bare arithmetic's $2,850.625. July uses $2,705/$812. The PR body explains the difference and Max's d1011 precedent. [January chart](https://www.hca.wa.gov/assets/free-or-low-cost/income-standards-20260101.pdf), [July chart](https://www.hca.wa.gov/assets/free-or-low-cost/income-standards-20260701.pdf).
- Updated reviewer responses, methodology and completed impact evidence. The invariant fixture now gives independent applicants singleton marital units; all existing assertions remain.

All requested files ran individually, with no concurrent test processes:

| File | Before fix | After fix |
|---|---:|---:|
| medicaid_ltss_home_equity_eligible.yaml | 2 failed, 14 passed | 16 passed |
| medicaid_ltss_csra_resource_eligible.yaml | 2 failed, 21 passed | 23 passed |
| is_medicaid_ltss_income_eligible.yaml | 1 failed, 13 passed | 14 passed |
| medicaid_ltss_mmmna.yaml | 2 failed, 7 passed | 9 passed |
| medicaid_ltss_financial_pathway.yaml | — | 15 passed |
| medicaid_ltss_special_income_limit.yaml | — | 2 passed |
| is_medicaid_ltss_financial_threshold_eligible.yaml | — | 10 passed |
| test_medicaid_ltss_financial_invariants.py | — | 18 passed |

The seven expected failures used unchanged `b24094b166` formulas/parameters; only the new input schema was registered to accept the continuing flag. Regression commit `42624f99fa` preserves that failing model. Total: **89 YAML cases and 18 invariants passed**. `make format` and lint passed before every commit. Failure/pass logs and the dependency audit are in `9184-r2-evidence/`. Equity’s tests passed; optional peak-memory instrumentation was denied by the sandbox.

The hub's real 2026/2028 microsimulation, merge base `6b80a8e447` versus `b24094b166`, measured exactly zero changes in `is_medicaid_eligible`, `medicaid`, `household_health_benefits`, `household_net_income` and `household_net_income_including_health_benefits`. That zero result carries over: the dependency audit found no existing consumers of the 28 financial screen/input variables, and no existing consumer or its parameters changes. The hub has no changed consumer to re-run.

Max's remaining choices, detailed in the PR body:

- **Standalone equity:** retain the independent screen and gate the composite. Alternative: gate the standalone result too. Independence preserves the statutory equity information; law fixes the bar/exceptions but leaves API organization open.
- **Couple budgeting:** callers supply the permitted unit/totals. Alternative: derive it from added residence/duration/election inputs. The contract avoids inventing administrative facts. Delaware law requires couple budgeting initially and leaves an individual/couple election open only after six months together in the institution; same-address HCBS couples use couple budgets.
- **Earned income:** retain the final-countable-income flag. Alternative: model separate raw earnings/unearned income and all exclusions. This bounds the trusted-input API. Law leaves representation open; deduction order is mandatory.

Future MNIL amounts use SSI projections. Federal CSRA/MMMNA and Washington chart amounts beyond their sourced 2026 values remain unverified future standards.

Six implementation/test commits: `42624f99fa`, `77c89729a4`, `cbb145281a`, `1925fa6ca2`, `24711fa628`, `688f0b4ea3`. Report, PR-body copy and test logs are saved in this workspace. Common Git metadata was read-only, so commits use private `.venv/.git-r2` metadata here; the caller's checkout was not written. **CI:** `gh pr checks` on code head `688f0b4ea3` confirmed Quick Feedback passed (7m44s). At 11:29 UTC, six checks succeeded, one was running and 28 were queued; no failures were reported. [Run 37612263818](https://github.com/PolicyEngine/policyengine-us/actions/runs/37612263818). Full CI is still in progress; the final documentation/evidence commit changes no model or test code.

No partner expected outputs changed. No merge was performed; DTrim99's re-review and Max's remaining choices are still outstanding.
