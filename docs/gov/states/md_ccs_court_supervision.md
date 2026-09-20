# Maryland CCS court supervision

The [approved FFY 2025–2027 CCDF plan, §2.2.1(c), PDF page 23](https://earlychildhood.marylandpublicschools.org/system/files/filedepot/12/acf-118_ccdf_ffy_2025-2027_plan_approved_updated_6.25.25_amendment_request_1.pdf#page=23) elects child-care eligibility for court-supervised children through age 18. The model follows that affirmative election from October 1, 2024, the plan period's start. It uses the existing under-19 disability ceiling for both older-child routes; court supervision does not set disability status.

This is an explicit source choice: [COMAR 13A.14.06.02B(11),(16)](https://regs.maryland.gov/us/md/exec/comar/13A.14.06.02) still describes older children through disability only. The plan's election is used for modeled court-supervision eligibility; the discrepancy with COMAR remains documented rather than treated as a regulatory amendment.

The current-plan formula does not infer protective-services status or waive income, activity, immigration or copayment requirements. The plan declines the protective-services reason-for-care category in §2.2.2(f). A supervised parent does not extend a child's age eligibility, and eligibility ends at the child's 19th birthday under the model's annual-age convention.

The dated formula preserves the previous calculation before October 2024. This implementation date is the scope of current-plan coverage, not a finding that Maryland first elected the option in 2024: the earlier FFY 2022–2024 plan also reported an affirmative election, but historical implementation is not expanded in this current-plan change. Existing birthday/renewal and payment approximations are unchanged.

YAML regressions cover age and plan-period boundaries, default false, immigration, ordinary disability eligibility, mixed siblings and supervised adults, actual payment rates, copayments, income/activity exclusions and no reported childcare expenses.
