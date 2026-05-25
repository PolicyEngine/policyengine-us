# SSI-Recipient Medicaid in 209(b) States

## Issue

- GitHub issue: https://github.com/PolicyEngine/policyengine-us/issues/8443
- Request: model SSI-recipient Medicaid eligibility in states that use section 1902(f), commonly called 209(b) states.
- Variable prefix: `medicaid` / `is_209b_ssi_recipient_for_medicaid`

## Official Sources

1. SSA POMS SI 01715.010, "Medicaid and the Supplemental Security Income (SSI) Program"
   - URL: https://secure.ssa.gov/apps10/poms.nsf/lnx/0501715010
   - Effective 2017-10-02 to present; page shows TN 7 (01-24), batch run 2026-03-19.
   - Current 209(b) states listed by SSA: Connecticut, New Hampshire, Hawaii, North Dakota, Illinois, Minnesota, Virginia, Missouri.
   - Current SSI-criteria states include Oklahoma, so Oklahoma is not treated as a 209(b) state here.
   - POMS footnote: Connecticut, New Hampshire, and Missouri do not include nonblind individuals under age 18 in their definition of disability.

2. CMS MACPro Implementation Guide, "More Restrictive Requirements than SSI under 1902(f) - 209(b) States"
   - URL: https://www.medicaid.gov/resources-for-states/downloads/macpro-ig-more-restrictive-requirements-1902f-209bstates.pdf#page=2
   - Downloaded to `/tmp/ssi-medicaid-209b-sources/pdf/macpro-ig-more-restrictive-requirements-1902f-209bstates.pdf`.
   - Extracted text to `/tmp/ssi-medicaid-209b-sources/pdf/macpro-ig-more-restrictive-requirements-1902f-209bstates.txt`.
   - Rendered images to `/tmp/ssi-medicaid-209b-sources/rendered/macpro-209b-01.png` through `macpro-209b-13.png` at 300 DPI.
   - Key points:
     - 209(b) applies only to aged, blind, or disabled Medicaid eligibility.
     - States may apply more restrictive criteria to aged, blind, disabled, or combinations of those populations.
     - Criteria may not be more restrictive than the state's Medicaid plan on January 1, 1972.
     - Receipt of SSI does not guarantee Medicaid in 209(b) states, but SSI recipients can still qualify if they meet the state's more restrictive requirements.
     - Special deductions and spenddown rules apply under 42 CFR 435.121(f).

3. 42 CFR 435.120, individuals receiving SSI
   - URL: https://www.ecfr.gov/current/title-42/section-435.120
   - Backup readable source used during research: https://www.law.cornell.edu/cfr/text/42/435.120
   - Rule: except as allowed under 42 CFR 435.121, Medicaid agencies must provide Medicaid to aged, blind, and disabled people receiving or deemed to receive SSI.

4. 42 CFR 435.121, individuals in states using more restrictive requirements than SSI
   - URL: https://www.ecfr.gov/current/title-42/section-435.121
   - Backup readable source used during research: https://www.law.cornell.edu/cfr/text/42/435.121
   - Rule: 209(b) states must cover aged, blind, and disabled SSI beneficiaries who meet the state's more restrictive requirements.
   - Rule: more restrictive requirements may include financial and nonfinancial criteria.
   - Rule: spenddown and required deductions apply under subsection (f).

## Existing PolicyEngine References

- `policyengine_us/variables/gov/hhs/medicaid/eligibility/categories/is_ssi_recipient_for_medicaid.py`
- `policyengine_us/variables/gov/hhs/medicaid/eligibility/categories/medicaid_ssi_recipient_state_classification.py`
- `policyengine_us/parameters/gov/hhs/medicaid/eligibility/categories/ssi_recipient/classification/section_209b.yaml`
- `policyengine_us/parameters/gov/hhs/medicaid/eligibility/categories/senior_or_disabled/`
- `policyengine_us/variables/gov/hhs/medicaid/eligibility/categories/is_optional_senior_or_disabled_income_eligible.py`
- `policyengine_us/variables/gov/hhs/medicaid/eligibility/categories/is_optional_senior_or_disabled_asset_eligible.py`
- `policyengine_us/variables/gov/hhs/medicaid/eligibility/categories/medically_needy/is_medically_needy_for_medicaid.py`

## Modeling Approach

- Keep automatic SSI-recipient coverage for 1634 and SSI-criteria states.
- Add a separate 209(b) SSI-recipient variable for people receiving SSI in 209(b) states.
- Reuse existing state ABD Medicaid countable-income and countable-resource tests for the more restrictive financial rules.
- Reuse existing medically needy/spenddown pathway rather than making `is_ssi_recipient_for_medicaid` circular with `is_medically_needy_for_medicaid`.
- Add a federal parameter for CT/NH/MO excluding nonblind disabled children under age 18 from the direct 209(b) SSI-recipient pathway.
- Not modeled in this change: state-specific January 1, 1972 methodologies beyond existing PE state ABD parameters; 1619(a)/(b) deemed SSI details; mandatory state supplement deductions where PE lacks a general state-supplement variable.
