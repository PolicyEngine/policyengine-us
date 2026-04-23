# NY UI Requirements Checklist

**Total requirements: 41** (28 simulatable + 13 not-modeled/out-of-scope)

| REQ | Tag | Description | Status |
|---|---|---|---|
| REQ-001 | INCOME | Standard base period = first 4 of last 5 completed calendar quarters | To do |
| REQ-002 | INCOME | Alternate base period = last 4 completed calendar quarters | To do |
| REQ-003 | INCOME | Quarter of filing excluded from base period | To do (approximation) |
| REQ-004 | INCOME | Per-quarter wage inputs for 4 base-period quarters | To do |
| REQ-005 | INCOME | Derive ny_ui_high_quarter_wages = max of 4 quarters | To do |
| REQ-006 | INCOME | Count quarters with non-zero wages | To do |
| REQ-007 | ELIGIBILITY | High-quarter minimum: $3,400 (2025), $3,500 (2026-01-05) | To do |
| REQ-008 | ELIGIBILITY | High-quarter minimum is indexed — use date-keyed parameter | To do |
| REQ-009 | ELIGIBILITY | Work-in-2-quarters test: wages in ≥ 2 quarters | To do |
| REQ-010 | ELIGIBILITY | 1.5x total-wages test (when HQ < cap) | To do |
| REQ-011 | ELIGIBILITY | 1.5x test capped case: when HQ ≥ $19,118, other 3 qtrs ≥ $9,559 | To do |
| REQ-012 | ELIGIBILITY | ny_ui_monetarily_eligible = all 3 tests pass | To do |
| REQ-013 | BENEFIT | Standard WBR: HQ/26 if HQ>$3,575; HQ/25 if HQ≤$3,575 (4-quarter case) | To do |
| REQ-014 | BENEFIT | 2/3-quarter WBR tier 1: HQ>$4,000 → avg of 2 highest qtrs / 26 | To do |
| REQ-015 | BENEFIT | 2/3-quarter WBR tier 2: $3,576–$4,000 → HQ / 26 | To do |
| REQ-016 | BENEFIT | 2/3-quarter WBR tier 3: HQ≤$3,575 → HQ / 25 | To do |
| REQ-017 | BENEFIT | WBR rounded down (floor) to nearest whole dollar | To do |
| REQ-018 | BENEFIT | Minimum WBR: $140 as of 2026-01-01 (was $104 historically) | To do |
| REQ-019 | BENEFIT | Maximum WBR: $504 through 2025-10-12; $869 from 2025-10-13 | To do |
| REQ-020 | BENEFIT | Max WBR indexed at 50% SAWW annually from 2025-10-13 (parameter update) | To do |
| REQ-021 | BENEFIT | Final WBR = min(max(floor(raw), min), max) | To do |
| REQ-022 | PARTIAL | Partial benefit credit = ceil(max(0.50 × WBR, $100)) | To do |
| REQ-023 | PARTIAL | Partial employment test: gross weekly compensation < WBR + PBC | To do |
| REQ-024 | PARTIAL | Hours-based tiers: 0-10h→100%, 11-16h→75%, 17-21h→50%, 22-30h→25%, 31+h→0% | To do |
| REQ-025 | PARTIAL | Hours cap: max 10 hours per calendar day when totaling weekly hours | To do (doc. limitation) |
| REQ-026 | PARTIAL | Gross earnings cap: if earnings > max WBR → no benefit (excl. self-employment) | To do |
| REQ-027 | PARTIAL | Self-employment earnings excluded from gross-earnings cap (hours still count) | To do |
| REQ-028 | DURATION | Maximum duration: 26 weeks within 52-week benefit year | To do |
| REQ-029 | DURATION | Maximum benefit amount = WBR × 26 | To do |
| REQ-030 | DURATION | ny_ui_weeks_unemployed input (0–26) | To do |
| REQ-031 | BENEFIT | ny_ui annual benefit = sum of weekly payables, capped at MBA | To do |
| REQ-032 | NOT-MODELED | Total/partial unemployment status (§ 522) | Not modeled |
| REQ-033 | NOT-MODELED | Able, available, actively seeking work (§ 591) | Not modeled |
| REQ-034 | NOT-MODELED | Disqualifications — voluntary quit, misconduct, refusal (§ 593) | Not modeled |
| REQ-035 | NOT-MODELED | Dismissal pay exclusion (§ 591(6)) | Not modeled |
| REQ-036 | NOT-MODELED | Pension offset — § 600 | Not modeled |
| REQ-037 | NOT-MODELED | Shared Work / STC (§ 599) | Not modeled |
| REQ-038 | NOT-MODELED | Self-Employment Assistance Program / SEAP (§ 591-a) | Not modeled |
| REQ-039 | NOT-MODELED | Extended Benefits (EB) — federal/state trigger program | Not modeled |
| REQ-040 | NOT-MODELED | Alternate base period automatic election / recalculation (§ 527) | Not modeled (input flag) |
| REQ-041 | EXEMPTION | No dependent allowance in NY UI (confirmed § 590) | Confirmed — no code needed |

---

**Simulatable requirements**: REQ-001 through REQ-031 (31 items)
**Not-modeled / out-of-scope**: REQ-032 through REQ-040 (9 items)
**Exemption confirmed / no code**: REQ-041 (1 item)
