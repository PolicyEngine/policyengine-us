# Batch F — sweep of state and local credits outside batches A-E

Audited against upstream/main 06c0dcbc54 (2026-11-11). Read-only; no tests run. Rows: `batch-F.csv` (91 rows, built by `work-F/build_csv.py` from `work-F/rows_*.py`). Tests: `tests-F/` (6 files, 7 cases, not run; YAML parses). Sources saved under `src/`.

Method: listed every file under `variables/gov/states/*/tax` and `variables/gov/local` (5,309 files), extracted the income variable each credit, rebate or relief file reads (`work-F/credit_income_reads.txt`), and listed the parameter files that hold income-source lists. Credits whose law uses federal or state AGI as PE does are in the coverage table (section 2). Credits whose law defines a different measure got a full audit (section 3).

Counts: 12 definitions audited in full (27 definitions in the CSV, counting the 15 AGI-type credits whose law was opened); 26 confirmed category gaps (25 undercount, 1 overcount) plus 2 timing gaps; 7 two-readings; 0 covered by an open PR; 3 not-modelable; 3 unverified.

## 1. Findings

| State | Credit | Finding | Class | Dollar direction |
|---|---|---|---|---|
| TN | Elderly property tax relief | Income is the tax unit's federal AGI; the rule counts all Social Security "after the Medicare deduction", so the nontaxable part is missing | CONFIRMED | Income too low, relief granted to ineligible households (largest effect in this batch) |
| TN | Elderly property tax relief | SSI, veterans' benefits, workers' compensation, tax-exempt interest, nontaxable pensions and Roth distributions, and nontaxable alimony are missing (six rows) | CONFIRMED | Income too low, relief too high |
| TN | Elderly property tax relief | Income of a spouse on a separate return and of co-owners is not counted (T.C.A. 67-5-702(a)(2)) | CONFIRMED (spouse); NOT-MODELABLE (co-owners) | Income too low |
| TN | Elderly property tax relief | The rule tests income of "the calendar year prior to the tax year"; PE tests the same year | TIMING | Either way |
| TN | Elderly property tax relief | Medicare premiums withheld from Social Security come off; no input | NOT-MODELABLE | Matters only after the fix |
| CO (Denver) | Property tax relief | `pension_income` is listed without `military_retirement_income` (the #10769 failure) | CONFIRMED | Income too low, rebate too high |
| CO (Denver) | Property tax relief | Retirement account distributions (IRA, 401(k)) are not counted, though "all financial income resources" count | CONFIRMED | Income too low |
| CO (Denver) | Property tax relief | Old Age Pension and Aid to the Needy Disabled are named as income but not counted | CONFIRMED | Income too low |
| CO (Denver) | Property tax relief | Capital gains, farm, partnership, estate, gambling and other income are not counted | CONFIRMED (general clause) | Income too low |
| CO (Denver) | Property tax relief | Unrelated adults who share the home: SPM unit vs "family or social unit" | TWO-READINGS | Under the wider reading, income too low |
| CO (Denver) | Property tax relief | The ordinance (D.R.M.C. 53-492) could not be opened; rows rest on the city's program guidelines | UNVERIFIED | — |
| IL | Senior real estate tax deferral (outside `states/*/tax`) | Household income is `irs_gross_income`: nontaxable Social Security, tax-exempt interest, nontaxable annuities, public assistance and workers' compensation are missing (four rows) | CONFIRMED | Income too low, deferral granted to ineligible households |
| IL | Senior real estate tax deferral | The base is gross income before above-the-line deductions and without losses; the law starts from AGI | CONFIRMED | Income too high (small) |
| VA | Low-income credit | Family Virginia AGI includes each dependent's Virginia AGI; PE reads the filers' `va_agi` | CONFIRMED | Income too low, credit too high |
| VA | Low-income credit | A spouse on a separate return is not combined | CONFIRMED (narrow) | Income too low |
| UT | Child tax credit | PE phases out on `ut_taxable_income` (after Utah subtractions and the state tax refund); the statute and worksheet use AGI + additions + tax-exempt interest | CONFIRMED | Income too low, credit too high by 10 cents per dollar |
| OR | Oregon Kids Credit | Losses above $20,000 are not added back (ORS 315.273(1)(c)(A)) | CONFIRMED | Income too low, credit too high |
| OR | Oregon Kids Credit | DOR's worksheet also adds back the foreign earned income exclusion and the OBBBA tip, overtime and car-loan deductions; the statute does not | TWO-READINGS (2) | Under the agency's reading, income too low |
| MN | Marriage credit | The lesser earner's income omits taxable 401(k), 403(b) and IRA distributions (Schedule M1MA line 3: Form 1040 lines 4b and 5b) | CONFIRMED | Income too low, credit too LOW |
| MN | Marriage credit | Military retired pay: excluded by the statute ("to the extent included in Minnesota taxable income"), counted by the schedule | TWO-READINGS | Under the form, credit too low |
| MN | Marriage credit | Social Security after Minnesota's subtraction (statute) vs Form 1040 line 6b (schedule); already a source-conflict candidate in #10722 | TWO-READINGS | Under the statute, income too high |
| MN | K-12 education credit | For 2021 and 2022 the law tested "income" (AGI plus nontaxable income); PE tests AGI | CONFIRMED (historical) | Income too low, credit too high, 2021-2022 only |
| DC | Schedule H property tax credit | A spouse or partner on a separate return in the same home is not combined | CONFIRMED (narrow) | Income too low |
| DC | Schedule H property tax credit | The broad "household gross income" definition survives in (b)(1), but the tables since 2014 use AGI of the tax filing unit; PE follows the tables | TWO-READINGS | None under PE's reading |
| DC | Schedule H property tax credit | Federal AGI (form) vs DC AGI (statute's cross-reference) | TWO-READINGS | Under the statute, income lower |
| DC | Senior/disabled property tax relief | "All persons residing in a household" vs PE's SPM unit | CONFIRMED | Income too low |
| DC | Senior/disabled property tax relief | AGI of the federal tax year ending before the property tax year begins; PE uses the same year | TIMING | Either way |
| KY | Family size credit | Interest on other states' bonds is added; PE has no in-state/out-of-state split | NOT-MODELABLE | Income too low |
| WV | Low-income family credit | Matches the statute's three terms | match | — |

Side findings outside the income definitions (not in the counts):
- MN K-12 credit: PE's 2023 threshold (36,980) and limit (41,400) are the old-law indexed amounts, but Laws 2023 c 64 art 1 s 37 is "effective for taxable years beginning after December 31, 2022" with $70,000 of AGI. PE's `amount_per_child` is 1,500 from 2021; the 2022 statute said $1,000. The 2023 Schedule M1ED was not found, so this is unverified against the form.
- OR Kids Credit: ORS 315.273(3)(c) bars a married taxpayer filing separately; `or_ctc` has no filing-status test.
- The #10769 pattern elsewhere: 30 parameter lists under `tax/` and `local/` name `pension_income` or `taxable_pension_income` without `military_retirement_income` (`work-F/pension_lists.txt` holds all 141 lists that name pension income, in any folder). Besides Denver, the credit-related ones are MN marriage credit (two-readings, above), ND marriage penalty credit (statute excludes military pay through "to the extent included in North Dakota taxable income"; match), and OH pension-based retirement credit (not audited). The rest are state tax bases and exclusions, or county assistance programs (LA EZ-SAVE, California county general relief), which this audit does not cover.

## 2. Coverage: every state, and the credits left to the AGI table

"O" = the law was opened this session and the quoted words read. "R" = PE's own code reference or comment was read, the law itself was not opened (not verified independently).

| State | Credits swept (batch F) | Income PE reads | Law's measure and citation | Result |
|---|---|---|---|---|
| AK | Permanent fund dividend, energy relief | none | no income test | nothing to audit |
| AL | Senior homestead exemption (state portion) | none | "Age 65 and over ... Income Limitation: None" for the state exemption (ALDOR homestead exemptions page, O). County tiers (state AGI under $12,000; federal taxable income of $12,000 or less) are not modeled | AGI-type; no gap in what is modeled |
| AR | Low-income tables, additional credit for qualified individuals, inflation relief credit, CDCC | Arkansas taxable income; federal credit | same (R) | AGI-type |
| AZ | Family tax credit | `az_agi + az_exemptions` | "Arizona adjusted gross income, plus the amount subtracted for exemptions under section 43-1023" (A.R.S. 43-1073, R) | match |
| AZ | Increased excise tax credit; dependent credit | federal AGI | "whose federal adjusted gross income is" (A.R.S. 43-1072.01, O); "federal adjusted gross income" (43-1073.01, O) | match |
| CA | Renter's credit | `ca_agi` | "if adjusted gross income is fifty thousand dollars ($50,000) or less" (R&TC 17053.5, O) | match |
| CA | CalEITC, young child, foster youth credits, CDCC | CalEITC earned income; federal AGI | R&TC 17052 (R) | AGI-type |
| CO | CDCC, low-income CDCC, CTC, family affordability, care worker, senior housing credits | federal AGI | (R) | AGI-type. Sales tax refund: batch D. PTC rebate: not modeled |
| CO local | Denver property tax relief | custom list | HOST guidelines | **audited (3.3)** |
| CT | Property tax credit | `ct_agi` | "whose Connecticut adjusted gross income exceeds" (C.G.S. 12-704c, O) | match |
| CT | 2022 child tax rebate | federal AGI | (R) | AGI-type. No circuit breaker modeled |
| DC | Schedule H credit | federal AGI | D.C. Code 47-1806.06 (O) | **audited (3.5)** |
| DC | Senior/disabled property tax relief | SPM-unit AGI | D.C. Code 47-863 (O) | **audited (3.6)** |
| DC | CTC, EITC, child care credit | federal AGI; DC taxable income | (R) | AGI-type |
| DE | Personal credits, EITC, CDCC, relief rebate | none / tax | (R) | no income test |
| FL, NV, SD, WY | payroll tax only | — | — | nothing to audit |
| GA | Low-income credit | federal AGI | "for each adjusted gross income bracket" (O.C.G.A. 48-7A-3(b), O). The section does not say federal or Georgia AGI; the form was not opened | AGI-type; which AGI unverified |
| HI | Food/excise credit | federal AGI | "'adjusted gross income' means adjusted gross income as defined by the Internal Revenue Code" (HRS 235-55.85(g), O); N-311 "federal adjusted gross income" (O) | match |
| HI | Low-income renters credit | `hi_agi` | "'Adjusted gross income' is defined by section 235-1" (HRS 235-55.7(a)(1), O) | match |
| HI | CDCC, Act 115 rebate | `hi_agi`; federal AGI | (R) | AGI-type |
| IA | CDCC | Iowa net/taxable income | (R) | AGI-type. Modified income: batch E |
| ID | Grocery credit, rebates | none | (R) | no income test |
| IL | Property tax credit, K-12 credit | federal AGI | "if the taxpayer's adjusted gross income for the taxable year exceeds (i) $500,000 ... or (ii) $250,000" (35 ILCS 5/208, O) | match |
| IL | Senior real estate tax deferral (`il/idor`, outside the path) | `irs_gross_income` | 320 ILCS 25/3.07 (O) | **audited briefly (3.12)** |
| IN | Unified tax credit for the elderly | federal AGI | "'Household federal adjusted gross income' means the total adjusted gross income, as defined in Section 62 of the Internal Revenue Code, of an individual, or of an individual and his spouse if they reside together" (IC 6-3-3-9, O) | match |
| IN | Over-65 property tax credit | federal AGI two years back | "adjusted gross income (as defined in Section 62 of the Internal Revenue Code)" "for the calendar year preceding by two (2) years" (IC 6-1.1-20.6-8.5, O) | match (including timing) |
| IN | Blind/disabled credit, supplemental homestead credit | none | (R) | no income test |
| KS | Food sales tax credit | federal AGI | "had federal adjusted gross income for the tax year that did not exceed $30,615" (K.S.A. 79-32,271, O) | match. Homestead refund and SAFESR: not modeled |
| KY | Family size credit | `ky_modified_agi` | KRS 141.010(23) (O) | **audited (3.8)** |
| LA | CDCC, school readiness credits | federal AGI | (R; the R.S. 47:297.4 page fetched held no text) | AGI-type, not verified |
| MA | Limited income credit | `ma_agi` | (R) | AGI-type. Circuit breaker: batch E |
| MD | Poverty level credit | federal AGI + Maryland additions; EITC earned income | "whose federal adjusted gross income as modified under 10-204 through 10-206 of this title does not exceed the applicable poverty income level" (Tax-Gen. 10-709, O) | match |
| MD | Senior credit, CTC, CDCC | federal AGI | (R) | AGI-type. Renters' and homeowners' credits: not modeled |
| ME | Dependent exemption credit, relief rebate, affordability payment | `me_agi`; federal AGI | (R) | AGI-type. Fairness credits: batch E |
| MI | EITC | — | — | Household resources: batch A |
| MN | K-12 education credit | federal AGI | Minn. Stat. 290.0674 (O) | **audited (3.11)** |
| MN | Marriage credit | custom list | Minn. Stat. 290.0675 (O) | **audited (3.10)** |
| MN | Child and working family credits, CDCC | AGI, earned income | (R) | AGI-type |
| MO | Working families credit | federal EITC | (R) | AGI-type |
| MS | CDCC; homestead exemption | federal AGI; none | (R) | AGI-type |
| MT | EITC, capital gain credit, rebates | — | — | Elderly credit: batch B |
| NC | Child credit (historical) | federal AGI | G.S. 105-153.10 "Repealed by Session Laws 2015-241, s. 32.13(c), effective for taxable years beginning on or after January 1, 2018" (O) | AGI-type (R for the old text) |
| ND | Marriage penalty credit | custom list | "'Qualifying income' means the sum of the following, to the extent included in North Dakota taxable income: (1) Earned income ...; and (2) Income received from a retirement pension, profit-sharing, stock bonus, or annuity plan" (N.D.C.C. 57-38-01.28(4), O) | match. Primary residence credit: no income test |
| NE | CDCC | federal AGI | "returns filed reporting federal adjusted gross incomes" (Neb. Rev. Stat. 77-2715.07, O) | match. Child care credit: batch D |
| NH | Education tax credit | none | (R) | no income test |
| NJ | CTC, CDCC, EITC, property tax deduction/credit | NJ taxable income; NJ gross income | (R) | AGI-type |
| NM | CTC | federal AGI | (R) | AGI-type. Modified gross income: batch B |
| NY | Household credit | federal AGI (+ separate spouse's) | "'Household gross income' shall mean the aggregate federal adjusted gross income of a household" (Tax Law 606(b), O) | match |
| NY | CTC, CDCC, inflation refund | federal AGI; NY AGI | (R) | AGI-type |
| NYC | School tax credit | federal AGI less IRA distributions | RPTL 425(4)(b)(ii) (R); PE subtracts `taxable_ira_distributions` and `taxable_sep_distributions` and documents what it cannot separate | match with documented limits |
| NYC | Household credit, CDCC, income tax elimination credit, EITC | federal AGI | (R) | AGI-type. Enhanced real property tax credit: not modeled |
| OH | Exemption, senior, CDCC, retirement, joint filing credits | `oh_modified_agi` | R.C. 5747.01(II) as quoted in the variable (R) | AGI-type |
| OK | Child care/child tax credit, EITC | federal AGI | (R) | AGI-type |
| OR | Oregon Kids Credit | `or_agi` | ORS 315.273 (O) | **audited (3.2)** |
| OR | Exemption credit | federal AGI | (R) | AGI-type |
| RI | Child tax credit (2027) | `ri_agi` | "adjusted gross income, as modified pursuant to 44-30-12" (H 7127 Aaa, 44-30-104(c), O) | match |
| SC | Two wage earner credit, EITC, CDCC, tuition credit; homestead exemption | earned income; none | (R) | no household income test |
| TN | Elderly property tax relief | federal AGI | T.C.A. 67-5-702; Rule 0600-03-.08 (O) | **audited (3.1)** |
| TX | School district homestead exemptions | none | (R) | no income test |
| UT | Child tax credit | `ut_taxable_income` + tax-exempt interest | Utah Code 59-10-1047 (O) | **audited (3.7)** |
| UT | Retirement credit, Social Security benefits credit | `ut_total_income` + tax-exempt interest | same three-part structure as the CTC worksheet (TC-40 instructions p. 21, O); statutes not opened | match on the worksheet |
| UT | At-home parent credit, EITC, taxpayer credit | federal AGI; Utah taxable income | (R) | AGI-type |
| VA | Low-income credit | `va_agi` | Va. Code 58.1-339.8 (O) | **audited (3.4)** |
| VT | CTC, veteran credit, CDCC | federal AGI | (R) | AGI-type |
| WA | Working families tax credit | EITC earned income (reduction); AGI (ceiling) | RCW 82.08.0206 as quoted in the variable (R); reviewed in #9391 | not re-audited |
| WA | Senior/disabled property tax exemption (`wa/dor`, outside the path) | custom list citing RCW 84.36.383(7) | not opened | not audited; #10722 edits its list |
| WI | Married couple credit, EITC, itemized deduction credit, school property tax credit | earned income; none | (R) | no household income test |
| WV | Low-income family credit | AGI + tax-exempt interest + additions | W. Va. Code 11-21-22a(d) (O) | **audited (3.9): match** |
| Local | Montgomery County EITC; CA county general relief; LA EZ-SAVE | — | — | not credits with a household income test, or assistance programs; not audited |

States with nothing left for batch F after batches A-E: MI, MO, MT, NM, NJ, PA, RI (other than the 2027 CTC), WI.

## 3. Definitions audited

### 3.1 Tennessee — elderly property tax relief income

**PE.** `variables/gov/states/tn/tax/property/elderly_property_tax_relief/tn_elderly_property_tax_relief_income.py`: `adds = ["adjusted_gross_income"]`, TaxUnit, with the comment "AGI is the closest available tax-unit proxy for statutory income from all sources." `tn_elderly_property_tax_relief_eligible` compares it with `income_limit` (2025: 37,530; 2026: 38,470) for the same period. Losses flow through AGI.

**Law.** T.C.A. 67-5-702(a)(2) (Comptroller's PDF, page 3): "the taxpayer's annual income from all sources shall not exceed ..." and "The income attributable to the applicant for tax relief shall be the income of all owners of the property, the income of applicant's spouse and the income of any owner of a remainder or reversion in the property if the property constituted the person's legal residence at any time during the year". Tenn. Comp. R. & Regs. 0600-03-.08: (1) "The yearly income will be the total combined income of all property owners for the calendar year prior to the tax year for which property tax relief is requested. ALL income must be included." (3) "Annual income from all sources shall include, but is not limited to, social security payments after the Medicare deduction, social security disability after the Medicare deduction, supplemental security income, retirement and pension benefits after deduction of healthcare insurance premiums, veteran's benefits, worker's compensation, unemployment compensation, salaries and wages, alimony, total interest and total dividends. ... Gain or loss from the sale of a principal residence, Temporary Assistance for Needy Families, Supplemental Nutrition Assistance Program, child support, and U.S. Department of Veterans Affairs Aid and Attendance shall not be considered income. ... When determining the income using a tax return, the adjusted gross income amount is used. This amount is added to any income sources specified above which may not be taxable by IRS standards." The 2026 brochure labels $38,470 "Maximum 2025 income of the applicant, spouse, co-owner, and resident remainder".

**Differences.** Missing: nontaxable Social Security, SSI, nontaxable pensions and Roth distributions, veterans' benefits, workers' compensation, tax-exempt interest, nontaxable alimony (all CONFIRMED). Whose income: a spouse on a separate return and co-owners are left out (the co-owner part needs an ownership input PE lacks). Timing: prior calendar year. Not modelable: the Medicare deduction (no input for premiums withheld; `base_part_b_premium` could approximate) and the healthcare-premium deduction from pensions; Aid and Attendance is not separable inside `veterans_benefits`.

**Open PRs.** None for Tennessee relief (`gh pr list --search "Tennessee property tax relief"`: empty). #10070 (gambling in gross income) and #10722 (railroad) do not touch this variable.

**Not verified.** The rule was read on Cornell LII (the Secretary of State's site returned 403); LII notes amendments effective 10/3/2017.

**Tests.** `tests-F/tn_elderly_property_tax_relief_income.yaml` (two cases).

### 3.2 Oregon — Kids Credit qualifying income

**PE.** `or_ctc.py` reads `or_agi` (= `adjusted_gross_income + or_additions - or_income_subtractions`, the last including the federal tax liability subtraction) and phases out between `reduction.start` (2025: 26,550) and start + 5,000. No add-backs.

**Law.** ORS 315.273(1)(c)(A): "adjusted gross income, as defined in section 62 of the Internal Revenue Code, as modified using Oregon subtractions and additions, but with losses of a taxpayer added back, to the extent that those losses exceed $20,000". 2025 Form OR-40 instructions (PDF pages 22-24; revised January 29, 2026): "Have qualifying income under $31,550, including Oregon additions and subtractions and with excluded foreign earned income and total losses greater than $20,000 added back. Deducted tip income, overtime wages, and passenger vehicle interest paid must also be added back." Worksheet Part B lists the losses: Form 1040 line 7a, Schedule 1 lines 3, 4, 5, 6 and 8a, and Schedule OR-ASC codes 321, 355, 356, 357.

**Differences.** Losses above $20,000 are not added back (CONFIRMED). The foreign earned income exclusion and the OBBBA deductions are added back only by the form (TWO-READINGS; statute-first leaves PE as is. PE has no Oregon subtraction for the OBBBA deductions, so its result equals the agency's today).

**Open PRs.** None (`--search "Oregon kids credit"`, `"or_ctc"`).

**Tests.** `tests-F/or_ctc.yaml`.

### 3.3 Denver — property tax relief income

**PE.** `co_denver_property_tax_relief_income` (SPMUnit) adds `gov.local.co.denver.dhs.property_tax_relief.income_sources` (2023 on): `employment_income`, `self_employment_income`, `sstb_self_employment_income`, `alimony_income`, `rental_income`, `disability_benefits`, `pension_income`, `veterans_benefits`, `interest_income`, `dividend_income`, `workers_compensation`, `total_unemployment_compensation`. No loss floor. Read by the homeowner and renter eligibility variables.

**Law.** Denver Department of Housing Stability, Property Tax Relief Program Guidelines, effective May 2026 (PDF pages 3-5): "Income: in determining financial eligibility, whether for the renter or owner rebate calculation, all financial income resources of the household members will be considered as 'income,' except: a. Gifts b. Prior year Elderly and Disabled Refund Program benefits c. Prior year Denver Property Tax Relief Program benefits d. State and Federal Income Tax Returns e. Medicaid f. Supplemental Nutrition Assistance Program (SNAP) g. Child Support/Dependent Income h. Temporary Assistance for Needy Families (TANF) i. Low-Income Energy Assistance (LEAP) j. Education assistance not used for household living and food expenses k. Social Security Disability Insurance (SSDI) l. Supplemental Security Income (SSI) m. Social Security Retirement Benefits". Proof of income "can include, but is not limited to": wages, self-employment, alimony, rental income, "e. Old Age Pension (OAP) f. Aid to the Needy Disabled (AND) g. Pension or annuity benefits h. Veteran benefits i. Taxable and nontaxable interest", dividends, workers' compensation, unemployment. "Household members are those who live in the household, regardless of their age their relationship to the primary applicant, and if they earn reportable income that contributes to household expenses."

**Differences.** Missing: military retired pay, retirement account distributions, OAP and AND, and other income under the general clause (CONFIRMED). The Social Security and SSI exclusion matches. Unrelated household members: TWO-READINGS.

**Open PRs.** None for Denver; #10769 changes only NM and OK.

**Not verified.** The ordinance (D.R.M.C. ch. 53, art. XI) sits on Municode, which blocked automated access; the 2023 instructions PE cites returned HTTP 429 from the Internet Archive. Check the ordinance before changing the list. The guidelines also give a homeowner limit of 80% of AMI for 2025; PE's `ami_rate` was not compared (outside the income definition).

**Tests.** `tests-F/co_denver_property_tax_relief_income.yaml`.

### 3.4 Virginia — family Virginia adjusted gross income

**PE.** `va_low_income_tax_credit_agi_eligible`: `va_agi <= tax_unit_fpg`, where `va_agi = adjusted_gross_income + va_additions - va_subtractions` (tax unit; dependents' own income is not in federal AGI).

**Law.** Va. Code 58.1-339.8(A): "'Family Virginia adjusted gross income' means the combined Virginia adjusted gross income of an individual, the individual's spouse, and any person claimed as a dependent on the individual's or his spouse's income tax return for the taxable year." (B)(1): allowed when it "does not exceed 100 percent of the poverty guideline amount".

**Differences.** Dependents' Virginia AGI is missing (CONFIRMED); a spouse on a separate return is not combined (CONFIRMED, narrow).

**Open PRs.** None on this credit (#9894 and #10134 concern dependents' items in other lines).

**Tests.** `tests-F/va_low_income_tax_credit_agi_eligible.yaml`.

### 3.5 District of Columbia — Schedule H credit

**PE.** `dc_ptc.py` reads the tax unit's `adjusted_gross_income`, floored at zero.

**Law.** D.C. Code 47-1806.06(a)(2)(B)-(D), (2A): "100% of property tax ... exceeding 3.0% of adjusted gross income of the tax filing unit". (j)(1): "household income ... shall be determined on the basis of the adjusted gross income of the tax filing unit, which is defined as an individual or married couple that would—were their income above the filing threshold—file an individual income tax return." (b)(1)(A) still defines "household gross income" broadly (pensions, Social Security, public assistance, workers' compensation), and (b)(2) ties "household income" to DC adjusted gross income (47-1803.02(b)). 2025 D-40 booklet, Schedule H instructions (PDF page 127): "enter the amount that you and, if applicable, your spouse or registered domestic partner reported on Line 4 of your D-40."

**Differences.** PE matches the operative tables and the agency. A couple on separate returns in one home is tested on one spouse (CONFIRMED, narrow). Two TWO-READINGS rows record the vestigial broad definition and the federal-vs-DC AGI question.

**Open PRs.** #10050 (dependent filers in DC) does not change the income measure.

### 3.6 District of Columbia — senior/disabled property tax relief

**PE.** `dc_senior_disabled_property_tax_relief_income`: SPMUnit, `adds = ["adjusted_gross_income"]`; compared with `income_limit` (2025: 159,750) in the same period.

**Law.** D.C. Code 47-863(a)(1): AGI "shall have the same meaning as in section 62 of the Internal Revenue Code". (a)(2): "'Household adjusted gross income' means the adjusted gross income of all persons residing in a household, as determined by each person's federal income tax year ending immediately before the beginning of the real property tax year during which the deduction ... shall be applicable, excluding the adjusted gross income of any person who is a tenant by virtue of a written lease for fair market value."

**Differences.** Whose income: all residents, not the SPM unit (CONFIRMED). Timing: the prior federal tax year (TIMING). Not checked: how core sums a tax-unit variable over an SPM unit holding several tax units.

### 3.7 Utah — child tax credit modified adjusted gross income

**PE.** `ut_ctc_potential.py`: `tax_exempt_interest_income + ut_taxable_income`, where `ut_taxable_income = ut_total_income - ut_subtractions - ut_state_tax_refund` and `ut_total_income = adjusted_gross_income + ut_additions`.

**Law.** Utah Code 59-10-1047(1)(d): "'Modified adjusted gross income' means the sum of the following ...: (i) adjusted gross income ...; (ii) any interest income that is not included in adjusted gross income ...; and (iii) any addition to adjusted gross income required by Section 59-10-114". 2025 TC-40 instructions, Child Tax Credit Worksheet (PDF page 24): "3. Enter the amount from TC-40, line 6 (Total Income) 4. Enter municipal bond interest from TC-40, Schedule A, Part 1, code 57 5. Line 3 minus line 4 6. Enter tax exempt interest from federal form 1040 or 1040-SR, line 2a 7. Modified Adjusted Gross Income Add lines 5 and 6".

**Differences.** PE subtracts Utah subtractions (`us_govt_interest`, `ut_other_subtractions`) and the state tax refund; the law does not (CONFIRMED). PE's retirement and Social Security benefits credits already use `ut_total_income`; the existing `ut_ctc.yaml` cases set `ut_total_income`, which hides the difference.

**Open PRs.** None.

**Tests.** `tests-F/ut_ctc.yaml`.

### 3.8 Kentucky — family size credit modified gross income

**PE.** `ky_modified_agi` = greater of federal AGI and Kentucky AGI, each plus `form_4972_lumpsum_distributions`; separate filers on a combined return floor each column at zero. The variable's comment says other states' bond interest "is not modeled".

**Law.** KRS 141.010(23): "'Modified gross income' means the greater of: (a) Adjusted gross income as defined in 26 U.S.C. sec. 62 ... adjusted as follows: 1. Include interest income derived from obligations of sister states and political subdivisions thereof; and 2. Include lump-sum pension distributions ...; or (b) Adjusted gross income as defined in subsection (1) of this section and adjusted to include lump-sum pension distributions". 740 instructions worksheet (PDF page 26), line (c): "Enter tax-exempt interest from municipal bonds (non-Kentucky)".

**Differences.** Only the sister-state bond interest, which PE cannot separate (NOT-MODELABLE). Otherwise a match.

### 3.9 West Virginia — low-income family tax credit

W. Va. Code 11-21-22a(d): "'Modified federal adjusted gross income' means the federal adjusted gross income plus any applicable increasing West Virginia modifications plus any tax exempt interest income reported on the federal tax return." PE's `wv_low_income_family_tax_credit_agi` adds `adjusted_gross_income`, `tax_exempt_interest_income` and `wv_additions`. Match. (#10178, open, concerns table endpoints, not income.)

### 3.10 Minnesota — marriage credit earned income

**PE.** `mn_marriage_credit.py` sums, per spouse, `gov.states.mn.tax.income.credits.marriage.income_sources` (`irs_employment_income`, `self_employment_income`, `sstb_self_employment_income`, `taxable_social_security`, `taxable_pension_income`) less `self_employment_tax_ald_person`.

**Law.** Minn. Stat. 290.0675 subd. 1(b): "'Earned income' means the sum of the following, to the extent included in Minnesota taxable income: (1) earned income as defined in section 290.01, subdivision 33; (2) income received from a retirement pension, profit-sharing, stock bonus, or annuity plan; and (3) Social Security benefits as defined in section 86(d)(1) of the Internal Revenue Code." 2025 Schedule M1MA instructions (PDF page 2), line 3: "Taxable pension income included on lines 4b and 5b of federal Forms 1040 and 1040-SR. When calculating line 3, do not include any Railroad Retirement Board benefits." Line 4: "Enter the amount from line 6b of federal Form 1040".

**Differences.** Taxable retirement account distributions are missing (CONFIRMED; the credit comes out too low). Military retired pay and the Social Security subtraction are TWO-READINGS; PR #10722 already records the second as candidate `us-mn:marriage-credit-subtracted-social-security`.

**Tests.** None: the credit has no separate income variable and its amount depends on the rate schedules. A fix should expose the per-spouse income as a variable and test that.

### 3.11 Minnesota — K-12 education credit

**PE.** `mn_k12_education_credit.py` and `_eligible.py` read `adjusted_gross_income` for every year from 2021.

**Law.** Current Minn. Stat. 290.0674 subd. 2(a): "For claimants with adjusted gross income not greater than $70,000 ...". Laws 2023 c 64 art 1 s 37: "This section is effective for taxable years beginning after December 31, 2022." The 2022 statute, subd. 2a: "'income' means the sum of the following: (1) federal adjusted gross income ...; and (2) the sum of the following amounts to the extent not included in clause (1): (i) all nontaxable income; ... (iv) cash public assistance and relief; (v) any pension or annuity (including railroad retirement benefits, all payments received under the federal Social Security Act, Supplemental Security Income, and veterans benefits) ...; (vii) workers' compensation; ..."

**Differences.** For 2021 and 2022, PE's AGI leaves out the nontaxable items (CONFIRMED, historical). From 2023 the measure matches; see the side finding on the 2023 parameter values.

### 3.12 Illinois — senior citizens real estate tax deferral (outside `states/*/tax`)

Found while checking for programs stored outside the tax folders. It is a deferral (a lien-backed loan), not a credit, so it is reported briefly.

**PE.** `il_scretd_income_eligible`: tax-unit sum of `irs_gross_income` (positive gross income sources before above-the-line deductions; taxable Social Security only) against `income_limit` (2025: 75,000).

**Law.** 320 ILCS 30/2(h): "'Household income' has the meaning ascribed to that term in the Senior Citizens and Persons with Disabilities Property Tax Relief Act." 320 ILCS 25/3.07: "'Income' means adjusted gross income, properly reportable for federal income tax purposes ..., modified by adding thereto the sum of the following amounts to the extent deducted or excluded from gross income ...: (A) ... interest or dividends ...; (C) ... an annuity ...; (D) An amount equal to the amount of benefits paid under the Federal Social Security Act ...; (E) ... Railroad Retirement Act ...; (F) ... cash public assistance payments ...; (G) ... net operating loss carryover deduction or capital loss carryover deduction ...; and (H) ... Workers' Compensation Act".

**Differences.** Nontaxable Social Security, tax-exempt interest, nontaxable annuities, public assistance and workers' compensation are missing (CONFIRMED); the base should be AGI, not gross income (CONFIRMED, small, opposite direction).

**Not verified.** The relief act's "household" section (320 ILCS 25/3.05-3.06) was not opened.

**Tests.** `tests-F/il_scretd_income_eligible.yaml`.

## 4. Open PRs and issues checked

`gh pr list --state open --search` for: Tennessee property tax relief; Oregon kids credit; or_ctc; Denver property tax relief; DC property tax; Schedule H; Virginia low income credit family; Kentucky family size; Utah child tax credit; Minnesota marriage credit; military_retirement_income; Illinois real estate tax deferral. Read: #10769 (body and file list), #10331 (body), #10722 (diff, for the Minnesota marriage credit and file list), #10070 (file list). None fixes a gap above. No row is classed covered-by-open-PR.

## 5. What could not be verified

- Denver's ordinance text (Municode blocked; archived instructions rate-limited).
- Hawaii's statutes were read from the Department of Taxation's chapter 235 PDF (the Capitol site returned 403).
- Tennessee's rule was read on Cornell LII (the Secretary of State's site returned 403).
- Georgia: which AGI O.C.G.A. 48-7A-3 means; Louisiana R.S. 47:297.4 (page held no text).
- Minnesota: the 2023 Schedule M1ED (side finding on 2023 parameter values); the military retired pay subtraction itself.
- Illinois: the relief act's household definition.
- Every "R" row in section 2: PE's reference was read, the law was not opened.
- One file-handling note: `src/ny_tax_606.html` existed before this batch and was overwritten by a fresh download of the same nysenate.gov page.
