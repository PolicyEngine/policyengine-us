# Indiana CCDF (Child Care and Development Fund) Voucher Program — Working References

**Official program name:** Child Care and Development Fund (CCDF) Voucher Program
**Administering agency:** Indiana Family and Social Services Administration (FSSA),
Office of Early Childhood and Out-of-School Learning (OECOSL)
**PolicyEngine directory:** `gov/states/in/fssa/ccdf` (the `in` state dir uses Python reserved-keyword
bracket indexing in formulas: `parameters(period).gov.states["in"].fssa.ccdf...`; dotted `adds` path
strings still resolve, e.g. `"gov.states.in.fssa.ccdf.income.sources"`)
**Federal program parent:** HHS CCDF (`gov/hhs/ccdf`) — reuse federal helpers where applicable.

> NOTE: This is the CCDF voucher (subsidy) program — NOT the SSP/TANF/HIP programs that already
> exist under `gov/states/in/fssa/`. New work goes under a new `ccdf/` subtree.

---

## 1. Primary Sources (all verified live; downloaded to /tmp)

| Document | URL | Pages | Notes |
|---|---|---|---|
| CCDF Voucher Program **Policy Manual** (Eligibility), Revised Oct 14 2024 / Feb 2 2025 | https://www.in.gov/fssa/carefinder/files/CCDF-Policy-Manual.pdf | 61 | Eligibility, service need, countable income, copay, reimbursement structure |
| **Sliding Fee Schedule w/ Copays 2026** (income eligibility + copay factors + dollar copay table) | https://www.in.gov/fssa/carefinder/files/CCDFSlidingFeeSchedule_withCopays_2026.pdf | 10 | Effective 4/5/2026. THE key benefit/copay table |
| Income limits to **get on** CCDF (initial, ~135% FPL) | https://www.in.gov/fssa/carefinder/files/Income-Get-on-CCDF.pdf | 1 | Effective 4/5/2026. Monthly gross by family size |
| Income limits to **stay on** CCDF (continuing, 85% SMI) | https://www.in.gov/fssa/carefinder/files/Income-Stay-On-CCDF.pdf | 1 | Effective 4/5/2026. Matches Max-SMI column of fee schedule |
| CCDF **Provider Manual**, Revised April 2025 | https://www.in.gov/fssa/carefinder/files/CCDF-Provider-Manual.pdf | 25 | Provider types, eligibility standards, reimbursement rate definitions |
| Sample **county reimbursement rate sheet** (Marion County, FY2023) | https://www.in.gov/fssa/carefinder/files/MarionReimbRateCCDF.pdf | 6 | Per-county; example of the 8,932-rate structure |
| Reimbursement rate portal (per-county selector) | https://www.in.gov/fssa/carefinder/provider-reimbursements/ | web | Choose 1 of 92 counties; no statewide/cluster file |
| CCDF **State Plan** FY2025-2027 (ACF-118) | https://www.in.gov/fssa/files/ACF-118-CCDF-FY2025-2027-IN.pdf | ~7.7MB | Federal plan; policy crosswalk |
| Child Care Assistance landing page (link hub) | https://www.in.gov/fssa/carefinder/child-care-assistance/ | web | Source of all PDF hrefs above |
| OECOSL bulletin: new cost-based rates + income eligibility 127%→150% FPL (Jul 2023) | https://content.govdelivery.com/accounts/INOECOSL/bulletins/366774c | web | Historical timeline anchor |

---

## 2. Eligibility Tests Identified (≈ 6)

1. **Residency** — must reside in Indiana (`defined_for = StateCode.IN`). Policy Manual §1.5
   (PDF p.11).
2. **Child age** — under 13 at application; a child turning 13 may finish the subsidy period; a child
   over 13 with documented special needs or court-ordered supervision and under 18 may participate
   until the Sunday following their 19th birthday. Policy Manual §1.6 (PDF p.12).
3. **Child citizenship/immigration** — eligible child must be a U.S. citizen or qualified legal alien.
   **Only the child's status matters** (not the parents'). Policy Manual §1.6 (PDF p.12).
   → Candidate reuse: `is_ccdf_immigration_eligible_child` (federal helper).
4. **Service need (activity)** — both Applicant and Co-Applicant must have a valid service need:
   employment/self-employment/on-the-job training (job search counts at **initial application only**),
   education/training, incapacitation, or CPS referral. **No minimum number of working hours.**
   Policy Manual §1.7 (PDF p.15).
5. **Income** — two-tier test:
   - **Initial (get on):** ≤ **135% FPL** (lowered from 150% FPL by 2025 state budget bill; the
     published "Get on" table rounds to ~138% FPL bracket boundaries). Income-Get-on PDF.
   - **Continuing (stay on):** ≤ **85% SMI** (Indiana Median Income). Income-Stay-on PDF, matches the
     fee schedule's "Max SMI" column exactly.
   - Gross monthly household income, before taxes, after exclusions.
6. **Assets** — household ineligible if assets > **$1,000,000** (cash + retirement + investments + real
   property). Policy Manual "Assets Greater Than One Million Dollars" (PDF p.31). NOTE: This is Indiana's
   own threshold, NOT the federal CCDF asset limit — do **not** reuse `is_ccdf_asset_eligible` here.

Use `is_tanf_enrolled` (bare input), not computed TANF eligibility, to avoid the CCDF↔TANF circular
dependency via `childcare_expenses` (see RI CCAP refactor lesson).

---

## 3. Countable Income (Policy Manual §1.8, PDF p.25–31)

**Counted (gross monthly):**
- Earned income: wages/salary, tips, self-employment (net of business expenses; loss = $0), gig
  (Uber/Lyft/DoorDash/Instacart)
- Rental income (net of mortgage/escrow; if no mortgage statement, counted in full)
- Social Security all types: **SSI, SSDI, retirement** (lump-sum SS not counted)
- TANF cash assistance
- Unemployment benefits
- Worker's compensation
- Child support / spousal maintenance (received)

**Exclusions / exemptions (≈ 5):**
1. Earned income of a household member **under 18** (except emancipated minors and minor parents)
2. Income of a valid **licensed foster family**
3. Income of a documented **Child Protective Services** family
4. Lump-sum Social Security payments
5. Earned-income adjustments deducted from gross wages: advance pay timing, health/dental/vision
   benefits w/ opposing deduction, employment reimbursements (mileage/per diem/meals/supplies),
   housing & food allowance in gross wages, employer retirement contributions (401k/deferred comp/pension)

---

## 4. Benefit Calculation (FORMULA — tiered, two-part)

**Subsidy = (CCDF Reimbursement Rate for the child) − (applicable weekly copayment).**
Plus the family pays any **overage** (provider charge above the reimbursement rate) directly.
Policy Manual §2.6 (PDF p.39).

### 4a. Reimbursement rate (the per-child cap)
- Determined by **geography (county), child age group, provider type, and Paths to QUALITY level.**
- **6 age groups:** Infant (0–11 mo), Toddler (12–35 mo), 3-4-5 Years (36 mo–5 yr), Kindergarten
  (half-day K, or age 6), School-Age Before/After, School-Age All Other. Policy Manual §2.4 (PDF p.37–38).
- **Provider types (rate purposes):** Legally License Exempt Home, Legally License Exempt
  Facilities (incl. Unlicensed Registered Child Care Ministry), Licensed Home, Licensed Center,
  Voluntary Certification Program (VCP) Ministry; plus PTQ Levels 1–4 modifiers; plus OMW types.
- **Time units:** Full-Time (weekly), Daily, Hourly. (Marion FY2023 example: Licensed Center Infant
  Full-Time = $416/wk; Licensed Home Infant Full-Time = $156/wk.)
- **Special-needs add-on:** subsidy may exceed the reimbursement rate by **10%** for children with
  documented special needs. Policy Manual §2.4 (PDF p.37).
- **⚠️ SCALE WARNING:** Indiana publishes **8,932 distinct rates** = 92 counties × 16 provider types
  × 6 age groups × {weekly/daily/hourly}. There is **no statewide or county-cluster file** — each
  county has its own PDF (e.g. `MarionReimbRateCCDF.pdf`). Full per-county modeling is impractical;
  a design decision is needed (statewide representative rate, a small county-cluster, or model the
  copay/income side and treat the rate as the provider charge). Flag for the user at design time.
- **Rate cut history:** effective **10/5/2025** rates were cut — infant/toddler −10%, preschool −15%,
  school-age −35% (per Child Care Answers / FSSA budget reporting).

### 4b. Copayment (the family's share — well-defined, modelable)
- **Weekly fee**, applies to all families with income **> 100% FPL** (≤100% FPL → $0 copay).
  Policy Manual §2.6 (PDF p.39); Sliding Fee Schedule 2026.
- Copay = **monthly countable income × FEE FACTOR**, where the factor depends on:
  - **Years on program tier:** Year 1-3, Year 4, Year 5, Year 6, Year 7, Year 8, Year 9, Year 10+
  - **Income bracket** (11 columns as % FPL): `≤100%`, `101-109%`, `110-118%`, `119-135%`, `136-140%`,
    `141-150%`, `151-160%`, `161-170%`, `171-200%`, `201-225%`, `226%-Max SMI`
  - Factors range 0.0000 (≤100% FPL) up to 0.0605 (Year 10+, top bracket).
  - Example (Year 1-3): factors 0.0000 / 0.0116 / 0.0140 / 0.0163 / 0.0163 / 0.0186 / 0.0209 / 0.0233
    / 0.0302 / 0.0372 / 0.0442 across the 11 brackets.
- The income brackets are expressed as **monthly gross income dollar ranges by family size** on the
  schedule (sizes 1–17). The schedule ALSO provides a precomputed **dollar weekly copay** lookup table
  (fee schedule pages 9–10) per family size × bracket × year-tier — either approach reproduces the copay.
- **On My Way Pre-K Regular** participants: **no copayment** for the entire subsidy period.
- Copay may **not be waived**; paid directly to provider regardless of attendance.
- "Years on program" → PolicyEngine has **no per-household program-tenure state**; model the
  **Year 1-3 tier** for new enrollees and document "we don't track years-on-program at the moment"
  in the variable docstring (same pattern as FL/cohort grandfathering lesson).

---

## 5. Income Eligibility Timeline (for backdating)

| Effective | Initial (get-on) | Continuing (stay-on) | Source |
|---|---|---|---|
| ~2022 / earlier | 127% FPL | 85% SMI | OECOSL bulletin |
| Aug 1, 2023 | 150% FPL | 85% SMI | OECOSL bulletin (Jul 2023), Policy Manual §1.1 (PDF p.5) |
| 2025 (state budget) → 4/5/2026 schedule | **135% FPL** | 85% SMI | Income-Get-on PDF (eff 4/5/2026); Child Care Answers |

> The Policy Manual body (eff 10/14/2024) still states "150% or less of FPL" (§1.1, PDF p.5);
> the current 135% value lives on the **Income-Get-on** PDF (eff 4/5/2026). Cite the Income-Get-on
> PDF for the current 135% value and the manual for the 150% era. Treat as a body-vs-operational
> split (see LA OSS lesson).

---

## 6. Provider Eligibility & Citizenship (Provider Manual, Apr 2025)

- **Eligible providers:** Licensed Child Care Center (IC 12-7-2-28.4), Licensed Child Care Home,
  Legally License Exempt providers / Nanny Care.
- **Must demonstrate Provider Eligibility Standards (PES):** Unlicensed Registered Child Care Ministry
  (church-extension, 501(c)(3), registered with OECOSL + Fire Marshal), Legally License Exempt providers
  (exempt per IC 12-17.2-2-8).
- **Nanny Care reimbursement:** per household at an hourly rate = current federal minimum wage, ≤ 40
  hrs/wk; one rate for all children; `hourly = minimum wage / number of children`. Policy Manual §2.5
  (PDF p.38). The standard reimbursement-rate table does NOT apply to nanny care.

---

## 7. Statutory / Regulatory Authority

- **470 IAC 3-18** — "Child Care Development Fund Voucher Program; Provider Eligibility" (the operative
  CCDF voucher rule). **Could not fetch text** (see Failed Fetches).
- **470 IAC 3-4.7** — "Child Care Centers; Licensing" (licensing of centers, NOT the voucher program's
  income/copay rules — the team-lead's note that 3-4.7 governs the voucher program appears to be a
  misattribution; the voucher program is 470 IAC 3-18 + the FSSA Policy Manual).
- **IC 12-17.2** (child care licensure) and **IC 12-17.2-2-8** (license-exempt categories).
- Federal: 45 CFR Part 98 (CCDF), CCDBG Act of 2014.
- FSSA Laws/Rules hub: https://www.in.gov/fssa/carefinder/laws-rules-and-related-policies/

---

## 8. Reuse from Federal CCDF Infrastructure

- `is_ccdf_immigration_eligible_child` — child citizenship/qualified-alien check (matches §1.6). REUSE.
- `child_care_subsidy_programs.yaml` (`gov/hhs/ccdf/`) — add `in_child_care_subsidies` to the `adds`
  list so the benefit flows into federal `child_care_subsidies`. REQUIRED registration.
- `is_ccdf_asset_eligible` / `gov.hhs.ccdf.asset_limit` — **DO NOT reuse**; Indiana uses its own
  $1,000,000 asset limit (federal limit is $1M too by coincidence in some years — VERIFY before
  reusing; safest to create `in_ccdf` asset param at $1,000,000 with the Policy Manual cite).
- `programs.yaml` — add a `state_implementations` entry under the `ccdf` federal program.

---

## 9. Reference Implementation Pattern

Closest structural match: **TX CCS** (`gov/states/tx/twc/ccs`) — per-region rate tables, copay rate,
age thresholds, work requirements, assets, income. Also RI/NH/AK/WV CCAP for the age-group-derived
variable pattern and MONTH-definition subsidy aggregator → YEAR state total → federal
`child_care_subsidies`.

---

## FAILED FETCHES (need manual download / browser access)

1. **470 IAC 3-18 full regulation text** — `licensingregulations.acf.hhs.gov` returns **HTTP 403** to
   curl/WebFetch; `regulations.justia.com` returns **HTTP 403**; `iac.iga.in.gov` (official IGA admin
   code) returned **HTTP 000** (JS-driven, no server response to curl). Likely contains the codified
   income-eligibility %, copay authorization, and provider-eligibility standards. Try Cornell LII
   (https://www.law.cornell.edu/regulations/indiana/title-470/article-3) in a browser, or download the
   IGA PDF manually. (Cornell LII often renders Indiana reg text client-side — may be a JS shell only.)
2. **470 IAC 3-4.7 text** (center licensing) — same portals 403; needed only to confirm it is licensing,
   not voucher rules. Low priority.
3. **CCDFSlidingFeeSchedule_w-Copays_2025_050125.pdf** (the older 2025 schedule) — returned **HTTP 404**
   (file moved/removed). The 2026 schedule downloaded fine; the 2025 prior-year schedule may be needed
   for backdating copay factors to the 150%-FPL era — request from FSSA or web archive.

---

## 470 IAC 3 (Indiana Administrative Code) — user-provided

**Source PDF (user-downloaded):** `/tmp/in-ccap-user-doc-1.pdf` — the full 191-page export of
"Title 470, Article 3. Child Welfare Services" from the IGA code reader. This RESOLVES "FAILED FETCH #1"
above: the 470 IAC 3-18 voucher-rule text that earlier curl/WebFetch attempts (acf.hhs.gov 403,
justia 403, iac.iga.in.gov 000) could not retrieve is now available in full.
**Live source URL (Rule 18):** https://iar.iga.in.gov/code/2025/470/3#470-3-18

> **Scope note:** 470 IAC 3-18 (Rule 18) = **PROVIDER certification** (fire safety, smoke/CO detection,
> exits, fire drills, criminal history, drug testing, central-registry check, immunization, inspections,
> denial/decertification). **NOT modeled by PolicyEngine** — PE does not model provider certification.
> Only 470 IAC 3-18-1 (definitions) and the legal framing are in scope.

### Legal authority chain
- **470 IAC 3-18 authority:** IC 12-13-5-3; **IC 12-17.2-3.5-15** (rulemaking for the CCDF voucher program).
  *Affected:* **IC 12-17.2-3.5** (the statute governing provider voucher reimbursement under CCDF).
- **CCDF federal basis** (per the definitions): 42 U.S.C. 9858 et seq., 45 CFR Part 98, 45 CFR Part 99.
- 470 IAC 3-18-1 filed Oct 14 2004 (eff.; 28 IR 950); readopted 2007, 2013, **2019** (most recent
  readoption: 20191211-IR-470190490RFA).

### Key definitions — 470 IAC 3-18-1 "General definitions" (PDF file p.175–177)
Citation: https://iar.iga.in.gov/code/2025/470/3#470-3-18 — PDF file p.175 (Sec. 1 begins; "Applicant",
"CCDF"), p.176 ("Provider", "Voucher payment/program/provider"), p.177 (closing definitions + history line).
- **(1) "Applicant"** = the individual who will receive payment from the CCDF program (or the individual
  authorized to sign for a corporation/partnership/sole proprietor). *(Note: provider-side applicant, not
  the family — this rule is provider eligibility.)*
- **(4) "CCDF"** = the Child Care and Development Fund program administered under 45 CFR 98.
- **(6) "Child"** = any individual under eighteen (18) years of age. *(Rule-18-local definition; the FSSA
  Policy Manual's operative CCDF age test is under 13 — see §2 above. Do not use this 18 figure for the
  voucher age test.)*
- **(10) "Decertification"** = a CCDF program provider who is no longer eligible to participate.
- **(11) "Division"** = the division of family and children.
- **(19) "Legally licensed exempt"** = a child care program that can operate legally without obtaining a
  license or registration under IC 12-17.2. *(Matches the "Legally License Exempt" provider type in §4a/§6.)*
- **(21) "Provider"** = an individual who provides child care services and is directly paid for the
  provision of child care under the federal CCDF voucher program (45 CFR 98 and 45 CFR 99), regardless of
  whether the facility is licensed or registered.
- **(24) "Temporary eligibility"** = provider eligibility period not to exceed forty-five (45) days.
- **(29) "Voucher agent"** = the state/agency/person/entity that contracts with the division to operate
  any function of the CCDF program.
- **(30) "Voucher payment"** / **(31) "Voucher program"** = payment / the federal CCDF program
  administered by the state under 42 U.S.C. 9858 et seq., 45 CFR 98, 45 CFR 99.
- **(32) "Voucher provider"** = a child care provider approved by the division as eligible to receive
  child care reimbursement through the CCDF program.

### Family-income / sliding-fee provisions found in this PDF — ⚠️ DIFFERENT PROGRAM (not CCDF)
> ⚠️ **POSSIBLY SUPERSEDED / WRONG PROGRAM — verify against the current FSSA CCDF Policy Manual + 2026
> Sliding Fee Schedule; use the Policy Manual / current tables for actual dollar values and thresholds.
> Cite IAC only for legal structure where it agrees with current operative sources.**
>
> The only "sliding fee schedule" and "family income" text in this 191-page export is in **Rule 4.6 —
> "School Age Child Care Program" (470 IAC 3-4.6)**, authorized by **IC 12-17-12** — a SEPARATE state
> grant program, NOT the CCDF voucher program (IC 12-17.2-3.5). It was last substantively amended in
> **1992** (filed Dec 1 1992, 16 IR 1087; readopted 2001/2007/2013/2019). Its fee schedule tops out at
> **$10 for families at 190% of poverty** and is per-unit-of-service — structurally unrelated to the
> CCDF copay (factor × monthly income, brackets to ~Max SMI, updated 2026). **Do NOT use these values
> for the CCDF implementation.** Recorded here only so future agents don't re-fetch chasing a CCDF
> family-income table in the IAC that does not exist (CCDF's lives in the FSSA Policy Manual + fee
> schedule, not the administrative code).

Rule 4.6 program title: "School Age Child Care Program" (PDF file p.50).

**SACC sliding fee schedule — 470 IAC 3-4.6-4 Sec. 4(c)** (PDF file p.52;
https://iar.iga.in.gov/code/2025/470/3#470-3-4.6-4):

| Percent of Poverty Level | Fee Per Family, Per Unit of Service |
|---|---|
| 0–100% | No fee |
| 101–109% | $1 |
| 110–118% | $2 |
| 119–127% | $3 |
| 128–136% | $4 |
| 137–145% | $5 |
| 146–154% | $6 |
| 155–163% | $7 |
| 164–172% | $8 |
| 173–181% | $9 |
| 182–190% | $10 |

- 4.6-4 Sec. 4(d): children above 190% poverty may be served; provider sets the fee.
- 4.6-4 Sec. 4(g): a "unit" = 4+ hours of school-age care for one child; one-half unit = up to 4 hours.

**SACC family-income / eligibility — 470 IAC 3-4.6-7** (PDF file p.56–57;
https://iar.iga.in.gov/code/2025/470/3#470-3-4.6-7):
- Sec. 7(b): provider must obtain a declaration of (1) **family income**, (2) a service-need basis (CPS
  referral, employment, vocational training under a degree program, or physical/mental incapacity of the
  custodian), and (3) the **child's age, 5–15 years**.
- Sec. 7(c): federal **OMB poverty guidelines** are used to determine the poverty level for the sliding fee.
- Sec. 7(d): the fee is based on **gross income received in the 30-day period prior to application**.
- Sec. 7(e): **"Family income includes"** money/wages/salary; AFDC grants; Social Security (incl.
  disability, SSI, old-age pensions); interest/rents/dividends; net self-employment income; pensions and
  annuities; unemployment compensation. *(Note the dated terms — "AFDC" pre-dates TANF — confirming this
  is the legacy SACC program, not current CCDF.)*

> **Bottom line on values:** The IAC family-income/fee values do **NOT** match the current Policy Manual
> CCDF values already in §3–§5 above (different program, different structure, frozen since 1992). The
> CCDF voucher program's countable income, income limits, and copay come from the FSSA **Policy Manual**
> and **2026 Sliding Fee Schedule** (§3–§5), not from 470 IAC. The IAC's value to the CCDF
> implementation is the **legal authority chain** (IC 12-17.2-3.5; 45 CFR 98/99) and the **Rule 18-1
> definitions** of "Provider", "Voucher program/payment/provider", and "Legally licensed exempt".
