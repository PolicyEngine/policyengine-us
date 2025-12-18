# Kansas TANF Implementation Notes

**Created:** 2024-12-18
**Updated:** 2024-12-18 (fixes implemented)
**Purpose:** Document research findings and implementation gaps for Kansas TANF

## FIXES IMPLEMENTED

1. ✅ Removed $82 minimum benefit (was incorrect - only applies to Diversion Payment)
2. ✅ Added $90 work expense deduction parameter (KEESM 8151)
3. ✅ Updated earned income deductions formula: deductions = $90 + (gross - $90) × 0.60
4. ✅ Added 30% FPL gross income limit (K.S.A. 39-709)
5. ✅ Added `ks_tanf_gross_income_eligible` variable
6. ✅ Updated `ks_tanf_eligible` to include gross income test
7. ✅ Updated all tests to reflect new formulas

---

---

## CRITICAL FIXES NEEDED

### 1. REMOVE $82 Minimum Benefit (INCORRECT)
- **Problem:** The $82 threshold is for DIVERSION PAYMENT eligibility, NOT regular TANF
- **Source:** [KEESM 1111](https://content.dcf.ks.gov/ees/keesm/Current/keesm1111_1.htm)
- **Quote:** "A working family who qualifies for $82.00 or less a month in TANF benefits would not be eligible" - this refers to Diversion Payment eligibility
- **Fix:** Remove `minimum_benefit` parameter and logic from `ks_tanf.py`

### 2. ADD $90 Work Expense Deduction (MISSING)
- **Problem:** KEESM 8151 requires $90 work expense deducted BEFORE 60% disregard
- **Source:** [KEESM 8151](https://content.dcf.ks.gov/ees/keesm/robo10-17/keesm8151.htm)
- **Current formula:** `countable = gross_earned × 0.40`
- **Correct formula:** `countable = (gross_earned - $90) × 0.40`
- **Fix:** Add `work_expense_deduction` parameter ($90) and update calculation

### 3. ADD 30% FPL Gross Income Limit (MISSING)
- **Problem:** No gross income eligibility test exists
- **Source:** K.S.A. 39-709; Kansas TANF State Plan FFY 2024-2026
- **Rule:** Income must be < 30% of Federal Poverty Level
- **Practical limits (2024):**
  - Family of 1: ~$281/month
  - Family of 2: ~$376/month
  - Family of 3: ~$519/month
  - Family of 4: ~$655/month
- **Fix:** Add `ks_tanf_gross_income_eligible` variable and parameter

### 4. EXEMPT Children's Earned Income (MISSING)
- **Problem:** Children's earned income should be exempt
- **Source:** [KEESM 6410](https://content.dcf.ks.gov/ees/keesm/robo10-21/keesm6410.htm)
- **Rule:** Earned income for children under 18 (or 18-19 if in school) is exempt
- **Fix:** Create Kansas-specific earned income variable that excludes children

---

## CORRECT INCOME CALCULATION ORDER (Per KEESM 8151)

```
1. Start with Gross Earned Income
2. Subtract $90 standard work expense deduction (per employed person)
3. Apply 60% earned income disregard to remainder
4. Result = Countable Earned Income
5. Add Unearned Income (no disregard)
6. Result = Total Countable Income
```

**Formula:**
```
countable_earned = max((gross_earned - $90_per_worker), 0) × 0.40
countable_income = countable_earned + unearned_income
benefit = floor(max(payment_standard - countable_income, 0))
```

---

## LEGAL SOURCES VERIFIED

### Kansas Statutes
- **K.S.A. 39-709:** TANF eligibility, time limits, work requirements
  - URL: https://ksrevisor.gov/statutes/chapters/ch39/039_007_0009.html

### Kansas Administrative Regulations (K.A.R.)
- **K.A.R. 30-4-41:** Assistance planning for TANF
- **K.A.R. 30-4-50:** Assistance eligibility (time limits, disqualifications)
- **K.A.R. 30-4-64:** Work program requirements
- **K.A.R. 30-4-70:** Eligibility factors specific to TAF program
- **K.A.R. 30-4-100:** Payment standards
- **K.A.R. 30-4-110:** Income calculation
  - URL: https://www.law.cornell.edu/regulations/kansas/agency-30/article-4

### KEESM Sections
- **KEESM 1111:** Program Descriptions (Diversion Payment $82 rule)
  - URL: https://content.dcf.ks.gov/ees/keesm/Current/keesm1111_1.htm
- **KEESM 5000/5110:** Resources ($3,000 limit)
  - URL: https://content.dcf.ks.gov/ees/keesm/current/keesm5000.htm
- **KEESM 6300:** Earned Income definition
  - URL: https://content.dcf.ks.gov/ees/keesm/robo01-22/keesm6300.htm
- **KEESM 6410:** Income Exempt as Income Only (children's income)
  - URL: https://content.dcf.ks.gov/ees/keesm/robo10-21/keesm6410.htm
- **KEESM 7110:** Prospective Budgeting
  - URL: https://content.dcf.ks.gov/ees/keesm/current/keesm7110.htm
- **KEESM 7400:** Rounding standards
  - URL: https://content.dcf.ks.gov/ees/keesm/current/keesm7400.htm
- **KEESM 8151:** Deduction From Earned Income ($90 work expense)
  - URL: https://content.dcf.ks.gov/ees/keesm/robo10-17/keesm8151.htm

### Implementation Memos
- **2008-0326:** TAF Earned Income Disregard (60%)
  - URL: https://content.dcf.ks.gov/ees/keesm/implem_memo/2008_0326_TAF_ei_disregard.htm
- **2008-1117:** Work Incentive Payment ($50/month)
  - URL: https://content.dcf.ks.gov/ees/keesm/implem_memo/2008_1117_taf_work_incent_paymnt.html

---

## PARAMETERS SUMMARY

| Parameter | Value | Source |
|-----------|-------|--------|
| Gross income limit | 30% of FPL | K.S.A. 39-709; State Plan |
| Resource limit | $3,000 | KEESM 5110 |
| Work expense deduction | $90/worker | KEESM 8151 |
| Earned income disregard | 60% | Memo 2008-0326 |
| Payment standard (size 1) | $224 | K.A.R. 30-4-100 |
| Payment standard (size 2) | $309 | K.A.R. 30-4-100 |
| Payment standard (size 3) | $386 | K.A.R. 30-4-100 |
| Payment standard (size 4) | $454 | K.A.R. 30-4-100 |
| Additional person | $61 | K.A.R. 30-4-100 |
| Time limit | 24 months | K.S.A. 39-709 |

---

## WHAT'S CORRECTLY IMPLEMENTED

1. ✓ Resource limit: $3,000
2. ✓ 60% Earned Income Disregard rate
3. ✓ Payment standards by family size (Plan I/II)
4. ✓ Net income test (countable < payment standard)
5. ✓ Rounding down to nearest dollar
6. ✓ Demographic eligibility via federal baseline

---

## KNOWN LIMITATIONS (Cannot Simulate)

1. 24-month lifetime limit (requires benefit history)
2. Work participation requirements (requires tracking)
3. Progressive sanctions (requires violation history)
4. County-specific payment plans III-V (only Plan I/II implemented)
5. Work Incentive Payment ($50 × 5 months)
6. Diversion Payment ($1,000 lump sum)
