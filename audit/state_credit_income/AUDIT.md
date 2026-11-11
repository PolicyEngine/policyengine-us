# State credit income definitions: audit against the law

Audited against PolicyEngine-US main at `06c0dcbc54` on 2026-11-11. This audit changes no model code.

## Verdict

**178 confirmed gaps** in 35 of the 39 state and local credits audited in full, each a credit whose law defines its own income: 146 leave income out, 27 count too much, and 5 use the wrong year. Another 56 differences turn on a law with two readings, 40 are already fixed by open PRs, and 50 can't be expressed with today's inputs. 347 of the 676 rows match the law.

The gaps aren't random. Ten patterns explain most of them (see [Patterns](#patterns)), and the two that started this audit recur:

- **The #10769 pattern (a pension list without military retired pay or retirement account distributions)** recurs in Michigan, Missouri, Oklahoma, Denver, and in the tax-exempt form in Arizona, Montana, Massachusetts, Rhode Island and Wisconsin.
- **The #10331 pattern (wrong year)** recurs in Oklahoma (earned income credit "received"), New Jersey's Stay NJ (income two tax years before payment), Tennessee and D.C. (prior-year income), and Ohio (prior-year income that reads as zero when only one year is supplied).

Most gaps understate income, so the model pays credits that are too large or pays households the law excludes. The overcounts matter too: four definitions count pre-2019 alimony twice.

**What this audit did not do:** run anything. None of the 140 failing test cases has been run (see [Tests](#tests)). No gap has a dollar estimate. Each finding is a lead to confirm, not a merge-ready fix.

## Scope and method

- **Scope:** every credit, rebate or refund under `variables/gov/states/*/tax` and `variables/gov/local` whose law defines its own income concept: 27 definitions found by name, plus 12 found by a sweep of every other state's credits for laws with their own income concept that the model tests against AGI or another proxy. The sweep also lists 17 credits whose law uses AGI or a similar measure as the model does, one row each.
- **Method, per definition:** read the parameter list and formula down to the inputs; open the statute, any regulation and the current form and instructions; quote each passage with its section or PDF file page; check open PRs before calling anything a gap; classify each difference.
- **Classes:**
  - *Confirmed:* the law is clear and the model differs. Where the statute is silent and the row rests on the agency's form, the row says so.
  - *Two readings:* statute and form disagree, or the text supports two meanings. Both are stated, with the one the agency follows.
  - *Covered:* an open PR fixes it.
  - *Not modelable:* no input can represent the category.
  - *Unverified:* the source could not be opened.
- **Files:**
  - [`audit.csv`](audit.csv): 676 rows, one per state, credit and income category, with the quoted passage, page, citation and source URL.
  - [`details/`](details/): the full write-up for each batch (what the model does, what the law says, differences, PRs checked, what could not be verified).
  - [`tests/`](tests/): 32 YAML files, 140 cases, one or more per confirmed gap that existing inputs can express. Each file's first line names the test file it belongs in.

## Ranked gaps

No gap has been measured. This order is a judgment from two things read in the law and code: how common the missing income is among the credit's target population, and whether the gap changes eligibility or only the amount. [What to measure](#what-to-measure-to-rank-the-gaps) says how to replace it with numbers.

### Tier 1: common income for the target population, eligibility at stake

| # | State | Credit | Gap | Direction |
|---|---|---|---|---|
| 1 | TN | Elderly property tax relief | Income is federal AGI. The rule counts all Social Security, SSI, veterans' benefits, workers' compensation, tax-exempt interest and nontaxable pensions. It also uses prior-year income. | Relief granted to households over the limit |
| 2 | MN | Homestead credit refund | Income is AGI plus nontaxable Social Security and retirement contributions. Minn. Stat. 290A.03 subd. 3 also adds SSI, cash assistance, workers' compensation, tax-exempt interest, nontaxable pensions and retirement distributions, and more (15 rows). | Refund too high |
| 3 | MI | Homestead property tax credit; home heating credit | Total household resources omit IRA and 401(k) distributions, military retired pay, Roth conversions and forgiven debt. Premiums are under-subtracted. | Credits too high (premiums: too low) |
| 4 | OK | Sales tax relief; property tax credit | Sums one tax unit where 68 O.S. 5012 counts "all persons occupying the same household". Omits retirement account distributions, veterans' benefits, disability benefits and TANF. Counts this year's EITC, not the credit received. | Credits too high |
| 5 | WI | Homestead credit | Starts from federal AGI, not Wisconsin AGI, so the medical insurance subtraction is never taken (the instructions' Example 1 gives 10,765; the model gives 12,500). Omits child support, workers' compensation, veterans' benefits and retirement contribution add-backs. | Both ways |
| 6 | NM | Low income comprehensive tax rebate; property tax rebate; child day care credit | Beyond #10769, the list lacks farm and partnership income, workers' compensation, general assistance, disability benefits, forgiven debt, gambling winnings, gifts and scholarships (14 rows). | Rebates too high |
| 7 | OR | Retirement income credit | Household income is AGI plus tax-exempt interest less taxable Social Security. ORS 316.157 also adds veterans' benefits, workers' compensation, child support, SSI and welfare payments, and caps net losses at $1,000 per category. | Credit too high |
| 8 | RI | Property tax relief | Losses reduce income though R.I. Gen. Laws 44-33-3(7) bars them. One tax unit is summed where the law counts the household. SSI, general assistance and veterans' pensions are missing. Pre-2019 alimony counts twice. | Both ways |
| 9 | MO | Property tax credit | Military retirement benefits and U.S. obligation interest are subtracted from Missouri AGI and never added back (RSMo 135.010(5)). General assistance and the state supplement are missing. | Credit too high |
| 10 | IL | Senior real estate tax deferral | Household income is federal gross income, so nontaxable Social Security, tax-exempt interest and public assistance are missing. Checked briefly. | Deferral granted to households over the limit |

### Tier 2: narrower population, or amount only

| # | State | Credit | Gap | Direction |
|---|---|---|---|---|
| 11 | NJ | ANCHOR | Sums `nj_gross_income`, not NJ-1040 line 29: Treasury interest, 401(k) deferrals and dependents' income count. | Benefit too low or lost |
| 12 | NJ | Stay NJ | The benefit paid in a year is set by income two tax years earlier; the model uses same-year income. Dependents' income is counted. | Either way |
| 13 | PA | Property tax/rent rebate | Pre-2019 alimony counts twice. Wages enter net of 401(k) deferrals. Cash assistance and cash gifts are missing. | Both ways |
| 14 | VT | Renter credit | 32 V.S.A. 6061(18) adds back losses and the listed above-the-line deductions; the model starts from AGI. It counts 75% of a dependent's Social Security. | Both ways |
| 15 | UT | Circuit breaker | Alimony counts twice. An adult dependent's income counts as zero. SSI and capital loss carryovers are missing. | Both ways |
| 16 | MA | Senior circuit breaker | Starts from gross income, not AGI. Omits Roth distributions, workers' compensation and state cash aid to the elderly. Long- and short-term capital results net. | Both ways |
| 17 | OH | Homestead exemption | The formula reads last year's income, as the law says. With one year of inputs that read returns zero, so the income limit never binds. Read from code, not run; may not apply in microsimulation. | Exemption granted to everyone aged or disabled |
| 18 | CO (Denver) | Property tax relief | `pension_income` without military retired pay; no retirement account distributions, Old Age Pension or Aid to the Needy Disabled. Rests on the city's guidelines; the ordinance could not be opened. | Rebate too high |
| 19 | MN | Renter's credit | Sums the AGI of every non-dependent adult in the household; the statute counts the renter and spouse. | Credit too low for renters living with other adults |
| 20 | PA | Tax forgiveness | Treasury interest is never added back though 72 P.S. 7301(o.2) names it. Alimony counts twice. Employee retirement contributions are missing. | Both ways |
| 21 | IA | Low-income exemption and alternate tax | The QBI deduction is added back twice. The 2025-2028 tip, overtime and car loan deductions are added back though Iowa Code 422.5 doesn't list them. | Tax too high |
| 22 | NY | Real property tax credit, through 2024 | Counts one tax unit where the law pools the household; omits workers' compensation, child support, veterans' pensions, nontaxable pensions and cash assistance. From 2025 the law uses federal AGI and the model matches. | Credit too high, past years only |

### Tier 3: small or rare

- **MT elderly credit:** post-2018 alimony, tax-exempt 401(k) distributions, savings bond interest, foreign earned income.
- **ND renter's refund:** gambling winnings; capital losses reduce income without limit.
- **AZ property tax credit:** tax-exempt retirement account distributions.
- **ME fairness credits:** SSI; losses netted on the federal return.
- **WV homestead excess credit:** nontaxable disability insurance benefits.
- **NE child care credit:** AGI where the statute says modified AGI.
- **VA low-income credit:** dependents' Virginia AGI left out of family income.
- **UT child tax credit:** phases out on taxable income, not AGI plus additions.
- **OR Kids Credit:** losses above $20,000 not added back.
- **MN marriage credit:** lesser earner's retirement distributions missing (credit too low).
- **DC Schedule H and senior relief:** separate-return spouse; all residents; prior-year income.
- **MN K-12 credit:** 2021-2022 only.

## Patterns

Fixing by pattern is cheaper than fixing state by state, and each pattern is a check for new credits.

1. **`pension_income` is not all retirement income.** It leaves out retirement account distributions and military retired pay, and the tax-exempt account distributions sit in separate variables. Lists that name only `pension_income`: Michigan, Oklahoma, Missouri, Denver (taxable side); Arizona, Montana, Massachusetts, Rhode Island, Wisconsin, Missouri (tax-exempt side). The sweep found 30 parameter lists under `tax/` and `local/` that name pension income without military retired pay.
2. **Alimony counted twice.** Rhode Island, Utah and both Pennsylvania definitions add `alimony_income` to a base that already holds taxable alimony, and `divorce_year` defaults to 2010.
3. **Whose income.** The law counts the household but the model sums one tax unit in Oklahoma, New York, Rhode Island, D.C.'s senior relief and Minnesota's homestead refund. The model counts too many people in Minnesota's renter's credit and both New Jersey programs (dependents), and a dependent's Social Security in Vermont.
4. **Losses.** Statutes bar, cap or add back losses that the model lets through AGI: Rhode Island, Vermont, Oregon, Missouri, Utah. Lists that floor after summing let one person's loss offset another's income: New Mexico, Oklahoma. Maine and Massachusetts go the other way.
5. **Timing.** Oklahoma (credit received), New Jersey Stay NJ (two years earlier), Tennessee and D.C. (prior year), Ohio (prior year reads zero). Montana is right after #10331, but its receipts are inputs that default to zero.
6. **"AGI plus add-backs" definitions stop short.** Public assistance, SSI, workers' compensation and veterans' benefits are missing from Minnesota, Oregon, New York, Rhode Island, Wisconsin, Massachusetts, Tennessee, and SSI alone from Maine and Utah.
7. **The wrong starting line.** Wisconsin (federal, not state, AGI), Massachusetts (gross income, not AGI), New Jersey ANCHOR (gross income, not line 29), Utah child tax credit (taxable income), Nebraska (AGI, not modified AGI), Iowa (double add-back).
8. **Gambling winnings** are outside federal gross income on main. #10070 fixes definitions that read AGI; the lists in North Dakota, New Mexico and Oklahoma stay wrong after it merges.
9. **Railroad retirement:** #10722 covers it in 14 definitions.
10. **Foreign earned income exclusion** is not added back in ten definitions. Rare.

## Laws with two readings

56 rows. These need a ruling under the source-conflict rule before anyone codes them. The ones that block open PRs or move the most:

- **Pennsylvania rent rebate, railroad retirement.** The statute counts 50% of all benefits (main). The booklet counts Tier 1 at 50% and Tier 2 in full. Open PRs #10696 and #10722 move to the booklet: a statute-against-form change.
- **Michigan, dependents' Social Security and SSI.** The form and bulletin count amounts received for children; MCL 206.508(3) says the household is "a claimant and spouse" (#10325).
- **Michigan, nontaxable pensions.** The form counts pensions "to the extent included in AGI"; Treasury's web page says to include nontaxable pensions. The model counts them.
- **West Virginia homestead excess credit.** The form adds other household members' income and SSI; the statute names neither.
- **North Dakota renter's refund, TANF and post-2018 alimony.** Statute and guideline differ; #10697 and #10724 each pick a side.
- **Massachusetts circuit breaker, SNAP.** The statute says cash "but not in-kind" assistance; the Department counts food stamps. The model follows the statute and documents it.
- **Montana elderly credit, above-the-line deductions.** The statute starts from federal AGI; the 2025 schedule adds gross lines.
- **New Jersey Stay NJ, wages.** W-2 box 16 (agency) or gross of 401(k) deferrals.

The rest are in `audit.csv` with `status = two-readings`.

## Covered by open PRs

40 rows. Confirm each when its PR merges.

| PR | Fixes | Definitions |
|---|---|---|
| #10722 | Railroad retirement benefits | MT, ND, NM, OK, MO, MN, WI, NY, RI, VT, CO, MA, ME, WV |
| #10070 | Gambling winnings in federal gross income | MT, MN (both), WI, NY, RI, VT, AZ, CO, UT, OR, NE, MA, ME, WV, IA, PA forgiveness |
| #10769 | Military retired pay | NM, OK |
| #10697 | Federally excluded income | ND renter's refund |
| #10724 | SSI | ND renter's refund |
| #10647, #9894 | Dependents' Social Security and tax-exempt interest | CO sales tax refund, ME fairness credits |

## What to measure to rank the gaps

Run these on Modal, not locally; a full Populace microsimulation needs about 32 GB.

1. **Which inputs carry data.** For each variable a gap names, the weighted national sum and share of nonzero records in Populace. Many (`tax_exempt_disability_benefits`, `strike_benefits`, `debt_relief`) are probably zero everywhere; those gaps matter only in the household calculator. This one table re-ranks half the list.
2. **Missing income among current recipients.** For each credit, among records that receive it on main: the weighted sum of each omitted (or double-counted) variable, by state. A gap with no income mass can wait.
3. **Cost and recipients after the fix.** For the top gaps from step 2, a reform that swaps in the corrected income: change in the credit's cost, in recipients, and in households that cross the limit. Compute `household_net_income` first (#9740).
4. **Against administrative totals.** Where the state publishes claims and dollars (Michigan homestead credit, Minnesota property tax refund, Wisconsin homestead credit, Pennsylvania rebate, New Jersey ANCHOR), compare before and after.
5. **Ohio first, because it is a yes/no.** One household with $99,000 of prior-year Ohio modified AGI and only current-year inputs: does `oh_homestead_exemption_eligible` return true? Then the same question in a microsimulation.

## Tests

`tests/` holds 32 files and 140 cases. Each asserts the income variable (and the credit where it can be hand-computed) at the value the law gives, with the arithmetic and citation in comments. Each file's first line names its target test file.

**Run status: none run.** The machine had too little memory to load the model. One run of `mo_ptc_gross_income.yaml` was started at the end and was stopped for low memory before it produced a result. Until each file is run, treat "failing on main" as a claim from reading the code. The local test environment also has `spm-calculator` 1.0, and main now requires 1.1.

To run one file:

```bash
policyengine-core test audit/state_credit_income/tests/<file>.yaml -c policyengine_us
```

No test was written where the fix needs a design choice first: Stay NJ's two-year lag, Tennessee's and D.C.'s prior-year income, whole-household income in New York and D.C., and Oklahoma's Oklahoma-credit receipt.

## Counts by definition

| State | Credit | Confirmed (under / over / timing) | Two readings | Covered by open PR | Not modelable | Unverified | Match |
|---|---|---|---|---|---|---|---|
| AZ | Dependent tax credit (az_dependent_tax_credit) | 0 (0 / 0 / 0) | 0 | 0 | 0 | 0 | 1 |
| AZ | Increased excise tax credit (az_increased_excise_tax_credit) | 0 (0 / 0 / 0) | 0 | 0 | 0 | 0 | 1 |
| AZ | Property tax credit (Form 140PTC) | 1 (1 / 0 / 0) | 4 | 1 | 2 | 0 | 22 |
| CA | Nonrefundable renter's credit (ca_renter_credit) | 0 (0 / 0 / 0) | 0 | 0 | 0 | 0 | 1 |
| CO | TABOR state sales tax refund (DR 0104 line 38) | 0 (0 / 0 / 0) | 0 | 3 | 1 | 0 | 4 |
| CO (Denver) | Denver Property Tax Relief Program (homeowner and renter rebates) | 4 (4 / 0 / 0) | 1 | 0 | 0 | 1 | 10 |
| CT | Property tax credit (ct_property_tax_credit) | 0 (0 / 0 / 0) | 0 | 0 | 0 | 0 | 1 |
| DC | Schedule H homeowner and renter property tax credit (dc_ptc) | 1 (1 / 0 / 0) | 2 | 0 | 0 | 0 | 2 |
| DC | Senior citizen or disabled property owner tax relief (dc_senior_disabled_property_tax_relief) | 2 (1 / 0 / 1) | 0 | 0 | 0 | 0 | 1 |
| GA | Low-income credit (ga_low_income_credit) | 0 (0 / 0 / 0) | 0 | 0 | 0 | 1 | 0 |
| HI | Refundable food/excise tax credit (hi_food_excise_credit) | 0 (0 / 0 / 0) | 0 | 0 | 0 | 0 | 1 |
| HI | Tax credit for low-income household renters (hi_low_income_household_renters_tax_credit) | 0 (0 / 0 / 0) | 0 | 0 | 0 | 0 | 1 |
| IA | Low-income exemption, single-filer tax reduction and alternate tax (IA 1040 Step 5; worksheets 41-145 and 41-146) | 3 (0 / 3 / 0) | 0 | 1 | 1 | 1 | 8 |
| IL | Property tax credit (il_property_tax_credit) | 0 (0 / 0 / 0) | 0 | 0 | 0 | 0 | 1 |
| IL | Senior Citizens Real Estate Tax Deferral (il_scretd; a deferral, outside states/*/tax, checked briefly) | 6 (5 / 1 / 0) | 0 | 0 | 1 | 1 | 0 |
| IN | Over 65 property tax credit (in_over_65_property_tax_credit) | 0 (0 / 0 / 0) | 0 | 0 | 0 | 0 | 1 |
| IN | Unified tax credit for the elderly (in_unified_elderly_tax_credit) | 0 (0 / 0 / 0) | 0 | 0 | 0 | 0 | 1 |
| KS | Food sales tax credit (ks_fstc) | 0 (0 / 0 / 0) | 0 | 0 | 0 | 0 | 1 |
| KY | Family size tax credit (ky_family_size_tax_credit) | 0 (0 / 0 / 0) | 0 | 0 | 1 | 0 | 3 |
| MA | Senior circuit breaker credit (Schedule CB) | 6 (5 / 1 / 0) | 3 | 2 | 3 | 0 | 20 |
| MD | Poverty level credit (md_poverty_line_credit) | 0 (0 / 0 / 0) | 0 | 0 | 0 | 0 | 1 |
| ME | Property tax fairness credit and sales tax fairness credit (Schedule PTFC/STFC) | 2 (1 / 1 / 0) | 1 | 3 | 0 | 0 | 12 |
| MI | Homestead property tax credit; home heating credit | 10 (8 / 2 / 0) | 4 | 0 | 5 | 0 | 25 |
| MN | Homestead credit refund (Form M1PR) | 16 (15 / 1 / 0) | 1 | 2 | 3 | 0 | 10 |
| MN | K-12 education credit (mn_k12_education_credit) | 1 (1 / 0 / 0) | 0 | 0 | 0 | 0 | 1 |
| MN | Marriage credit (mn_marriage_credit) | 1 (1 / 0 / 0) | 2 | 0 | 0 | 0 | 3 |
| MN | Renter's credit (Schedule M1RENT) | 1 (0 / 1 / 0) | 0 | 1 | 2 | 0 | 6 |
| MO | Property tax credit (RSMo 135.010-135.030; Forms MO-PTS and MO-PTC) | 6 (5 / 1 / 0) | 3 | 1 | 0 | 0 | 14 |
| MT | Elderly homeowner/renter credit (MCA 15-30-2337 to 2341) | 4 (4 / 0 / 0) | 4 | 2 | 5 | 0 | 21 |
| ND | Marriage penalty credit (nd_mpc) | 0 (0 / 0 / 0) | 0 | 0 | 0 | 0 | 1 |
| ND | Renter's refund (N.D.C.C. 57-02-08.1(2)); same income definition as the homestead credit | 2 (2 / 0 / 0) | 4 | 6 | 0 | 0 | 19 |
| NE | Child and dependent care credit (ne_cdcc_refundable) | 0 (0 / 0 / 0) | 0 | 0 | 0 | 0 | 1 |
| NE | Child care refundable tax credit (Child Care Tax Credit Act; ne_refundable_ctc) | 2 (2 / 0 / 0) | 1 | 1 | 0 | 0 | 2 |
| NJ | ANCHOR (nj_anchor, nj_anchor_eligible) | 5 (0 / 5 / 0) | 0 | 0 | 0 | 0 | 2 |
| NJ | Stay NJ property tax credit (nj_staynj, nj_staynj_eligible); Senior Freeze income test (not modelled: nj_senior_freeze is an input) | 3 (0 / 2 / 1) | 4 | 0 | 1 | 0 | 6 |
| NM | Low income comprehensive tax rebate; property tax rebate (65+); child day care credit | 14 (14 / 0 / 0) | 1 | 2 | 3 | 0 | 17 |
| NY | Household credit (ny_household_credit) | 0 (0 / 0 / 0) | 0 | 0 | 0 | 0 | 1 |
| NY | Real property tax credit (IT-214), tax years from 2025 | 0 (0 / 0 / 0) | 0 | 0 | 0 | 0 | 1 |
| NY | Real property tax credit (IT-214), tax years through 2024 | 10 (10 / 0 / 0) | 2 | 2 | 3 | 0 | 7 |
| OH | Homestead exemption for senior citizens, disabled persons and surviving spouses (DTE 105A) | 1 (0 / 0 / 1) | 0 | 0 | 1 | 0 | 7 |
| OK | Sales tax relief credit (68 O.S. 5011-5013, Form 538-S); property tax credit (68 O.S. 2904-2911, Form 538-H) | 10 (9 / 0 / 1) | 3 | 2 | 0 | 0 | 11 |
| OR | Oregon Kids Credit (or_ctc) | 1 (1 / 0 / 0) | 2 | 0 | 0 | 0 | 2 |
| OR | Retirement income credit (ORS 316.157) | 11 (10 / 1 / 0) | 2 | 1 | 4 | 0 | 5 |
| OR | Working family household and dependent care credit (ORS 315.264) | 0 (0 / 0 / 0) | 1 | 0 | 0 | 0 | 2 |
| PA | Property Tax/Rent Rebate (pa_property_tax_or_rent_rebate, pa_property_tax_or_rent_rebate_eligible) | 6 (4 / 2 / 0) | 3 | 0 | 1 | 1 | 14 |
| PA | Tax forgiveness / special tax provisions for poverty (pa_tax_forgiveness_rate, pa_tax_forgiveness_amount; Schedule SP) | 6 (5 / 1 / 0) | 2 | 1 | 2 | 0 | 7 |
| RI | Child tax credit, tax years 2027 on (ri_ctc) | 0 (0 / 0 / 0) | 0 | 0 | 0 | 0 | 1 |
| RI | Property tax relief credit (RI-1040H; ri_property_tax_credit, ri_property_tax_credit_eligible) | 9 (8 / 1 / 0) | 1 | 2 | 1 | 0 | 7 |
| TN | Property tax relief for elderly low-income homeowners | 9 (8 / 0 / 1) | 0 | 0 | 1 | 0 | 7 |
| UT | Homeowner's / renter's (circuit breaker) relief: ut_renters_credit, ut_homeowners_credit | 5 (4 / 1 / 0) | 2 | 1 | 3 | 0 | 16 |
| UT | Nonrefundable child tax credit (ut_ctc) | 1 (1 / 0 / 0) | 0 | 0 | 0 | 0 | 4 |
| VA | Credit for low-income individuals (va_low_income_tax_credit) | 2 (2 / 0 / 0) | 0 | 0 | 0 | 0 | 1 |
| VT | Renter credit (RCC-146; vt_renter_credit) | 3 (2 / 1 / 0) | 1 | 2 | 0 | 0 | 6 |
| WI | Homestead credit (Schedule H / H-EZ) | 13 (11 / 2 / 0) | 0 | 2 | 6 | 0 | 16 |
| WV | Homestead excess property tax credit (Schedule HEPTC-1) | 1 (1 / 0 / 0) | 2 | 2 | 0 | 0 | 8 |
| WV | Low-income family tax credit (wv_low_income_family_tax_credit) | 0 (0 / 0 / 0) | 0 | 0 | 0 | 0 | 1 |
| WV | Senior citizens tax credit (Form SCTC-A) | 0 (0 / 0 / 0) | 0 | 0 | 0 | 0 | 2 |

## What could not be verified

- **Secondary hosts.** New York Tax Law 606(e) was read on newyork.public.law, New Jersey's Gross Income Tax Act on Justia, Tennessee's rule on Cornell LII, and Hawaii's chapter 235 from the Department of Taxation's PDF, because the official sites refused automated fetches.
- **New Mexico PIT-RC instructions.** The PDF's text layer is garbled, so the quotes have restored spacing and inferred line numbers.
- **Denver.** The ordinance (D.R.M.C. 53-492) could not be opened; those rows rest on the city's program guidelines.
- **Unopened:** N.D.C.C. 57-38-30.3(2); the Illinois relief act's household definition; which AGI Georgia's O.C.G.A. 48-7A-3 means; Iowa's 2021 and 2022 instructions; the basis for Pennsylvania's Civil Service Retirement offset.
- **The AGI table** in `details/batch-F.md` section 2: rows marked "R" rest on the model's own references, not on law opened in this audit.
- **Not audited:** Washington's senior property tax exemption and Ohio's pension-based retirement credit list.
- **Quote checks.** Seven quoted passages were re-checked against the downloaded sources and all seven were found. Six code-side claims were re-read (Michigan, Minnesota, Missouri, Rhode Island, Ohio, Tennessee) and all six hold. The other rows have not been independently re-checked.
