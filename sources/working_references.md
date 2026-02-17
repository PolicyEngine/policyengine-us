# Collected Documentation

## SNAP ABAWD (Able-Bodied Adults Without Dependents) Work Requirement Changes - Federal Implementation
**Collected**: 2026-02-16
**Implementation Task**: Document HR1 (Public Law 119-21) changes to SNAP ABAWD exemptions, age thresholds, and work requirements; verify effective dates against existing PolicyEngine codebase

---

## Official Program Name

**Federal Program**: Supplemental Nutrition Assistance Program (SNAP) - Able-Bodied Adults Without Dependents (ABAWD) Work Requirements
**Legal Name**: ABAWD Time Limit (Section 6(o) of the Food and Nutrition Act of 2008)
**Amended By**: One Big Beautiful Bill Act of 2025 (HR1, Public Law 119-21), Section 10102
**Signed Into Law**: July 4, 2025

---

## Source Documents

### 1. Public Law 119-21 (The Enacted Law)
- **Title**: One Big Beautiful Bill Act of 2025
- **Citation**: Public Law 119-21, Section 10102, 139 Stat. 80-82
- **URL**: https://www.congress.gov/119/plaws/publ21/PLAW-119publ21.pdf#page=81
- **Signed**: July 4, 2025
- **Status**: ENACTED LAW

### 2. USDA FNS Information Memorandum (September 4, 2025)
- **Title**: Supplemental Nutrition Assistance Program Provisions of the One Big Beautiful Bill Act of 2025 -- Information Memorandum
- **Citation**: FNS Information Memorandum, dated September 4, 2025
- **URL**: https://fns-prod.azureedge.us/sites/default/files/resource-files/OBBB-SNAP-Provisions-Implementation-Memo.pdf
- **Key Quote**: "These changes were effective upon enactment. State agencies must apply updated exceptions to new and ongoing participants after they are screened, in accordance with 7 CFR 273.24(k)."

### 3. USDA FNS ABAWD Exceptions Implementation Memorandum (October 3, 2025)
- **Title**: SNAP Provisions of the One Big Beautiful Bill Act of 2025 - ABAWD Exceptions - Implementation Memorandum
- **Citation**: FNS Implementation Memorandum, dated October 3, 2025
- **URL**: https://fns-prod.azureedge.us/sites/default/files/resource-files/OBBB-ABAWD-ImplementationMemo-Exception-Changes.pdf
- **FNS Landing Page**: https://www.fns.usda.gov/snap/obbb-ABAWD-exemptions-implementation-memo
- **Key Quote**: "These changes were effective upon enactment, July 4, 2025. State agencies must immediately screen for and apply the modified exception criteria to all initial applications and recertification applications."

### 4. USDA FNS ABAWD Waivers Implementation Memorandum (October 3, 2025)
- **Title**: SNAP Provisions of the One Big Beautiful Bill Act of 2025 -- ABAWD Waivers - Implementation Memorandum
- **Citation**: FNS Implementation Memorandum, dated October 3, 2025
- **URL**: https://fns-prod.azureedge.us/sites/default/files/resource-files/OBBB-Implementation%20Memo-ABAWD-Waivers.pdf
- **FNS Landing Page**: https://www.fns.usda.gov/snap/obbb-abawd-waivers-implementation

### 5. California ACL 25-93 (December 31, 2025) -- State Implementation Example
- **Title**: CalFresh Implementation of House of Representatives 1: Changes to Time Limit for Able-Bodied Adults Without Dependents Policy
- **Citation**: California All County Letter No. 25-93
- **URL**: Local PDF provided by user
- **Note**: California implementation date is June 1, 2026 (state-specific delay for CalSAWS automation). This is NOT the federal effective date.

### 6. Statutory Citations
- **7 U.S.C. 2015(o)**: Food and Nutrition Act of 2008, Section 6(o) -- ABAWD time limit
- **7 U.S.C. 2015(o)(2)**: Time limit provision (3 months in 36-month period)
- **7 U.S.C. 2015(o)(3)**: Exceptions from the time limit (as amended by HR1)
- **7 U.S.C. 2015(o)(4)**: Waiver authority (as amended by HR1)
- **7 U.S.C. 2015(o)(7)**: NEW -- Exemption for noncontiguous states (Alaska and Hawaii)
- **7 CFR 273.24**: ABAWD time limit regulations
- **7 CFR 273.7(b)(1)**: Work registration exemptions
- **25 U.S.C. 1603(13)**: Definition of "Indian" (IHCIA)
- **25 U.S.C. 1603(28)**: Definition of "Urban Indian" (IHCIA)
- **25 U.S.C. 1679(a)**: Definition of "California Indian" (IHCIA)

---

## CRITICAL FINDING: Federal Effective Date

### The federal effective date is July 4, 2025, NOT 2027-01-01.

**Evidence (three independent confirmations):**

1. **The law itself** (Public Law 119-21, Section 10102): Contains NO separate effective date provision. Under standard legislative rules, provisions without explicit delayed effective dates take effect upon enactment. The law was signed July 4, 2025.

2. **FNS Information Memorandum (September 4, 2025)**: States on page 3: "These changes were effective upon enactment."

3. **FNS ABAWD Exceptions Implementation Memorandum (October 3, 2025)**: States on page 5: "These changes were effective upon enactment, July 4, 2025. State agencies must immediately screen for and apply the modified exception criteria to all initial applications and recertification applications."

**The existing PolicyEngine codebase uses 2027-01-01 as the effective date for all HR1 ABAWD changes. This is INCORRECT and needs to be updated to 2025-07-04.**

### Quality Control Exclusionary Period

The November 1, 2025 date referenced in the FNS memo is the QC exclusionary period end date -- meaning states that misapplied rules between July 4, 2025 and November 1, 2025 would not be penalized. This does NOT change the legal effective date.

---

## Summary of All HR1 ABAWD Changes

### 1. ABAWD Age Range Expansion

**Prior Law (FRA 2023 final phase)**:
- ABAWD time limit applied to ages 18-54
- FRA 2023 phase-in: Age 50 (Sep 1, 2023) -> Age 52 (Oct 1, 2023) -> Age 54 (Oct 1, 2024)
- FRA 2023 exemptions were temporary, set to sunset October 1, 2030

**HR1 (Public Law 119-21)**:
- ABAWD time limit now applies to ages 18-64
- Exemption for age: under 18 OR over 65
- Federal effective date: **July 4, 2025**

**Statutory Text** (7 U.S.C. 2015(o)(3)(A), as amended):
> "(A) under 18, or over 65, years of age;"

**Source**: Public Law 119-21, Section 10102(a), 139 Stat. 80

**Existing PolicyEngine parameter**: `gov.usda.snap.work_requirements.abawd.age_threshold.exempted`
- Currently has upper threshold change from 55 to 65 effective 2027-01-01
- **NEEDS UPDATE**: Change effective date from 2027-01-01 to 2025-07-04

**Note on FRA 2023 phase-in**: The existing codebase has threshold 55 from 2019-01-01 (which represents the pre-FRA age 50-54 range simplified). The FRA 2023 actually phased in to age 50 (Sept 2023), 52 (Oct 2023), 54 (Oct 2024). The HR1 supersedes all of this by raising to 64 effective July 4, 2025.

---

### 2. Modified Dependent Child Exemption

**Prior Law**:
- Exempt if parent of child under 18, or residing in household with member under 18
- Citation: 7 CFR 273.24(c)(3) and 7 CFR 273.24(c)(4)

**HR1**:
- Exempt only if "a parent or other member of a household with responsibility for a dependent child under 14 years of age"
- No longer exempt solely because a household member is under 18
- "Responsibility for care" broadly defined -- includes parents, stepparents, siblings, grandparents, other relatives, or unrelated persons providing regular necessary care or supervision
- Child does not need to be in the SNAP household; physical or legal custody not required
- A single child under 14 can exempt more than one adult if each independently has responsibility for care
- Federal effective date: **July 4, 2025**

**Statutory Text** (7 U.S.C. 2015(o)(3)(C), as amended):
> "(C) a parent or other member of a household with responsibility for a dependent child under 14 years of age;"

**Source**: Public Law 119-21, Section 10102(a), 139 Stat. 80

**Existing PolicyEngine parameter**: `gov.usda.snap.work_requirements.abawd.age_threshold.dependent`
- Currently has value change from 18 to 14 effective 2027-01-01
- **NEEDS UPDATE**: Change effective date from 2027-01-01 to 2025-07-04

---

### 3. Eliminated Exemptions (FRA 2023 Temporary Exemptions Removed)

**Prior Law (FRA 2023)**:
The FRA of 2023 added temporary exemptions (set to sunset October 1, 2030) for:
1. **Veterans**
2. **Individuals experiencing homelessness**
3. **Former foster youth** under age 25 who were in foster care on their 18th birthday (or higher age if state offered extended foster care)

**HR1**:
- ALL three FRA 2023 temporary exemptions are **removed**
- HR1 completely replaces paragraph (3) of 7 U.S.C. 2015(o), so the FRA exemptions no longer exist
- Federal effective date: **July 4, 2025**

**Source**: Public Law 119-21, Section 10102(a) strikes paragraph (3) entirely and inserts new text that does not include these exemptions.

**FNS Memo Confirmation** (October 3, 2025):
> "The OBBB removes the temporary exceptions for the following populations, which were added by the Fiscal Responsibility Act of 2023 (FRA): 1. Homeless individuals; 2. Veterans; and 3. Individuals aged 24 or younger and in foster care on their 18th birthday (or a higher age if the State offers extended foster care)."

**Existing PolicyEngine parameter**: `gov.usda.snap.work_requirements.abawd.in_effect`
- Currently has value change from false to true effective 2027-01-01
- This parameter controls whether homeless/veteran exemptions are removed
- **NEEDS UPDATE**: Change effective date from 2027-01-01 to 2025-07-04

**Implementation Note**: The existing variable `meets_snap_abawd_work_requirements` already handles this via the `in_effect` flag toggling the `is_homeless` and `is_veteran` conditions. However, it does NOT currently handle the foster youth exemption (which was never implemented in the first place).

---

### 4. New Exemption: Native American / Indian / Urban Indian / California Indian

**This is entirely NEW under HR1. No prior law equivalent.**

**HR1 Text** (7 U.S.C. 2015(o)(3)(F) and (G), as amended):
> "(F) an Indian or an Urban Indian (as such terms are defined in paragraphs (13) and (28) of section 4 of the Indian Health Care Improvement Act); or"
> "(G) a California Indian described in section 809(a) of the Indian Health Care Improvement Act."

**Federal effective date**: **July 4, 2025**

**IHCIA Definitions**:

**"Indian" (25 U.S.C. 1603(13))**: A member of an Indian Tribe. "Indian Tribe" means any Indian tribe, band, nation, or other organized group or community, including Alaska Native villages, groups, or regional or village corporations established under the Alaska Native Claims Settlement Act, that is recognized as eligible for federal programs and services provided to Indians because of their status as Indians.

**"Urban Indian" (25 U.S.C. 1603(28))**: An individual who resides in an urban center AND meets at least one of:
1. Is a member of a tribe, band, or other organized group of Indians (including groups terminated since 1940 and those recognized now or in the future by their State), or is a first- or second-degree descendant of such a member;
2. Is an Eskimo, Aleut, or other Alaska Native;
3. Is determined to be an Indian under regulations of the Secretary of Interior; or
4. Is determined to be an Indian under regulations of the Secretary of HHS.

**"California Indian" (25 U.S.C. 1679(a))**: An individual who meets at least one of:
1. Is a member of a federally recognized Indian Tribe;
2. Is a descendant of an Indian who resided in California on June 1, 1852, provided they are a member of the Indian community served by a local Indian Health Service program and are regarded as an Indian by their community;
3. Is an Indian who holds trust interests in public domain, national forest, or reservation allotments in California; or
4. Is an Indian of California listed on plans for distribution of assets of rancherias and reservations under the Act of August 18, 1958, including their descendants.

**Verification**: Self-attestation is sufficient unless questionable. Per FNS guidance and California ACL 25-93, counties/state agencies must not seek additional verification unless the information provided conflicts with previous statements or case records.

**Existing PolicyEngine Implementation**: **NOT IMPLEMENTED**. The codebase has no variable for Native American/Indian/tribal member status at the person level. The closest is `is_on_tribal_land` (household-level geographic variable), which is NOT the same thing. A new person-level input variable would be needed.

---

### 5. Complete List of ABAWD Exemptions Under HR1

After HR1, the exhaustive list of ABAWD time limit exemptions under 7 U.S.C. 2015(o)(3) is:

| Letter | Exemption | Status |
|--------|-----------|--------|
| (A) | Under 18 or over 65 years of age | MODIFIED (was 54, now 64 -- exempt if over 65) |
| (B) | Medically certified as physically or mentally unfit for employment | UNCHANGED |
| (C) | Parent or household member with responsibility for dependent child under 14 | MODIFIED (was under 18, now under 14) |
| (D) | Otherwise exempt under subsection (d)(2) (work registration exemptions) | UNCHANGED |
| (E) | Pregnant woman | UNCHANGED |
| (F) | An Indian or Urban Indian (IHCIA definitions) | **NEW** |
| (G) | A California Indian (IHCIA section 809(a)) | **NEW** |

**Removed by HR1** (previously existed under FRA 2023):
- Veterans
- Homeless individuals
- Former foster youth under 25 who aged out of foster care

---

### 6. Work Registration vs. ABAWD for Ages 60-64

**Critical Distinction**: HR1 does NOT change general work registration requirements.

- **Work Registration Exemption**: Individuals aged 60+ remain exempt from work registration under 7 CFR 273.7(b)(1). This is UNCHANGED by HR1.
- **ABAWD Time Limit**: Individuals aged 60-64 are NOW subject to the ABAWD time limit under HR1, unless they qualify for another exemption.

**FNS Memo (October 3, 2025) states**:
> "The OBBB does not change the upper age limit for the general work requirements at Section 6(d)(3) of the Act. Individuals aged 60 or older remain exempt from the general work requirements, including mandatory participation in SNAP Employment and Training (E&T)."

**This means**: Ages 60-64 are exempt from work registration (general work requirements) due to age, but they are NOT exempt from the ABAWD time limit solely due to age. They must be screened for OTHER work registration exemptions or ABAWD exemptions.

**The existing PolicyEngine code handles this via the `meets_snap_general_work_requirements` variable**, which already exempts ages 60+ from general work requirements. The ABAWD variable checks for general work requirement exemption as one of its conditions. However, the nuance is that being exempt from work registration "due to age" alone (ages 60-64) should NOT automatically exempt from ABAWD. The current code structure may need review to ensure this is correctly handled -- currently `meets_snap_general_work_requirements` returns True for age 60+, which then feeds into `meets_snap_abawd_work_requirements` as an exemption. This would incorrectly exempt ages 60-64 from ABAWD.

**IMPORTANT IMPLEMENTATION ISSUE**: The current code at line 30 of `meets_snap_abawd_work_requirements.py` uses `meets_snap_general_work_requirements` as an ABAWD exemption condition. For ages 60-64, this creates a conflict: they ARE exempt from general work registration (due to age), but they should NOT be ABAWD-exempt based solely on that age-based general work registration exemption. Per the FNS memo, state agencies must screen 60-64 year-olds for work registration exemptions OTHER THAN AGE before granting ABAWD exemption.

---

### 7. Alaska and Hawaii Provisions

HR1 creates two special provisions for "noncontiguous States" (defined as states not among the contiguous 48 states or DC, excluding Guam and the Virgin Islands -- effectively meaning Alaska and Hawaii):

**a. Special ABAWD Waiver Criterion** (7 U.S.C. 2015(o)(4)(A)(ii)):
- Alaska and Hawaii may request ABAWD waivers if their area unemployment rate is at or above 1.5 times (150%) the national unemployment rate
- This is a permanent provision (no expiration)
- Other states can only get waivers if unemployment exceeds 10%

**b. Good Faith Exemption** (7 U.S.C. 2015(o)(7)):
- Secretary may exempt individuals in Alaska/Hawaii from ABAWD requirements if the state demonstrates a good faith effort to comply
- Exemptions expire no later than December 31, 2028
- Requires quarterly progress reports
- Can be terminated early if state fails to comply

**Federal effective date**: **July 4, 2025** (effective upon enactment)

**FNS Waivers Memo (October 3, 2025) states**:
> "The Secretary's authority to grant ABAWD good faith exemptions is effective immediately, and exemptions issued under this authority expire no later than December 31, 2028."

**Existing PolicyEngine parameter**: `gov.usda.snap.work_requirements.abawd.exempt_states`
- Currently has Alaska (AK) and Hawaii (HI) added effective 2027-01-01
- **NEEDS UPDATE**: Change effective date from 2027-01-01 to 2025-07-04
- **NOTE**: The Alaska/Hawaii exemption in the law is NOT automatic -- it requires states to apply and the Secretary to approve. However, for PolicyEngine modeling purposes, treating Alaska and Hawaii as exempt from ABAWD is a reasonable simplification since the good-faith exemption provision was specifically created to allow them transition time. The parameter description should note this simplification.

---

### 8. "Elderly" Definition Unchanged

HR1 does NOT change the definition of "elderly" under Section 3(j) of the Food and Nutrition Act. Individuals age 60 or older continue to be defined as "elderly" for SNAP purposes and continue to receive:
- Excess medical deduction
- Uncapped shelter deduction (no cap on excess shelter deduction)

This is true regardless of whether they are also considered an ABAWD under HR1.

---

## Warning: Non-Simulatable Rules (Architecture Limitation)

### Cannot be fully simulated (single-period architecture):
- **ABAWD Time Limit**: 3 countable months in a 36-month period [CANNOT ENFORCE -- requires tracking months of benefit receipt over time]
- **Work Requirement Compliance**: Must work 20+ hours/week averaged monthly [Can check point-in-time hours but cannot track month-to-month compliance]
- **Statewide Clock**: Fixed 36-month periods (e.g., Jan 2026 - Dec 2028 in California) [CANNOT TRACK -- requires history]
- **Additional 3-Month Eligibility Period**: One-time additional 3 consecutive months if regain compliance [CANNOT TRACK]
- **Discretionary Exemptions**: Limited pool allocated by FNS annually [CANNOT MODEL -- administrative discretion]

### CAN be simulated (current point-in-time):
- Whether a person meets the ABAWD definition (age, no dependents, able-bodied)
- Whether a person qualifies for an ABAWD exemption (age, disability, dependent child, pregnancy, Native American status, state exemption)
- Whether a person is currently working 20+ hours/week
- Whether a person is in an exempt state (Alaska/Hawaii)
- General work registration exemptions

---

## Existing PolicyEngine Codebase: Parameters Requiring Date Correction

All of the following parameters currently use **2027-01-01** as the effective date. The correct federal effective date is **2025-07-04**.

| Parameter File | Current Date | Correct Date | Change Description |
|---|---|---|---|
| `gov/usda/snap/work_requirements/abawd/age_threshold/exempted.yaml` | 2027-01-01 | 2025-07-04 | Upper age threshold: 55 -> 65 |
| `gov/usda/snap/work_requirements/abawd/age_threshold/dependent.yaml` | 2027-01-01 | 2025-07-04 | Dependent child age: 18 -> 14 |
| `gov/usda/snap/work_requirements/abawd/in_effect.yaml` | 2027-01-01 | 2025-07-04 | Removal of homeless/veteran exemptions |
| `gov/usda/snap/work_requirements/abawd/exempt_states.yaml` | 2027-01-01 | 2025-07-04 | Alaska and Hawaii exemption |

### Additional Implementation Gaps

1. **Native American/Indian exemption (NEW)**: Not implemented. Needs new person-level input variable (e.g., `is_abawd_exempt_native_american`) and integration into `meets_snap_abawd_work_requirements` formula.

2. **Foster youth exemption removal**: The FRA 2023 foster youth exemption was never implemented in the codebase, so its removal by HR1 has no code impact. However, for completeness, this should be noted.

3. **Ages 60-64 work registration vs. ABAWD conflict**: The current code structure may incorrectly exempt ages 60-64 from ABAWD because they are exempt from general work registration due to age. Per HR1 and FNS guidance, age-based work registration exemption alone should NOT exempt from ABAWD. This needs architectural review.

4. **FRA 2023 phase-in dates**: The existing age bracket parameter jumps from 55 (2019) to 65 (currently 2027, should be 2025-07-04). The intermediate FRA 2023 phase-in (50 on Sept 2023, 52 on Oct 2023, 54 on Oct 2024) is not captured. While HR1 supersedes this, for historical accuracy, consider adding these intermediate values.

5. **`gov/contrib/reconciliation/snap_abawd_work_requirement/`**: These files appear to be pre-enactment "contrib" (proposed reform) parameters. Now that HR1 is enacted law, these should either be removed or marked as superseded by the actual `gov/usda/snap/work_requirements/abawd/` parameters.

---

## Existing PolicyEngine Test Cases Requiring Updates

The following test cases in `tests/policy/baseline/gov/usda/snap/eligibility/work_requirements/meets_snap_abawd_work_requirements.yaml` use period 2026 or 2027 and would be affected by the date correction:

- **Case 9** (period 2026): Tests age 55 as exempt. With corrected dates, age 55 is NOT exempt starting July 2025. This test would FAIL if dates are corrected.
- **Case 10** (period 2027): Tests age 55 as not exempt. Would still pass.
- **Case 11** (period 2026-01): Tests parent with child age 15 as exempt. With corrected dates (child under 14 only after July 2025), this parent of a 15-year-old would NOT be exempt. This test would FAIL.
- **Case 12** (period 2027): Tests parent with child age 15 as not exempt. Would still pass.
- **Case 14** (period 2027): Tests veteran with child 15 as not exempt. Would still pass.
- **Case 15** (period 2027): Tests Hawaii exemption. Would still pass.
- **Case 16** (period 2026): Tests Hawaii in baseline as NOT exempt. With corrected dates, Hawaii IS exempt starting July 2025, so this test would FAIL.

---

## References for Metadata

### For parameters:
```yaml
reference:
  - title: "Public Law 119-21, Section 10102(a) - Modifications to SNAP Work Requirements for Able-Bodied Adults"
    href: "https://www.congress.gov/119/plaws/publ21/PLAW-119publ21.pdf#page=81"
  - title: "7 U.S.C. 2015(o)(3) - ABAWD Time Limit Exceptions"
    href: "https://www.law.cornell.edu/uscode/text/7/2015#o_3"
  - title: "USDA FNS SNAP ABAWD Exceptions Implementation Memorandum (October 3, 2025)"
    href: "https://fns-prod.azureedge.us/sites/default/files/resource-files/OBBB-ABAWD-ImplementationMemo-Exception-Changes.pdf"
```

### For variables:
```python
reference = "https://www.law.cornell.edu/uscode/text/7/2015#o_3"
```

### For Alaska/Hawaii provisions:
```yaml
reference:
  - title: "Public Law 119-21, Section 10102(c) - Waiver for Noncontiguous States"
    href: "https://www.congress.gov/119/plaws/publ21/PLAW-119publ21.pdf#page=81"
  - title: "USDA FNS ABAWD Waivers Implementation Memorandum (October 3, 2025)"
    href: "https://fns-prod.azureedge.us/sites/default/files/resource-files/OBBB-Implementation%20Memo-ABAWD-Waivers.pdf"
```

### For Native American/Indian exemption:
```yaml
reference:
  - title: "Public Law 119-21, Section 10102(a) - 7 U.S.C. 2015(o)(3)(F)-(G)"
    href: "https://www.congress.gov/119/plaws/publ21/PLAW-119publ21.pdf#page=81"
  - title: "25 U.S.C. 1603 - Definitions (Indian Health Care Improvement Act)"
    href: "https://www.law.cornell.edu/uscode/text/25/1603"
  - title: "25 U.S.C. 1679 - California Indians (IHCIA)"
    href: "https://www.law.cornell.edu/uscode/text/25/1679"
```

---

## Timeline of ABAWD Age Threshold Changes

| Date | Upper Age Threshold | Source |
|------|---------------------|--------|
| Pre-Sept 2023 | 49 (ages 18-49 subject to ABAWD) | Original law |
| September 1, 2023 | 50 (ages 18-50) | FRA 2023, phase 1 |
| October 1, 2023 | 52 (ages 18-52) | FRA 2023, phase 2 |
| October 1, 2024 | 54 (ages 18-54) | FRA 2023, phase 3 (final) |
| **July 4, 2025** | **64 (ages 18-64)** | **HR1 (Public Law 119-21), Section 10102** |

Note: The FRA 2023 also added temporary exemptions for veterans, homeless, and foster youth, set to sunset October 1, 2030. HR1 removes these exemptions immediately (July 4, 2025).

---

## PDFs Successfully Extracted

1. **California ACL 25-93** (15 pages) -- Full text extracted with pdftotext; screenshots at 300 DPI in `/tmp/acl-25-93-*.png`
2. **USDA FNS ABAWD Exceptions Implementation Memo** (6 pages) -- Full text extracted: `/tmp/fns-abawd-exceptions.txt`
3. **USDA FNS Information Memorandum** (4 pages) -- Full text extracted: `/tmp/fns-snap-provisions.txt`
4. **USDA FNS ABAWD Waivers Implementation Memo** (4 pages) -- Full text extracted: `/tmp/fns-abawd-waivers.txt`
5. **Public Law 119-21** (full enrolled bill) -- Downloaded and extracted: `/tmp/plaw-119-21.txt`
