# Core Variables

This section documents all variables in the core module.

## Variable List

### able_contributions

**Label**: ABLE contributions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Contributions made to an ABLE account by all members of the tax unit.

### able_contributions_person

**Label**: Person-level ABLE contributions
**Entity**: person
**Period**: year
**Unit**: currency-USD

Contributions made to an ABLE account by each individual.

### above_the_line_deductions

**Label**: Above-the-line deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Deductions applied to reach adjusted gross income from gross income.

**References**:
- https://www.law.cornell.edu/uscode/text/26/62

### aca_child_index

**Label**: Index of child in tax unit (1 = oldest)
**Entity**: person
**Period**: year

### aca_magi

**Label**: ACA-related modified AGI for this tax unit
**Entity**: tax_unit
**Period**: year

### aca_magi_fraction

**Label**: ACA-related modified AGI as fraction of prior-year FPL
**Entity**: tax_unit
**Period**: year

ACA-related MAGI as fraction of federal poverty line.Documentation on use of prior-year FPL in the following reference:  title: 2022 IRS Form 8962 (ACA PTC) instructions, Line 4  href: https://www.irs.gov/pub/irs-pdf/i8962.pdf#page=7Documentation on truncation of fraction in the following reference:  title: 2022 IRS Form 8962 instructions, Line 5 Worksheet 2  href: https://www.irs.gov/pub/irs-pdf/i8962.pdf#page=8

### aca_ptc

**Label**: ACA premium tax credit for tax unit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/36B

### aca_ptc_phase_out_rate

**Label**: ACA PTC phase-out rate (i.e., IRS Form 8962 'applicable figure')
**Entity**: tax_unit
**Period**: year
**Unit**: /1

**References**:
- https://www.law.cornell.edu/uscode/text/26/36B#b_3_A

### aca_take_up_seed

**Label**: Randomly assigned seed for ACA take-up
**Entity**: tax_unit
**Period**: year

### acp

**Label**: Affordable Connectivity Program
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

Affordable Connectivity Program amount

**References**:
- https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title47-section1752&edition=prelim

### additional_medicare_tax

**Label**: Additional Medicare Tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Additional Medicare Tax from Form 8959 (included in payrolltax)

### additional_senior_deduction

**Label**: Senior deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.congress.gov/bill/119th-congress/house-bill/1/text

### additional_senior_deduction_eligible_person

**Label**: Person is eligible for the additional senior deduction
**Entity**: person
**Period**: year

**References**:
- https://www.congress.gov/bill/119th-congress/house-bill/1/text

### additional_standard_deduction

**Label**: Additional standard deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/63#f

### adjusted_earnings

**Label**: Personal earned income adjusted for self-employment tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

### adjusted_gross_income

**Label**: Adjusted gross income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/62

### adjusted_gross_income_person

**Label**: Federal adjusted gross income for each person
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/62

### adjusted_net_capital_gain

**Label**: Adjusted net capital gain
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

The excess of net long-term capital gain over net short-term capital loss.

**References**:
- {'title': '26 U.S. Code § 1(h)(3)', 'href': 'https://www.law.cornell.edu/uscode/text/26/1#h_3'}

### adopted_this_year

**Label**: Person was adopted this year
**Entity**: person
**Period**: year

### adult_earnings_index

**Label**: index of adult in household by earnings
**Entity**: person
**Period**: year

### adult_index

**Label**: Index of adult in household
**Entity**: person
**Period**: year

### adult_index_cg

**Label**: index of adult in household, ranked by capital gains
**Entity**: person
**Period**: year

### advanced_main_air_circulating_fan_expenditures

**Label**: Expenditures on advanced main air circulating fans
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Must be used in a natural gas, propane, or oil furnaces and which have an annual electricity use of no more than 2 percent of the total annual energy use of the furnace.

**References**:
- https://www.law.cornell.edu/uscode/text/26/25C#d_5

### after_school_expenses

**Label**: After school childcare expenses
**Entity**: person
**Period**: year
**Unit**: currency-USD

### age

**Label**: age
**Entity**: person
**Period**: year

### age_group

**Label**: Age group
**Entity**: person
**Period**: year

### age_head

**Label**: Age of head of tax unit
**Entity**: tax_unit
**Period**: year
**Unit**: year

Age in years of taxpayer (i.e. primary adult)

### age_spouse

**Label**: Age of spouse of tax unit
**Entity**: tax_unit
**Period**: year
**Unit**: year

Age in years of spouse (i.e. secondary adult if present)

### aged_blind_count

**Label**: Aged and or blind head and spouse count
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/63#f

### aged_head

**Label**: Aged head
**Entity**: tax_unit
**Period**: year

**References**:
- https://www.law.cornell.edu/uscode/text/26/63#f

### aged_spouse

**Label**: Aged spouse
**Entity**: tax_unit
**Period**: year

**References**:
- https://www.law.cornell.edu/uscode/text/26/63#f

### air_sealing_ventilation_expenditures

**Label**: Expenditures on air sealing and ventilation
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=585

### ak_energy_relief

**Label**: Alaska One Time Energy Relief
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://pfd.alaska.gov

### ak_permanent_fund_dividend

**Label**: Alaska Permanent Fund Dividend
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://pfd.alaska.gov

### al_agi

**Label**: Alabama adjusted gross income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
-  https://alisondb.legislature.state.al.us/alison/CodeOfAlabama/1975/Coatoc.htm

### al_casualty_loss_deduction

**Label**: Alabama casualty loss deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### al_deductions

**Label**: Alabama deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2023/01/22f40abk.pdf

### al_dependent_exemption

**Label**: Alabama dependent exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

https://alisondb.legislature.state.al.us/alison/CodeOfAlabama/1975/Coatoc.htm

### al_federal_income_tax_deduction

**Label**: Alabama federal income tax deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2023/01/22f40abk.pdf#page=20

### al_income_tax

**Label**: Alabama income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### al_income_tax_before_non_refundable_credits

**Label**: Alabama income tax before non-refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
-  https://alisondb.legislature.state.al.us/alison/CodeOfAlabama/1975/Coatoc.htm

### al_income_tax_before_refundable_credits

**Label**: Alabama income tax before refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
-  https://alisondb.legislature.state.al.us/alison/CodeOfAlabama/1975/Coatoc.htm

### al_interest_deduction

**Label**: Alabama investment interest
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/alabama/2022/title-40/chapter-18/article-1/section-40-18-15/https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2023/01/22f40schabdc_blk.pdf#page=1https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2022/06/21f40schabdc_blk.pdf#page=1

### al_itemized_deductions

**Label**: Alabama itemized deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/alabama/2022/title-40/chapter-18/article-1/section-40-18-15/https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2023/01/22f40schabdc_blk.pdf#page=1https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2022/06/21f40schabdc_blk.pdf#page=1

### al_medical_expense_deduction

**Label**: Alabama medical expense deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/alabama/2022/title-40/chapter-18/article-1/section-40-18-15/https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2023/01/22f40schabdc_blk.pdf#page=1https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2022/06/21f40schabdc_blk.pdf#page=1

### al_misc_deduction

**Label**: Alabama Work Related Expense
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/alabama/2022/title-40/chapter-18/article-1/section-40-18-15/https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2023/01/22f40schabdc_blk.pdf#page=1https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2022/06/21f40schabdc_blk.pdf#page=1

### al_non_refundable_credits

**Label**: Alabama non-refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### al_personal_exemption

**Label**: Alabama personal exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

https://alisondb.legislature.state.al.us/alison/CodeOfAlabama/1975/Coatoc.htm

### al_refundable_credits

**Label**: Alabama refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### al_retirement_exemption

**Label**: Alabama retirement exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

https://www.revenue.alabama.gov/wp-content/uploads/2024/01/23schrsinstr.pdf#page=1https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2024/01/23f40bk.pdf#page=14https://casetext.com/statute/code-of-alabama/title-40-revenue-and-taxation/chapter-18-income-taxes/article-1-general-provisions/section-40-18-19-exemptions-generally

### al_retirement_exemption_eligible_person

**Label**: Alabama retirement exemption
**Entity**: person
**Period**: year

https://www.revenue.alabama.gov/wp-content/uploads/2024/01/23schrsinstr.pdf#page=1https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2024/01/23f40bk.pdf#page=14https://casetext.com/statute/code-of-alabama/title-40-revenue-and-taxation/chapter-18-income-taxes/article-1-general-provisions/section-40-18-19-exemptions-generally

### al_retirement_exemption_person

**Label**: Alabama retirement exemption for each person
**Entity**: person
**Period**: year
**Unit**: currency-USD

https://www.revenue.alabama.gov/wp-content/uploads/2024/01/23schrsinstr.pdf#page=1https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2024/01/23f40bk.pdf#page=14https://casetext.com/statute/code-of-alabama/title-40-revenue-and-taxation/chapter-18-income-taxes/article-1-general-provisions/section-40-18-19-exemptions-generally

### al_standard_deduction

**Label**: Alabama standard deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

https://alisondb.legislature.state.al.us/alison/CodeOfAlabama/1975/Coatoc.htm

### al_taxable_income

**Label**: Alabama taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2023/01/22f40abk.pdf

### al_withheld_income_tax

**Label**: Alabama withheld income tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

### alimony_expense

**Label**: Alimony expense
**Entity**: person
**Period**: year
**Unit**: currency-USD

### alimony_expense_ald

**Label**: Alimony expense ALD
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Above-the-line deduction from gross income for alimony expenses.

**References**:
- https://www.irs.gov/taxtopics/tc452

### alimony_income

**Label**: Alimony income
**Entity**: person
**Period**: year
**Unit**: currency-USD

### alternative_minimum_tax

**Label**: Alternative Minimum Tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Alternative Minimum Tax (AMT) liability

### ambulance_expense

**Label**: Ambulance expenses
**Entity**: person
**Period**: year
**Unit**: currency-USD

### american_opportunity_credit

**Label**: American Opportunity Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Total value of the American Opportunity Credit

**References**:
- https://www.law.cornell.edu/uscode/text/26/25A#b

### ami

**Label**: Area median income
**Entity**: household
**Period**: year

Area median income for a four-person household

### amt_base_tax

**Label**: Alternative Minimum Tax base tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Alternative Minimum Tax (AMT) base tax, Form 6251 Part II Line 7 'All Others'

**References**:
- https://www.irs.gov/pub/irs-pdf/f6251.pdf

### amt_excluded_deductions

**Label**: AMT taxable income excluded deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/55#b_2

### amt_foreign_tax_credit

**Label**: AMT foreign tax credit from Form 6251
**Entity**: person
**Period**: year
**Unit**: currency-USD

### amt_form_completed

**Label**: AMT form completed
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### amt_higher_base_tax

**Label**: Alternative Minimum Tax higher base tax amount
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Alternative Minimum Tax (AMT) base tax, Form 6251 Part II Line 7 'All Others' - higher bracket

**References**:
- https://www.irs.gov/pub/irs-pdf/f6251.pdf

### amt_income

**Label**: AMT taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/56

### amt_income_less_exemptions

**Label**: Alternative Minimum Tax Income less exemptions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Alternative Minimum Tax (AMT) income less exemptions

### amt_kiddie_tax_applies

**Label**: Alternative Minimum Tax kiddie tax applies
**Entity**: tax_unit
**Period**: year

Whether the kiddie tax applies to the tax unit

### amt_lower_base_tax

**Label**: Alternative Minimum Tax lower base tax amount
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Alternative Minimum Tax (AMT) base tax, Form 6251 Part II Line 7 'All Others' - lower bracket

**References**:
- https://www.irs.gov/pub/irs-pdf/f6251.pdf

### amt_non_agi_income

**Label**: Income considered for AMT but not AGI
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### amt_part_iii_required

**Label**: Alternative Minimum Tax Part III required
**Entity**: tax_unit
**Period**: year

Whether the Alternative Minimum Tax (AMT) Part III worksheet is required, Form 6251, Part III

**References**:
- https://www.irs.gov/pub/irs-pdf/f6251.pdf

### amt_separate_addition

**Label**: AMT taxable income separate addition
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/55#b_2

### amt_tax_including_cg

**Label**: Alternative Minimum Tax computed using the capital gains rates
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Alternative Minimum Tax (AMT) liability computed using the capital gains rates, Form 6251, Part III

**References**:
- https://www.irs.gov/pub/irs-pdf/f6251.pdf

### ar_agi

**Label**: Arkansas adjusted gross income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ar_agi_indiv

**Label**: Arkansas adjusted gross income for each individual
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=22

### ar_agi_joint

**Label**: Arkansas adjusted gross income for each individual
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=22

### ar_capped_retirement_or_disability_benefits_exemption_person

**Label**: Arkansas capped individual retirement or disability benefits exemption
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=13

### ar_cdcc

**Label**: Arkansas Child and Dependent Care Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

https://codes.findlaw.com/ar/title-26-taxation/ar-code-sect-26-51-502/

### ar_deduction_indiv

**Label**: Arkansas deduction when married couples are filing separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=14

### ar_deduction_joint

**Label**: Arkansas deduction when married filing jointly
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=14

### ar_exemptions

**Label**: Arkansas exemptions from income tax for each individual
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=10

### ar_files_separately

**Label**: married couple files separately on the Arkansas tax return
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2023_AR1000F_and_AR1000NR_Instructions.pdfhttps://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2023_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdf

### ar_gross_income_indiv

**Label**: Arkansas gross income when married filing separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://casetext.com/statute/arkansas-code-of-1987/title-26-taxation/subtitle-5-state-taxes/chapter-51-income-taxes/subchapter-4-computation-of-tax-liability/section-26-51-404-gross-income-generally

### ar_gross_income_joint

**Label**: Arkansas gross income when married filing jointly
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://casetext.com/statute/arkansas-code-of-1987/title-26-taxation/subtitle-5-state-taxes/chapter-51-income-taxes/subchapter-4-computation-of-tax-liability/section-26-51-404-gross-income-generally

### ar_income_tax

**Label**: Arkansas income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ar_income_tax_before_non_refundable_credits_indiv

**Label**: Arkansas income tax before non refundable credits when married couples are filing separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2023_AR1000F_and_AR1000NR_Instructions.pdfhttps://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2023_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdf

### ar_income_tax_before_non_refundable_credits_joint

**Label**: Arkansas income tax before non refundable credits when married filing jointly
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2023_AR1000F_and_AR1000NR_Instructions.pdfhttps://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2023_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdf

### ar_income_tax_before_non_refundable_credits_unit

**Label**: Arkansas income tax before non refundable credits combined
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2023_AR1000F_and_AR1000NR_Instructions.pdfhttps://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2023_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdf

### ar_income_tax_before_refundable_credits

**Label**: Arkansas income tax before refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ar_inflation_relief_credit

**Label**: Arkansas inflation relief income-tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ar_inflation_relief_credit_person

**Label**: Arkansas inflation relief income-tax credit for each individual
**Entity**: person
**Period**: year
**Unit**: currency-USD

### ar_itemized_deductions

**Label**: Arkansas itemized deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ar_itemized_deductions_indiv

**Label**: Arkansas itemized deductions when married couples are filing separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR3_ItemizedDeduction.pdf

### ar_itemized_deductions_joint

**Label**: Arkansas itemized deductions when married filing jointly
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR3_ItemizedDeduction.pdf

### ar_low_income_tax_joint

**Label**: Arkansas low income tax when married couples are filing separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=29

### ar_medical_expense_deduction_indiv

**Label**: Arkansas medical and dental expense deduction when married filing separately
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=21

### ar_medical_expense_deduction_joint

**Label**: Arkansas medical and dental expense deduction when married filing jointly
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=21

### ar_military_retirement_income_person

**Label**: Arkansas military retirement income for each person
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=13

### ar_misc_deduction_indiv

**Label**: Arkansas miscellaneous deduction when married filing separately
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/AR1075_2022.pdf#page=1

### ar_misc_deduction_joint

**Label**: Arkansas miscellaneous deduction when married filing jointly
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/AR1075_2022.pdf#page=1

### ar_non_refundable_credits

**Label**: Arkansas non-refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ar_personal_credit_dependent

**Label**: Arkansas personal tax credit dependent amount
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2021_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdfhttps://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdf#page=1https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=12

### ar_personal_credit_disabled_dependent

**Label**: Arkansas disabled dependent personal tax credit amount
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2021_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdfhttps://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdf#page=1https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=12

### ar_personal_credits

**Label**: Arkansas personal credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2021_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdfhttps://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdf#page=1https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=12

### ar_personal_credits_base

**Label**: Arkansas base personal credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2021_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdfhttps://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdf#page=1https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=12

### ar_post_secondary_education_tuition_deduction

**Label**: Arkansas post-secondary education tuition deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/AR1075_2022.pdf#page=1

### ar_post_secondary_education_tuition_deduction_person

**Label**: Arkansas person post-secondary education tuition deduction
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/AR1075_2022.pdf#page=1

### ar_refundable_credits

**Label**: Arkansas refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ar_retirement_or_disability_benefits_exemption

**Label**: Arkansas retirement or disability benefits exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=13

### ar_retirement_or_disability_benefits_exemption_person

**Label**: Arkansas individual retirement or disability benefits exemption
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=13

### ar_standard_deduction

**Label**: Arkansas standard deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ar_standard_deduction_indiv

**Label**: Arkansas standard deduction when married couples are filing separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=14

### ar_standard_deduction_joint

**Label**: Arkansas standard deduction when married filing jointly
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=14

### ar_tax_unit_itemizes

**Label**: Whether the tax unit in Arkansas itemizes the deductions when married filing separately
**Entity**: tax_unit
**Period**: year

### ar_taxable_capital_gains_indiv

**Label**: Arkansas taxable capital gains when married filing separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://codes.findlaw.com/ar/title-26-taxation/ar-code-sect-26-51-815.html
- https://www.taxformfinder.org/forms/2023/2023-arkansas-form-ar1000d.pdf#page=1

### ar_taxable_capital_gains_joint

**Label**: Arkansas taxable capital gains when married filing jointly
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://codes.findlaw.com/ar/title-26-taxation/ar-code-sect-26-51-815.html
- https://www.taxformfinder.org/forms/2023/2023-arkansas-form-ar1000d.pdf#page=1

### ar_taxable_income

**Label**: Arkansas taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ar_taxable_income_indiv

**Label**: Arkansas taxable income when married couples are filing separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdfhttps://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdf

### ar_taxable_income_joint

**Label**: Arkansas taxable income when married filing jointly
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdfhttps://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdf

### ar_withheld_income_tax

**Label**: Arkansas withheld income tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

### assessed_property_value

**Label**: Assessed property value
**Entity**: person
**Period**: year
**Unit**: currency-USD

Total assessed value of property owned by this person.

### auto_loan_balance

**Label**: auto loan total balance
**Entity**: household
**Period**: year
**Unit**: currency-USD

### auto_loan_interest

**Label**: auto loan interest expense
**Entity**: household
**Period**: year
**Unit**: currency-USD

### auto_loan_interest_deduction

**Label**: Auto loan interest deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.congress.gov/bill/119th-congress/house-bill/1/text

### average_home_energy_use_in_state

**Label**: Average energy use per in state
**Entity**: household
**Period**: year

Average energy use per home in household's state, in kilowatt hours

### az_529_college_savings_plan_subtraction

**Label**: Arizona 529 college savings plan subtraction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

https://azdor.gov/sites/default/files/2023-03/FORMS_INDIVIDUAL_2022_140i.pdf#page=15

### az_additions

**Label**: Arizona additions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### az_aged_exemption

**Label**: Arizona aged exemption
**Entity**: person
**Period**: year
**Unit**: currency-USD

### az_aged_exemption_eligible_person

**Label**: Eligible person for the Arizona aged exemption
**Entity**: person
**Period**: year
**Unit**: currency-USD

### az_agi

**Label**: Arizona adjusted gross income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

https://azdor.gov/sites/default/files/2023-03/FORMS_INDIVIDUAL_2020_140NRBOOKLET.pdf#page=18

### az_base_standard_deduction

**Label**: Arizona base standard deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

https://www.azleg.gov/viewdocument/?docName=https://www.azleg.gov/ars/43/01041.htm

### az_blind_exemption

**Label**: Arizona blind exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### az_charitable_contributions_credit

**Label**: Arizona charitable contributions credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/arizona/2022/title-43/section-43-1088/

### az_charitable_contributions_to_qualifying_charitable_organizations

**Label**: Charitable contributions to qualifying charitable organizations in Arizona
**Entity**: tax_unit
**Period**: year

**References**:
- https://law.justia.com/codes/arizona/2022/title-43/section-43-1088/

### az_charitable_contributions_to_qualifying_foster_care_organizations

**Label**: Charitable contributions to qualifying foster care organizations in Arizona
**Entity**: tax_unit
**Period**: year

**References**:
- https://law.justia.com/codes/arizona/2022/title-43/section-43-1088/

### az_deductions

**Label**: Arizona deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://azdor.gov/sites/default/files/2023-08/FORMS_INDIVIDUAL_2022_140f.pdf

### az_dependent_tax_credit

**Label**: Arizona dependent tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

https://www.azleg.gov/viewdocument/?docName=https://www.azleg.gov/ars/43/01073-01.htm

### az_exemptions

**Label**: Arizona total exemptions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### az_family_tax_credit

**Label**: Arizona Family Tax Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### az_family_tax_credit_eligible

**Label**: Eligible for the Arizona Family Tax Credit
**Entity**: tax_unit
**Period**: year

### az_filing_status

**Label**: Arizona filing status
**Entity**: tax_unit
**Period**: year

https://www.azleg.gov/viewdocument/?docName=https://www.azleg.gov/ars/43/01001.htmhttps://azdor.gov/forms/individual/form-140a-arizona-resident-personal-income-tax-booklet

### az_income_tax

**Label**: Arizona income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### az_income_tax_before_non_refundable_credits

**Label**: Arizona income tax before non-refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### az_income_tax_before_refundable_credits

**Label**: Arizona income tax before refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### az_increased_excise_tax_credit

**Label**: Arizona Increased Excise Tax Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.azleg.gov/viewdocument/?docName=https://www.azleg.gov/ars/43/01072-01.htm

### az_increased_excise_tax_credit_eligible

**Label**: Eligible for Arizona Increased Excise Tax Credit
**Entity**: tax_unit
**Period**: year

**References**:
- https://www.azleg.gov/viewdocument/?docName=https://www.azleg.gov/ars/43/01072-01.htm

### az_increased_standard_deduction_for_charitable_contributions

**Label**: Arizona increased standard deduction for charitable contributions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

https://www.azleg.gov/viewdocument/?docName=https://www.azleg.gov/ars/43/01041.htm

### az_itemized_deductions

**Label**: Arizona Itemized Deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Arizona Form 140 Schedule A

**References**:
- https://law.justia.com/codes/arizona/2022/title-43/section-43-1042/
- https://azdor.gov/forms/individual/itemized-deduction-adjustments-form
- https://azdor.gov/forms/individual/form-140-resident-personal-income-tax-form-calculating

### az_long_term_capital_gains_subtraction

**Label**: Arizona long-term capital gains subtraction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

https://azdor.gov/sites/default/files/2023-03/FORMS_INDIVIDUAL_2022_140i.pdf#page=31

### az_military_retirement_subtraction

**Label**: Arizona military retirement subtraction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.azleg.gov/ars/43/01022.htm
- https://azdor.gov/sites/default/files/2023-03/FORMS_INDIVIDUAL_2022_140BOOKLET.pdf#page=25
- https://azdor.gov/sites/default/files/2023-03/FORMS_INDIVIDUAL_2021_140BOOKLET.pdf#page=27

### az_non_refundable_credits

**Label**: Arizona non-refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### az_parents_grandparents_exemption

**Label**: Arizona parents and grandparents exemption
**Entity**: person
**Period**: year
**Unit**: currency-USD

### az_property_tax_credit

**Label**: Arizona Property Tax Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### az_property_tax_credit_eligible

**Label**: Eligible for the Arizona Property Tax Credit
**Entity**: tax_unit
**Period**: year

**References**:
- https://www.azleg.gov/viewdocument/?docName=https://www.azleg.gov/ars/43/01072.htm

### az_property_tax_credit_income

**Label**: Income for the Arizona property tax the credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### az_public_pension_exclusion

**Label**: Arizona Pension Exclusion
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://azdor.gov/sites/default/files/2023-03/FORMS_INDIVIDUAL_2022_140BOOKLET.pdf#page=18https://azdor.gov/sites/default/files/2023-03/FORMS_INDIVIDUAL_2021_140BOOKLET.pdf#page=23https://www.azleg.gov/ars/43/01022.htm

### az_refundable_credits

**Label**: Arizona refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### az_standard_deduction

**Label**: Arizona standard deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

https://www.azleg.gov/viewdocument/?docName=https://www.azleg.gov/ars/43/01041.htm

### az_stillborn_exemption

**Label**: Arizona stillborn exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### az_subtractions

**Label**: Arizona subtractions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### az_tanf_eligible_child

**Label**: Eligible child for the Arizona Cash Assistance
**Entity**: person
**Period**: year

### az_taxable_income

**Label**: Arizona taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

https://azdor.gov/sites/default/files/2023-03/FORMS_INDIVIDUAL_2022_140Ai.pdf#page=8https://azdor.gov/sites/default/files/2023-03/FORMS_INDIVIDUAL_2022_140Ai.pdf#page=8

### az_withheld_income_tax

**Label**: Arizona withheld income tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

### basic_income

**Label**: basic income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Total basic income payments for this filer.

### basic_income_before_phase_out

**Label**: Basic income before phase-outs
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### basic_income_eligible

**Label**: Basic income eligible
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Eligible for basic income payments based on adjusted gross income.

### basic_income_phase_in

**Label**: Basic income phase-in
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### basic_income_phase_out

**Label**: Basic income phase-out
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### basic_standard_deduction

**Label**: Basic standard deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/63#c_2

### bedrooms

**Label**: Bedrooms
**Entity**: household
**Period**: year

### biomass_stove_boiler_expenditures

**Label**: Expenditures on biomass stoves and boilers
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=339#342

### birth_year

**Label**: Birth year
**Entity**: person
**Period**: year
**Unit**: year

### blind_head

**Label**: Tax unit head is blind
**Entity**: tax_unit
**Period**: year

### blind_spouse

**Label**: Tax unit spouse is blind
**Entity**: tax_unit
**Period**: year

### bonus_guaranteed_deduction

**Label**: Bonus guaranteed deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://waysandmeans.house.gov/malliotakis-steel-lead-legislation-to-provide-tax-relief-to-working-families/

### bottled_gas_expense

**Label**: Bottled gas expense
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### broadband_cost

**Label**: Broadband cost
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### broadband_cost_after_lifeline

**Label**: Broadband costs after Lifeline
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

Broadband costs after Lifeline benefits

**References**:
- https://www.law.cornell.edu/cfr/text/47/54.403

### business_is_qualified

**Label**: Business is qualified
**Entity**: person
**Period**: year
**Unit**: currency-USD

Whether all income from self-employment, partnerships and S-corporations is from qualified businesses. A qualified trade or business is any trade or business other than a specified service trade or business, or employment. The list of specified service trades can be found at https://www.law.cornell.edu/uscode/text/26/1202#e_3_A.

**References**:
- https://www.law.cornell.edu/uscode/text/26/199A#d_1

### business_is_sstb

**Label**: Business is SSTB
**Entity**: person
**Period**: year
**Unit**: currency-USD

Whether all income from self-employment, partnerships and S-corporations is from qualified businesses. A qualified trade or business is any specified service trade or business, or employment. The list of specified service trades can be found at https://www.law.cornell.edu/uscode/text/26/1202#e_3_A.

**References**:
- https://www.law.cornell.edu/uscode/text/26/199A#d_1

### ca_additions

**Label**: CA AGI additions to federal AGI
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ftb.ca.gov/forms/2021/2021-540.pdf

### ca_agi

**Label**: CA AGI
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ftb.ca.gov/forms/2021/2021-540.pdfhttps://www.ftb.ca.gov/forms/2022/2022-540.pdf

### ca_agi_subtractions

**Label**: CA AGI subtractions from federal AGI
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ftb.ca.gov/forms/2021/2021-540-ca-instructions.htmlhttps://www.ftb.ca.gov/forms/2022/2022-540-ca-instructions.html

### ca_amt

**Label**: California alternative minimum tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ftb.ca.gov/forms/2022/2022-540-p.pdf

### ca_amt_exemption

**Label**: California AMT exemption amount
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ftb.ca.gov/forms/2022/2022-540-p-instructions.html

### ca_amti

**Label**: California alternative minimum taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ftb.ca.gov/forms/2022/2022-540-p.pdf

### ca_amti_adjustments

**Label**: California AMTI adjustment
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ftb.ca.gov/forms/2022/2022-540-p.pdf

### ca_calworks_child_care

**Label**: California CalWORKs Child Care final payment
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

### ca_calworks_child_care_age_eligible

**Label**: California CalWORKs Child Care SPMUnit Age Eligibility
**Entity**: spm_unit
**Period**: year

**References**:
- http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FChild%20Care%2FChild_Care%2F1210_Overview%2F1210_Overview.htm%23Backgroundbc-3&rhtocid=_3_3_0_2

### ca_calworks_child_care_child_age_eligible

**Label**: Eligible child for the California CalWORKs Child Care based on age
**Entity**: person
**Period**: year

**References**:
- http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FChild%20Care%2FChild_Care%2F1210_Overview%2F1210_Overview.htm%23Backgroundbc-3&rhtocid=_3_3_0_2

### ca_calworks_child_care_days_per_month

**Label**: California CalWORKs Child Care days per month
**Entity**: person
**Period**: month

### ca_calworks_child_care_eligible

**Label**: Eligible for the California CalWORKs Child Care
**Entity**: spm_unit
**Period**: year

**References**:
- http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FChild%20Care%2FChild_Care%2F1210_Overview%2F1210_Overview.htm%23Backgroundbc-3&rhtocid=_3_3_0_2

### ca_calworks_child_care_factor_category

**Label**: California CalWORKs Child Care factor category
**Entity**: person
**Period**: month

**References**:
- http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FChild%20Care%2FChild_Care%2F1210_8_Regional_Market_Rate_Ceilings%2F1210_8_Regional_Market_Rate_Ceilings.htm%23Referencesbc-11&rhtocid=_3_3_8_10

### ca_calworks_child_care_full_time

**Label**: Whether a child is classified as receiving full-time care for CalWORKs Child Care
**Entity**: person
**Period**: month

**References**:
- http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FChild%20Care%2FChild_Care%2F1210_8_Regional_Market_Rate_Ceilings%2F1210_8_Regional_Market_Rate_Ceilings.htm%23Contactbc-13&rhtocid=_3_3_8_12

### ca_calworks_child_care_immigration_status_eligible_person

**Label**: California CalWORKs Child Care immigration status Eligibility
**Entity**: person
**Period**: year

**References**:
- http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FChild%20Care%2FChild_Care%2F1210_Overview%2F1210_Overview.htm%23Backgroundbc-3&rhtocid=_3_3_0_2

### ca_calworks_child_care_meets_work_requirement

**Label**: Meets CalWORKs Child Care Work Requirement
**Entity**: spm_unit
**Period**: year

**References**:
- http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FChild%20Care%2FChild_Care%2F1210_Overview%2F1210_Overview.htm%23Backgroundbc-3&rhtocid=_3_3_0_2

### ca_calworks_child_care_payment

**Label**: California CalWORKs Child Care payment
**Entity**: person
**Period**: month
**Unit**: currency-USD

### ca_calworks_child_care_payment_factor

**Label**: California CalWORKs Child Care payment factor
**Entity**: person
**Period**: month

**References**:
- http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FChild%20Care%2FChild_Care%2F1210_8_Regional_Market_Rate_Ceilings%2F1210_8_Regional_Market_Rate_Ceilings.htm%23Referencesbc-11&rhtocid=_3_3_8_10

### ca_calworks_child_care_payment_standard

**Label**: California CalWORKs Child Care Payment Standard
**Entity**: person
**Period**: month
**Unit**: currency-USD

**References**:
- http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FChild%20Care%2FChild_Care%2F1210_8_Regional_Market_Rate_Ceilings%2F1210_8_Regional_Market_Rate_Ceilings.htm%23Contactbc-13&rhtocid=_3_3_8_12

### ca_calworks_child_care_provider_category

**Label**: California CalWORKs Child Care provider categroy
**Entity**: person
**Period**: month

**References**:
- http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FChild%20Care%2FChild_Care%2F1210_8_Regional_Market_Rate_Ceilings%2F1210_8_Regional_Market_Rate_Ceilings.htm%23Contactbc-13&rhtocid=_3_3_8_12

### ca_calworks_child_care_time_category

**Label**: California CalWORKs Child Care time category
**Entity**: person
**Period**: month

**References**:
- http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FChild%20Care%2FChild_Care%2F1210_8_Regional_Market_Rate_Ceilings%2F1210_8_Regional_Market_Rate_Ceilings.htm%23Contactbc-13&rhtocid=_3_3_8_12

### ca_calworks_child_care_time_coefficient

**Label**: California CalWORKs Child Care hours per month
**Entity**: person
**Period**: month

**References**:
- http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FChild%20Care%2FChild_Care%2F1210_8_Regional_Market_Rate_Ceilings%2F1210_8_Regional_Market_Rate_Ceilings.htm%23Contactbc-13&rhtocid=_3_3_8_12

### ca_calworks_child_care_weeks_per_month

**Label**: California CalWORKs Child Care weeks per month
**Entity**: person
**Period**: month

### ca_calworks_child_care_welfare_to_work

**Label**: California CalWORKs Welfare to Work
**Entity**: person
**Period**: year
**Unit**: hour

**References**:
- http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FChild%20Care%2FChild_Care%2F1210_Overview%2F1210_Overview.htm%23Backgroundbc-3&rhtocid=_3_3_0_2
- https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=11322.6.

### ca_capi

**Label**: California CAPI
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.cdss.ca.gov/Portals/9/CAPI/CAPI_Regulations-Accessible.pdf

### ca_capi_countable_vehicle_value

**Label**: California CAPI countable vehicle value
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.cdss.ca.gov/Portals/9/CAPI/CAPI_Regulations-Accessible.pdf

### ca_capi_eligible

**Label**: California CAPI eligible
**Entity**: spm_unit
**Period**: year

**References**:
- https://www.cdss.ca.gov/Portals/9/CAPI/CAPI_Regulations-Accessible.pdf

### ca_capi_eligible_person

**Label**: California CAPI eligible person
**Entity**: person
**Period**: year

**References**:
- https://www.cdss.ca.gov/Portals/9/CAPI/CAPI_Regulations-Accessible.pdf

### ca_capi_income_eligible

**Label**: California CAPI income eligible
**Entity**: spm_unit
**Period**: year

**References**:
- https://www.cdss.ca.gov/Portals/9/CAPI/CAPI_Regulations-Accessible.pdf

### ca_capi_resource_eligible

**Label**: California CAPI resource eligible
**Entity**: spm_unit
**Period**: year

**References**:
- https://www.cdss.ca.gov/Portals/9/CAPI/CAPI_Regulations-Accessible.pdf

### ca_capi_resources

**Label**: California CAPI resources
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.cdss.ca.gov/Portals/9/CAPI/CAPI_Regulations-Accessible.pdf

### ca_care

**Label**: California CARE
**Entity**: household
**Period**: year
**Unit**: currency-USD

California's CARE program provides this electricity discount to eligible households.

**References**:
- https://www.cpuc.ca.gov/industries-and-topics/electrical-energy/electric-costs/care-fera-program

### ca_care_amount_if_eligible

**Label**: California CARE amount discounted
**Entity**: household
**Period**: year
**Unit**: currency-USD

California's CARE program provides this electricity discount to eligible households.

**References**:
- https://www.cpuc.ca.gov/industries-and-topics/electrical-energy/electric-costs/care-fera-program

### ca_care_categorically_eligible

**Label**: Eligible for California CARE program by virtue of participation in a qualifying program
**Entity**: household
**Period**: year

Eligible for California Alternate Rates for Energy

**References**:
- https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=PUC&sectionNum=739.1

### ca_care_eligible

**Label**: Eligible for California CARE program
**Entity**: household
**Period**: year

Eligible for California Alternate Rates for Energy

**References**:
- https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=PUC&sectionNum=739.1

### ca_care_income_eligible

**Label**: Eligible for California CARE program by virtue of income
**Entity**: household
**Period**: year

Eligible for California Alternate Rates for Energy

**References**:
- https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=PUC&sectionNum=739.1

### ca_care_poverty_line

**Label**: Poverty line as defined for California CARE program
**Entity**: household
**Period**: year
**Unit**: currency-USD

**References**:
- https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=PUC&sectionNum=739.1

### ca_cdcc

**Label**: California Child and Dependent Care Expenses Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

https://www.ftb.ca.gov/forms/2020/2020-3506-instructions.html

### ca_cdcc_rate

**Label**: CDCC credit rate replicated to include California limitations
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ftb.ca.gov/about-ftb/data-reports-plans/Summary-of-Federal-Income-Tax-Changes/index.html#PL-117-2-9631

### ca_cdcc_relevant_expenses

**Label**: CDCC-relevant care expenses replicated to include California limitations
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ftb.ca.gov/about-ftb/data-reports-plans/Summary-of-Federal-Income-Tax-Changes/index.html#PL-117-2-9631

### ca_child_care_subsidies

**Label**: California child care subsidies
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### ca_cvrp

**Label**: California Clean Vehicle Rebate Project
**Entity**: person
**Period**: year
**Unit**: currency-USD

Total California Clean Vehicle Rebate Project (CVRP) benefit

**References**:
- https://cleanvehiclerebate.org/en/eligibility-guidelines

### ca_cvrp_vehicle_rebate_amount

**Label**: CVRP rebate for purchased vehicle
**Entity**: person
**Period**: year
**Unit**: currency-USD

Rebate value for a purchased vehicle under the California Clean Vehicle Rebate Project (CVRP)

**References**:
- https://cleanvehiclerebate.org/en/eligible-vehicles

### ca_deductions

**Label**: California deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ftb.ca.gov/forms/2021/2021-540.pdfhttps://www.ftb.ca.gov/forms/2022/2022-540.pdf

### ca_eitc

**Label**: CalEITC
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ca_eitc_eligible

**Label**: CalEITC eligible
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ca_exemptions

**Label**: CA Exemptions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ftb.ca.gov/forms/2021/2021-540.pdf

### ca_federal_capped_cdcc

**Label**: Capped child/dependent care credit replicated to include California limitations
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ftb.ca.gov/forms/2020/2020-3506-instructions.html

### ca_federal_cdcc

**Label**: Child and Dependent Care Expenses Credit replicated to include California limitations
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

https://www.ftb.ca.gov/about-ftb/data-reports-plans/Summary-of-Federal-Income-Tax-Changes/index.html#PL-117-2-9631

### ca_fera

**Label**: California FERA
**Entity**: household
**Period**: year
**Unit**: currency-USD

California's FERA program provides this electricity discount to eligible households.

**References**:
- https://www.cpuc.ca.gov/industries-and-topics/electrical-energy/electric-costs/care-fera-program

### ca_fera_amount_if_eligible

**Label**: California FERA discounted amount
**Entity**: household
**Period**: year
**Unit**: currency-USD

California's CARE program provides this electricity discount to eligible households.

**References**:
- https://www.cpuc.ca.gov/industries-and-topics/electrical-energy/electric-costs/care-fera-program

### ca_fera_eligible

**Label**: Eligible for California FERA program
**Entity**: household
**Period**: year

Eligible for California Alternate Rates for Energy

**References**:
- https://www.cpuc.ca.gov/industries-and-topics/electrical-energy/electric-costs/care-fera-program
- https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=PUC&sectionNum=739.12

### ca_ffyp_eligible

**Label**: Eligible person for the California Former Foster Youth Program
**Entity**: person
**Period**: year

**References**:
- https://www.dhcs.ca.gov/services/medi-cal/eligibility/Pages/FFY_Bene.aspx
- https://www.dhcs.ca.gov/formsandpubs/forms/Forms/MCED/MC_Forms/MC250A_Eng.pdf

### ca_foster_care_minor_dependent

**Label**: California foster care minor dependent
**Entity**: person
**Period**: month

### ca_foster_youth_tax_credit

**Label**: California foster youth tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ca_foster_youth_tax_credit_eligible_person

**Label**: Eligible person for the California foster youth tax credit
**Entity**: person
**Period**: year

**References**:
- https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=17052.2.

### ca_foster_youth_tax_credit_person

**Label**: California foster youth tax credit
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ftb.ca.gov/forms/2022/2022-3514.pdf#page=4

### ca_in_home_supportive_services

**Label**: California In-Home Supportive Services
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.cdss.ca.gov/in-home-supportive-services

### ca_in_medical_care_facility

**Label**: Is in a California medical care facility
**Entity**: person
**Period**: year

### ca_income_tax

**Label**: CA income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ftb.ca.gov/forms/Search/Home/Confirmation

### ca_income_tax_before_credits

**Label**: CA income tax before credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ftb.ca.gov/forms/Search/Home/Confirmation

### ca_income_tax_before_refundable_credits

**Label**: CA income tax before refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ftb.ca.gov/forms/Search/Home/Confirmation

### ca_investment_interest_deduction

**Label**: California investment interest deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ftb.ca.gov/forms/2021/2021-3526.pdfhttps://law.justia.com/codes/california/2022/code-rtc/division-2/part-11/chapter-7/article-1/section-24344/

### ca_is_qualifying_child_for_caleitc

**Label**: Child qualifies for CalEITC
**Entity**: person
**Period**: year

**References**:
- https://www.ftb.ca.gov/file/personal/credits/EITC-calculator/Help/QualifyingChildren

### ca_itemized_deductions

**Label**: California itemized deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ftb.ca.gov/forms/2021/2021-540-ca-instructions.htmlhttps://www.ftb.ca.gov/forms/2022/2022-540-ca-instructions.html

### ca_itemized_deductions_pre_limitation

**Label**: California pre-limitation itemized deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ftb.ca.gov/forms/2021/2021-540-ca-instructions.htmlhttps://www.ftb.ca.gov/forms/2022/2022-540-ca-instructions.html

### ca_la_expectant_parent_payment

**Label**: Los Angeles County expectant parent payment
**Entity**: person
**Period**: month

### ca_la_expectant_parent_payment_eligible

**Label**: Eligible for the Los Angeles County expectant parent payment
**Entity**: person
**Period**: month

### ca_la_ez_save

**Label**: Los Angeles County EZ Save program
**Entity**: household
**Period**: month

### ca_la_ez_save_countable_income

**Label**: Los Angeles County EZ Save program countable income
**Entity**: household
**Period**: year

### ca_la_ez_save_eligible

**Label**: Eligible for the Los Angeles County EZ Save program
**Entity**: household
**Period**: month

### ca_la_ez_save_fpg

**Label**: Los Angeles County EZ save federal poverty guideline
**Entity**: household
**Period**: month
**Unit**: currency-USD

The federal poverty guideline used to determine LA ez save eligibility.

### ca_la_infant_supplement

**Label**: Los Angeles County infant supplement
**Entity**: household
**Period**: month

### ca_la_infant_supplement_eligible_person

**Label**: Eligible for the Los Angeles County infant supplement
**Entity**: person
**Period**: month

### ca_mental_health_services_tax

**Label**: CA mental health services tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ftb.ca.gov/forms/Search/Home/Confirmation

### ca_nonrefundable_credits

**Label**: California nonrefundable income tax credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ftb.ca.gov/forms/Search/Home/Confirmation

### ca_pre_exemption_amti

**Label**: California pre-exemption alternative minimum taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ftb.ca.gov/forms/2022/2022-540-p.pdf

### ca_refundable_credits

**Label**: California refundable income tax credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ftb.ca.gov/forms/Search/Home/Confirmation

### ca_renter_credit

**Label**: California Renter Tax Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

https://casetext.com/statute/california-codes/california-revenue-and-taxation-code/division-2-other-taxes/part-10-personal-income-tax/chapter-2-imposition-of-tax/section-170535-credit-for-qualified-renter

### ca_riv_liheap_countable_income

**Label**: Riverside County Low Income Home Energy Assistance Program (LIHEAP) countable income
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://capriverside.org/sites/g/files/aldnop136/files/2024-12/2025%20LIHEAP%20CAP%20APPLICATION%20ENGLISH.pdf#page=3

### ca_riv_liheap_eligible

**Label**: Eligible for the California Riverside County LIHEAP
**Entity**: spm_unit
**Period**: year

**References**:
- https://capriverside.org/utility-assistance-program

### ca_riv_share_countable_income

**Label**: Riverside County Sharing Households Assist Riverside's Energy program (SHARE) countable income
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://riversideca.gov/utilities/residents/assistance-programs/share-english

### ca_riv_share_electricity_emergency_payment

**Label**: Riverside County Sharing Households Assist Riverside's Energy program (SHARE) electric emergency payment
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://riversideca.gov/utilities/residents/assistance-programs/share-english

### ca_riv_share_eligible

**Label**: Eligible for the Riverside County Sharing Households Assist Riverside's Energy program (SHARE)
**Entity**: spm_unit
**Period**: month

**References**:
- https://riversideca.gov/utilities/residents/assistance-programs/share-english

### ca_riv_share_eligible_for_emergency_payment

**Label**: SPM Unit has urgent notice and/or disconnection notice under Riverside County SHARE program
**Entity**: spm_unit
**Period**: month

**References**:
- https://riversideca.gov/utilities/residents/assistance-programs/share-english

### ca_riv_share_payment

**Label**: Riverside County Sharing Households Assist Riverside's Energy program (SHARE) payment
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://riversideca.gov/utilities/residents/assistance-programs/share-english

### ca_sf_wftc

**Label**: San Francisco Working Families Tax Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.sfhsa.org/sites/default/files/media/document/2024-01/form_wfc_english_1.26.24.pdf#page=4

### ca_standard_deduction

**Label**: California standard deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

https://www.ftb.ca.gov/forms/2021/2021-540.pdf

### ca_state_disability_insurance

**Label**: California state disability insurance (SDI)
**Entity**: person
**Period**: year
**Unit**: currency-USD

### ca_state_supplement

**Label**: California state supplement
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=12200

### ca_state_supplement_aged_blind_disabled_amount

**Label**: California SSI state supplement aged disabled and blind amount
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=12200

### ca_state_supplement_aged_disabled_amount

**Label**: California SSI state supplement aged disabled amount
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=12200

### ca_state_supplement_aged_disabled_count

**Label**: California SSI state supplement aged or disabled count
**Entity**: spm_unit
**Period**: month

**References**:
- https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=12200

### ca_state_supplement_blind_amount

**Label**: California SSI state supplement blind amount
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=12200

### ca_state_supplement_dependent_amount

**Label**: California SSI state supplement dependent amount
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=12200

### ca_state_supplement_eligible_person

**Label**: California SSI state supplement eligible person
**Entity**: person
**Period**: month

**References**:
- https://law.justia.com/codes/california/code-wic/division-9/part-3/chapter-3/article-4/

### ca_state_supplement_food_allowance

**Label**: California SSI state supplement food allowance
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=12200

### ca_state_supplement_food_allowance_eligible

**Label**: California SSI state supplement food allowance eligible
**Entity**: spm_unit
**Period**: month

**References**:
- https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=12200

### ca_state_supplement_medical_care_facility_amount

**Label**: California SSI state supplement medical care facility amount
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=12200

### ca_state_supplement_out_of_home_care_facility_amount

**Label**: California SSI state supplement out of home care facility amount
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=12200

### ca_state_supplement_payment_standard

**Label**: California SSI state supplement payment standard
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=12200

### ca_tanf

**Label**: California CalWORKs Cash Benefit
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### ca_tanf_applicant_financial_test

**Label**: California CalWORKs Applicant Financial Test
**Entity**: spm_unit
**Period**: year

**References**:
- http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FCalWORKs%2FCalWORKs%2F44-111_23_Earned_Income_Disregards%2F44-111_23_Earned_Income_Disregards.htm%23Policybc-2&rhtocid=_3_1_6_2_1

### ca_tanf_countable_income_applicant

**Label**: California CalWORKs Countable Income for Eligibility
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

**References**:
- http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FCalWORKs%2FCalWORKs%2F44-111_23_Earned_Income_Disregards%2F44-111_23_Earned_Income_Disregards.htm%23Policybc-2&rhtocid=_3_1_6_2_1

### ca_tanf_countable_income_recipient

**Label**: California CalWORKs countable income for payment computation
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

**References**:
- http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FCalWORKs%2FCalWORKs%2F44-111_23_Earned_Income_Disregards%2F44-111_23_Earned_Income_Disregards.htm%23Policybc-2&rhtocid=_3_1_6_2_1

### ca_tanf_db_unearned_income

**Label**: California CalWORKs Disability-Based Unearned Income
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

**References**:
- http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FCalWORKs%2FCalWORKs%2F44-101_Income_Definitions%2F44-101_Income_Definitions.htm%23Definitionsbc-4&rhtocid=_3_1_6_0_3

### ca_tanf_earned_income

**Label**: California CalWORKs gross earned income
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

**References**:
- http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FCalWORKs%2FCalWORKs%2F44-101_Income_Definitions%2F44-101_Income_Definitions.htm%23Definitionsbc-4&rhtocid=_3_1_6_0_3

### ca_tanf_eligible

**Label**: Eligible for the California CalWORKs
**Entity**: spm_unit
**Period**: year

### ca_tanf_exempt

**Label**: California CalWORKs Exempt Eligibility
**Entity**: spm_unit
**Period**: year

**References**:
- http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FCalWORKs%2FCalWORKs%2F44-315_CalWORKs_Maximum_Aid_Payment_Levels%2F44-315_CalWORKs_Maximum_Aid_Payment_Levels.htm%23Policybc-2&rhtocid=_3_1_8_4_1

### ca_tanf_financial_eligible

**Label**: California CalWORKs Financial Eligibility
**Entity**: spm_unit
**Period**: year

### ca_tanf_immigration_status_eligible_person

**Label**: California TANF immigration status Eligibility
**Entity**: person
**Period**: year

**References**:
- http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FChild%20Care%2FChild_Care%2F1210_Overview%2F1210_Overview.htm%23Backgroundbc-3&rhtocid=_3_3_0_2

### ca_tanf_income_limit

**Label**: California CalWORKs Minimum Basic Standard of Adequate Care
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

**References**:
- http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FCalWORKs%2FCalWORKs%2F44-212_Minimum_Basic_Standard_of_Adequate_Care%2F44-212_Minimum_Basic_Standard_of_Adequate_Care.htm%23Documentsbc-6&rhtocid=_3_1_7_20_5

### ca_tanf_maximum_payment

**Label**: California CalWORKs Maximum Aid Payment
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://hhsaprogramguides.sandiegocounty.gov/CalWORKS/44-300/CalWORKs_Payment_Standards/G_CalWORKs_Payment_Standards.pdf

### ca_tanf_other_unearned_income

**Label**: California CalWORKs other unearned income
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

**References**:
- http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FCalWORKs%2FCalWORKs%2F44-101_Income_Definitions%2F44-101_Income_Definitions.htm%23Definitionsbc-4&rhtocid=_3_1_6_0_3

### ca_tanf_recipient_financial_test

**Label**: California CalWORKs Recipient Financial Test
**Entity**: spm_unit
**Period**: year

**References**:
- http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FCalWORKs%2FCalWORKs%2F44-111_23_Earned_Income_Disregards%2F44-111_23_Earned_Income_Disregards.htm%23Policybc-2&rhtocid=_3_1_6_2_1

### ca_tanf_region1

**Label**: In a CalWORKs region 1 county
**Entity**: household
**Period**: year

**References**:
- http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FCalWORKs%2FCalWORKs%2F44-212_Minimum_Basic_Standard_of_Adequate_Care%2F44-212_Minimum_Basic_Standard_of_Adequate_Care.htm%23Definitionsbc-4&rhtocid=_3_1_7_20_3

### ca_tanf_resources

**Label**: California CalWORKs Resources
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

**References**:
- http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FCalWORKs%2FCalWORKs%2F42-200_Property%2F42-200_Property.htm%23Policybc-2&rhtocid=_3_1_2_0_1

### ca_tanf_resources_eligible

**Label**: Eligible for the California CalWORKs based on the available resources
**Entity**: spm_unit
**Period**: year

**References**:
- http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FCalWORKs%2FCalWORKs%2F42-200_Property%2F42-200_Property.htm%23Policybc-2&rhtocid=_3_1_2_0_1

### ca_tanf_resources_limit

**Label**: California CalWORKs Resources Limit
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

**References**:
- http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FCalWORKs%2FCalWORKs%2F42-200_Property%2F42-200_Property.htm%23Policybc-2&rhtocid=_3_1_2_0_1

### ca_tanf_vehicle_value_eligible

**Label**: Eligible child for the California CalWORKs based on the vehicle value
**Entity**: spm_unit
**Period**: year

**References**:
- http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects/CalWORKs/CalWORKs/42-215_Determining_Value_of_Property_Vehicles/42-215_Determining_Value_of_Property_Vehicles.htm

### ca_taxable_income

**Label**: CA taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ftb.ca.gov/forms/2021/2021-540.pdfhttps://www.ftb.ca.gov/forms/2022/2022-540.pdf

### ca_use_tax

**Label**: CA Use Tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.pa.gov/FormsandPublications/FormsforIndividuals/PIT/Documents/2021/2021_pa-40in.pdf#page=22

### ca_withheld_income_tax

**Label**: California withheld income tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

### ca_yctc

**Label**: California Young Child Tax Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=17052.1
- https://www.ftb.ca.gov/forms/2021/2021-3514-instructions.html
- https://www.ftb.ca.gov/forms/2021/2021-3514.pdf#page=3
- https://www.ftb.ca.gov/forms/2022/2022-3514-instructions.html
- https://www.ftb.ca.gov/forms/2022/2022-3514.pdf#page=3

### capital_gains

**Label**: Capital gains (both short-term and long-term)
**Entity**: person
**Period**: year
**Unit**: currency-USD

Net gain from disposition of property.

### capital_gains_28_percent_rate_gain

**Label**: 28-percent rate gain
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Includes collectibles and certain small business stock gains. These are taxed at a higher (28-percent) rate than other capital gains, while a proportion is excluded from taxable income.

**References**:
- {'title': '26 U.S. Code § 1(h)(4)', 'href': 'https://www.law.cornell.edu/uscode/text/26/1#h_4'}

### capital_gains_behavioral_response

**Label**: capital gains behavioral response
**Entity**: person
**Period**: year
**Unit**: currency-USD

### capital_gains_elasticity

**Label**: elasticity of capital gains realizations
**Entity**: person
**Period**: year
**Unit**: /1

### capital_gains_excluded_from_taxable_income

**Label**: Capital gains excluded from taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

This is subtracted from taxable income before applying the ordinary tax rates. Capital gains tax is calculated separately.

**References**:
- {'title': '26 U.S. Code § 1(h)(1)(A)', 'href': 'https://www.law.cornell.edu/uscode/text/26/1#h_1_A'}

### capital_gains_tax

**Label**: Maximum income tax after capital gains tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### capital_losses

**Label**: Capital losses (expressed as a non-negative number)
**Entity**: person
**Period**: year
**Unit**: currency-USD

Losses from transactions involving property.

### capped_advanced_main_air_circulating_fan_credit

**Label**: Capped advanced main air circulating fan credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Capped advanced main air circulating fan credit

**References**:
- https://www.law.cornell.edu/uscode/text/26/25C#b_3_A

### capped_cdcc

**Label**: Capped child/dependent care credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.irs.gov/pub/irs-prior/i2441--2021.pdf#page=1
- https://www.irs.gov/instructions/i2441#en_US_2022_publink1000106356
- https://www.law.cornell.edu/uscode/text/26/30D#c_2

### capped_count_cdcc_eligible

**Label**: Capped child/dependent care eligiable count
**Entity**: tax_unit
**Period**: year

**References**:
- https://www.law.cornell.edu/uscode/text/26/21#c
- https://www.law.cornell.edu/uscode/text/26/21#d_1

### capped_electric_heat_pump_clothes_dryer_rebate

**Label**: Capped electric heat pump clothes dryer rebate
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Before total high efficiency electric home rebate cap

### capped_electric_load_service_center_upgrade_rebate

**Label**: Capped electric load service center upgrade rebate
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Before total high efficiency electric home rebate cap

### capped_electric_stove_cooktop_range_or_oven_rebate

**Label**: Capped electric stove cooktop range or oven rebate
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Before total high efficiency electric home rebate cap

### capped_electric_wiring_rebate

**Label**: Capped electric wiring rebate
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Before total high efficiency electric home rebate cap

### capped_energy_efficient_central_air_conditioner_credit

**Label**: Capped energy efficient central air conditioner credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Capped energy-efficient central air conditioner expenditures

**References**:
- https://www.law.cornell.edu/uscode/text/26/25C#b_3_A

### capped_energy_efficient_door_credit

**Label**: Capped energy-efficient exterior door credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Capped energy-efficient exterior door credit

**References**:
- https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=339

### capped_energy_efficient_insulation_credit

**Label**: Capped energy efficient insulation credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Capped credit on energy-efficient insulation material

**References**:
- https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=339

### capped_energy_efficient_roof_credit

**Label**: Capped credit on energy-efficient roof credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Capped credit on energy-efficient roof materials

**References**:
- https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=339

### capped_energy_efficient_window_credit

**Label**: Capped energy efficient window credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Capped credit on energy-efficient exterior window and skylights

**References**:
- https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=339

### capped_heat_pump_heat_pump_water_heater_biomass_stove_boiler_credit

**Label**: Capped credit on heat pumps, heat pump water heaters, and biomass stoves and boilers
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Capped credit on heat pumps, heat pump water heaters, and biomass stoves and boilers

**References**:
- https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=340

### capped_heat_pump_rebate

**Label**: Capped heat pump rebate
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Before total high efficiency electric home rebate cap

### capped_heat_pump_water_heater_rebate

**Label**: Capped heat pump water heater rebate
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Before total high efficiency electric home rebate cap

### capped_home_energy_audit_credit

**Label**: Capped home energy audit credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Capped home energy audit credit

**References**:
- https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=366

### capped_insulation_air_sealing_ventilation_rebate

**Label**: Capped insulation air sealing and ventilation rebate
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Before total high efficiency electric home rebate cap

### capped_property_taxes

**Label**: Local real estate taxes limited by the federal SALT cap.
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Local real estate taxes limited by the federal SALT cap.

### capped_qualified_furnace_or_hot_water_boiler_credit

**Label**: Capped qualified furnace or hot water boiler credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Capped qualified furnace or hot water boiler credit

**References**:
- https://www.law.cornell.edu/uscode/text/26/25C#b_3_B

### care_and_support_costs

**Label**: Total costs for this person's care and support
**Entity**: person
**Period**: year
**Unit**: currency-USD

### care_and_support_payments_from_tax_filer

**Label**: Amount of payments made by the tax filer for this person's care and support
**Entity**: person
**Period**: year
**Unit**: currency-USD

### care_expenses

**Label**: Care expenses
**Entity**: person
**Period**: month
**Unit**: currency-USD

### casualty_loss

**Label**: Casualty/theft loss
**Entity**: person
**Period**: year
**Unit**: currency-USD

### casualty_loss_deduction

**Label**: Casualty loss deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ccdf_age_group

**Label**: CCDF age group
**Entity**: person
**Period**: year

**References**:
- https://ocfs.ny.gov/main/policies/external/ocfs_2019/LCM/19-OCFS-LCM-23.pdf

### ccdf_county_cluster

**Label**: County cluster for CCDF
**Entity**: household
**Period**: year

### ccdf_duration_of_care

**Label**: Child care duration of care
**Entity**: person
**Period**: year

**References**:
- https://ocfs.ny.gov/main/policies/external/ocfs_2019/LCM/19-OCFS-LCM-23.pdf#page=5

### ccdf_income

**Label**: Income
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### ccdf_income_to_smi_ratio

**Label**: Income to SMI ratio
**Entity**: spm_unit
**Period**: year

### ccdf_market_rate

**Label**: CCDF market rate
**Entity**: person
**Period**: year
**Unit**: currency-USD

### cdcc

**Label**: Child/dependent care credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/21

### cdcc_credit_limit

**Label**: Child/dependent care credit credit limit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/21

### cdcc_limit

**Label**: CDCC-relevant care expense limit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/21#c

### cdcc_potential

**Label**: Potential value of the Child/dependent care credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/21

### cdcc_rate

**Label**: CDCC credit rate
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/21#a_2

### cdcc_relevant_expenses

**Label**: CDCC-relevant care expenses
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/21#c
- https://www.law.cornell.edu/uscode/text/26/21#d_1

### charitable_cash_donations

**Label**: Charitable donations (cash)
**Entity**: person
**Period**: year
**Unit**: currency-USD

### charitable_deduction

**Label**: Charitable deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Deduction from taxable income for charitable donations.

**References**:
- https://www.law.cornell.edu/uscode/text/26/170

### charitable_deduction_for_non_itemizers

**Label**: Charitable deduction for non-itemizers
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Charitable deduction amount for non-itemizers.

**References**:
- https://www.irs.gov/newsroom/expanded-tax-benefits-help-individuals-and-businesses-give-to-charity-during-2021-deductions-up-to-600-available-for-cash-donations-by-non-itemizers

### charitable_non_cash_donations

**Label**: Charitable donations (non-cash)
**Entity**: person
**Period**: year
**Unit**: currency-USD

### child_index

**Label**: Index of child in household
**Entity**: person
**Period**: year

### child_support_expense

**Label**: Child support expense
**Entity**: person
**Period**: year
**Unit**: currency-USD

Legally mandated child support expenses.

### child_support_received

**Label**: Child support receipt
**Entity**: person
**Period**: year
**Unit**: currency-USD

Value of child support benefits received.

### childcare_days_per_week

**Label**: Child care days per week
**Entity**: person
**Period**: year
**Unit**: day

### childcare_expenses

**Label**: Child care expenses
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### childcare_hours_per_day

**Label**: Child care hours per day
**Entity**: person
**Period**: year
**Unit**: hour

### childcare_hours_per_week

**Label**: Child care hours per week
**Entity**: person
**Period**: year
**Unit**: hour

### childcare_provider_type_group

**Label**: Childcare provider type group
**Entity**: person
**Period**: year

### chip

**Label**: CHIP
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.macpac.gov/publication/chip-spending-by-state/

### chip_category

**Label**: CHIP category
**Entity**: person
**Period**: year

Category under which a person is eligible for the Children's Health Insurance Program

**References**:
- https://www.ssa.gov/OP_Home/ssact/title21/2110.htm
- https://www.medicaid.gov/medicaid/national-medicaid-chip-program-information/medicaid-childrens-health-insurance-program-basic-health-program-eligibility-levels
- https://www.kff.org/affordable-care-act/state-indicator/medicaid-and-chip-income-eligibility-limits-for-pregnant-women-as-a-percent-of-the-federal-poverty-level

### claimed_as_dependent_on_another_return

**Label**: Is claimed as a dependent elsewhere
**Entity**: person
**Period**: year

Whether the person is claimed as a dependent in another tax unit.

### claimed_ma_covid_19_essential_employee_premium_pay_program_2020

**Label**: Claimed MA COVID 19 Essential Employee Premium Pay Program for 2020
**Entity**: person
**Period**: year

**References**:
- https://www.mass.gov/info-details/covid-19-essential-employee-premium-pay-program

### cliff_evaluated

**Label**: cliff evaluated
**Entity**: person
**Period**: year

Whether this person's cliff has been simulated. If not, the cliff gap is assumed to be zero.

### cliff_gap

**Label**: cliff gap
**Entity**: person
**Period**: year
**Unit**: currency-USD

Amount of income lost if this person's employment income increased by delta amount.

### co_able_contribution_subtraction

**Label**: Colorado able contribution subtraction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.colorado.gov/sites/tax/files/documents/Book0104_2023.pdf#page=14
- https://advance.lexis.com/documentpage/?pdmfid=1000516&crid=28da6d1b-814f-4ace-b369-4a0d0233db83&config=014FJAAyNGJkY2Y4Zi1mNjgyLTRkN2YtYmE4OS03NTYzNzYzOTg0OGEKAFBvZENhdGFsb2d592qv2Kywlf8caKqYROP5&pddocfullpath=%2Fshared%2Fdocument%2Fstatutes-legislation%2Furn%3AcontentItem%3A689J-29B3-GXF6-81G9-00008-00&pdcontentcomponentid=234176&pdteaserkey=sr2&pditab=allpods&ecomp=bs65kkk&earg=sr2&prid=a5cd01c5-3332-4547-a3ff-d2bd6bcc868f

### co_additions

**Label**: Colorado additions to federal taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://casetext.com/statute/colorado-revised-statutes/title-39-taxation/specific-taxes/income-tax/article-22-income-tax/part-1-general/section-39-22-104-effective-until-official-proclamation-by-governor-income-tax-imposed-on-individuals-estates-and-trusts-single-rate-report-legislative-declaration-definitions-repeal
- https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=5
- https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2021.pdf#page=5
- https://tax.colorado.gov/individual-income-tax-guide

### co_ccap_add_on_parent_fee

**Label**: Colorado Child Care Assistance Program add on parent fee
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=41
- https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=62

### co_ccap_base_parent_fee

**Label**: Colorado Child Care Assistance Program base parent fee
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=41
- https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=62

### co_ccap_child_eligible

**Label**: Child eligibility for Colorado Child Care Assistance Program
**Entity**: person
**Period**: month

**References**:
- https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=6

### co_ccap_countable_income

**Label**: Colorado Child Care Assitance Program Countable Income
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=22

### co_ccap_eligible

**Label**: Eligible for Colorado Child Care Assistance Program
**Entity**: spm_unit
**Period**: month

**References**:
- https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=17
- https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=19
- https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=31

### co_ccap_eligible_children

**Label**: Number of children eligible for Colorado Child Care Assistance Program
**Entity**: spm_unit
**Period**: month

### co_ccap_entry_eligible

**Label**: Eligible for the entry of the Colorado Child Care Assistance Program
**Entity**: spm_unit
**Period**: month

**References**:
- https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=17
- https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=19

### co_ccap_entry_income_eligible

**Label**: Eligible for the entry of Colorado Child Care Assistance Program through income
**Entity**: spm_unit
**Period**: month

**References**:
- https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=19

### co_ccap_fpg_eligible

**Label**: Meets Colorado Child Care Assistance Program poverty-based income eligibility test
**Entity**: spm_unit
**Period**: month

**References**:
- https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=19

### co_ccap_is_in_entry_process

**Label**: Whether applicants are in the entry process of the Colorado Child Care Assistance Program
**Entity**: spm_unit
**Period**: month

### co_ccap_is_in_re_determination_process

**Label**: Whether applicants are in the re-determination process of the Colorado Child Care Assistance Program
**Entity**: spm_unit
**Period**: month

### co_ccap_parent_fee

**Label**: Colorado Child Care Assistance Program parent fee
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=41
- https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=62

### co_ccap_re_determination_eligible

**Label**: Eligible for the re-determination of the Colorado Child Care Assistance Program
**Entity**: spm_unit
**Period**: month

**References**:
- https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=31

### co_ccap_re_determination_income_eligible

**Label**: Eligible for the re-determination of Colorado Child Care Assistance Program through income
**Entity**: spm_unit
**Period**: month

**References**:
- https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=19

### co_ccap_smi

**Label**: State median income for Colorado CCAP
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

The state median income used to determine eligibility for Colorado's Child Care Assistance Program. This differs from the HHS definition by basing it on the prior year if before October, and dividing by 12.

### co_ccap_smi_eligible

**Label**: Meets Colorado Child Care Assistance Program state median income-based income eligibility test
**Entity**: spm_unit
**Period**: month

**References**:
- https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=19

### co_ccap_subsidy

**Label**: Colorado Child Care Assistance Program
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

### co_cdcc

**Label**: Colorado Child Care Expenses Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

https://advance.lexis.com/documentpage/?pdmfid=1000516&crid=d14880b7-7410-4295-bcf1-2e099e57d8f3&pdistocdocslideraccess=true&config=014FJAAyNGJkY2Y4Zi1mNjgyLTRkN2YtYmE4OS03NTYzNzYzOTg0OGEKAFBvZENhdGFsb2d592qv2Kywlf8caKqYROP5&pddocfullpath=%2Fshared%2Fdocument%2Fstatutes-legislation%2Furn%3AcontentItem%3A65HV-06G3-CGX8-050B-00008-00&pdcomponentid=234177&pdtocnodeidentifier=ABPAACAACAABAACABA&ecomp=k2vckkk&prid=e2e32763-f8fa-4832-8191-f70124d877f6https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=46

### co_charitable_contribution_subtraction

**Label**: Colorado charitable contribution subtraction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.colorado.gov/sites/tax/files/documents/DR0104AD_2022.pdf#page=1
- https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=12
- https://casetext.com/regulation/colorado-administrative-code/department-200-department-of-revenue/division-201-taxation-division/rule-1-ccr-201-2-income-tax/rule-39-22-1044m-charitable-contribution-subtraction-for-taxpayers-claiming-the-federal-standard-deduction

### co_charitable_contribution_subtraction_eligible

**Label**: Eligible for the Colorado charitable contribution subtraction
**Entity**: tax_unit
**Period**: year

**References**:
- https://tax.colorado.gov/sites/tax/files/documents/DR0104AD_2022.pdf#page=1
- https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=12
- https://casetext.com/regulation/colorado-administrative-code/department-200-department-of-revenue/division-201-taxation-division/rule-1-ccr-201-2-income-tax/rule-39-22-1044m-charitable-contribution-subtraction-for-taxpayers-claiming-the-federal-standard-deduction

### co_child_care_subsidies

**Label**: Colorado child care subsidies
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### co_chp

**Label**: Colorado Child Health Plan Plus expense savings
**Entity**: person
**Period**: year

### co_chp_eligible

**Label**: Colorado Child Health Plan Plus eligibility
**Entity**: person
**Period**: year

### co_chp_out_of_pocket_maximum

**Label**: Colorado Child Health Plan Plus out of pocket maximum
**Entity**: person
**Period**: year

### co_collegeinvest_subtraction

**Label**: Colorado collegeinvest subtraction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.colorado.gov/sites/tax/files/documents/DR0104AD_2022.pdf#page=1
- https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=12
- https://law.justia.com/codes/colorado/2022/title-39/article-22/part-1/section-39-22-104/

### co_ctc

**Label**: Colorado child tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://casetext.com/statute/colorado-revised-statutes/title-39-taxation/specific-taxes/income-tax/article-22-income-tax/part-1-general/section-39-22-129-child-tax-credit-legislative-declaration-definitions-repeal
- https://tax.colorado.gov/sites/tax/files/documents/DR_0104CN_2022.pdf#page=1
- https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=16

### co_ctc_eligible_child

**Label**: Colorado child tax credit eligible child
**Entity**: person
**Period**: year

**References**:
- https://leg.colorado.gov/sites/default/files/2023a_1112_signed.pdf#page=2

### co_ctc_eligible_children_count

**Label**: Colorado child tax credit eligible children count
**Entity**: tax_unit
**Period**: year

**References**:
- https://leg.colorado.gov/sites/default/files/2023a_1112_signed.pdf#page=2

### co_denver_homeowner_property_tax_relief

**Label**: Denver Property Tax Relief for homeowners
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://denvergov.org/files/content/public/v/37/government/agencies-departments-offices/agencies-departments-offices-directory/denver-human-services/be-supported/additional-assistance/property-tax-relief/denver-property-tax-relief-program-year-2021-rules.pdf

### co_denver_property_tax_relief

**Label**: Denver Property Tax Relief
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://denvergov.org/files/content/public/v/37/government/agencies-departments-offices/agencies-departments-offices-directory/denver-human-services/be-supported/additional-assistance/property-tax-relief/denver-property-tax-relief-program-year-2021-rules.pdf

### co_denver_property_tax_relief_homeowner_eligible

**Label**: Eligible for the homeowner Denver Property Tax Relief
**Entity**: spm_unit
**Period**: year

**References**:
- https://library.municode.com/co/denver/codes/code_of_ordinances?nodeId=TITIIREMUCO_CH53TAMIRE_ARTXIREPRTAASELLCOPROWTE_S53-492DE

### co_denver_property_tax_relief_income

**Label**: Denver Property Tax Relief income
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://denvergov.org/files/assets/public/v/2/denver-human-services/documents/property-tax-relief/dptr-instructions-2023.pdf#page=1

### co_denver_property_tax_relief_renter_eligible

**Label**: Eligible for the renter Denver Property Tax Relief
**Entity**: spm_unit
**Period**: year

**References**:
- https://library.municode.com/co/denver/codes/code_of_ordinances?nodeId=TITIIREMUCO_CH53TAMIRE_ARTXIREPRTAASELLCOPROWTE_S53-492DE

### co_denver_renter_property_tax_relief

**Label**: Denver Property Tax Relief for renters
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://denvergov.org/files/content/public/v/37/government/agencies-departments-offices/agencies-departments-offices-directory/denver-human-services/be-supported/additional-assistance/property-tax-relief/denver-property-tax-relief-program-year-2021-rules.pdf

### co_eitc

**Label**: Colorado EITC
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://leg.colorado.gov/sites/default/files/te19_colorado_earned_income_tax_credit.pdf

### co_family_affordability_credit

**Label**: Colorado Family Affordability Credit
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://leg.colorado.gov/bills/hb24-1311

### co_federal_ctc

**Label**: Child Tax Credit replicated to include the Colorado limitations
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Total value of the non-refundable and refundable portion of the Child Tax Credit.

**References**:
- https://casetext.com/statute/colorado-revised-statutes/title-39-taxation/specific-taxes/income-tax/article-22-income-tax/part-1-general/section-39-22-129-child-tax-credit-legislative-declaration-definitions-repeal
- https://tax.colorado.gov/sites/tax/files/documents/DR_0104CN_2022.pdf#page=1
- https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=16

### co_federal_ctc_child_individual_maximum

**Label**: CTC maximum amount (child) replicated to account for the Colorado state CTC child eligibility
**Entity**: person
**Period**: year
**Unit**: currency-USD

The CTC entitlement in respect of this person as a child.

**References**:
- https://casetext.com/statute/colorado-revised-statutes/title-39-taxation/specific-taxes/income-tax/article-22-income-tax/part-1-general/section-39-22-129-child-tax-credit-legislative-declaration-definitions-repeal
- https://tax.colorado.gov/sites/tax/files/documents/DR_0104CN_2022.pdf#page=1
- https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=16

### co_federal_ctc_maximum

**Label**: Maximum CTC replicated to include the Colorado limitations
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Maximum value of the Child Tax Credit, before phase-out.

**References**:
- https://casetext.com/statute/colorado-revised-statutes/title-39-taxation/specific-taxes/income-tax/article-22-income-tax/part-1-general/section-39-22-129-child-tax-credit-legislative-declaration-definitions-repeal
- https://tax.colorado.gov/sites/tax/files/documents/DR_0104CN_2022.pdf#page=1
- https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=16

### co_federal_deduction_addback

**Label**: Colorado federal deductions addback
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://casetext.com/statute/colorado-revised-statutes/title-39-taxation/specific-taxes/income-tax/article-22-income-tax/part-1-general/section-39-22-104-effective-upon-official-proclamation-by-governor-income-tax-imposed-on-individuals-estates-and-trusts-single-rate-report-legislative-declaration-definitions-repeal
- https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=5
- https://tax.colorado.gov/individual-income-tax-guide

### co_federal_deduction_addback_required

**Label**: Required to add back the Colorado federal deductions
**Entity**: tax_unit
**Period**: year

**References**:
- https://casetext.com/statute/colorado-revised-statutes/title-39-taxation/specific-taxes/income-tax/article-22-income-tax/part-1-general/section-39-22-104-effective-upon-official-proclamation-by-governor-income-tax-imposed-on-individuals-estates-and-trusts-single-rate-report-legislative-declaration-definitions-repeal
- https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=5
- https://tax.colorado.gov/individual-income-tax-guide

### co_income_qualified_senior_housing_credit

**Label**: Colorado Income Qualified Senior Housing Income Tax Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.colorado.gov/income-qualified-senior-housing-income-tax-credit
- https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=17

### co_income_qualified_senior_housing_credit_eligible

**Label**: Eligible for Colorado Income Qualified Senior Housing Income Tax Credit
**Entity**: tax_unit
**Period**: year

**References**:
- https://tax.colorado.gov/income-qualified-senior-housing-income-tax-credit
- https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=17

### co_income_tax

**Label**: Colorado income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### co_income_tax_before_non_refundable_credits

**Label**: Colorado income tax before non-refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### co_income_tax_before_refundable_credits

**Label**: Colorado income tax before refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### co_low_income_cdcc

**Label**: Colorado Low-income Child Care Expenses Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

https://casetext.com/statute/colorado-revised-statutes/title-39-taxation/specific-taxes/income-tax/article-22-income-tax/part-1-general/section-39-22-1195-child-care-expenses-tax-credit-legislative-declaration-definitionshttps://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=46

### co_low_income_cdcc_eligible

**Label**: Eligible for the Colorado Low-income Child Care Expenses Credit
**Entity**: tax_unit
**Period**: year

https://casetext.com/statute/colorado-revised-statutes/title-39-taxation/specific-taxes/income-tax/article-22-income-tax/part-1-general/section-39-22-1195-child-care-expenses-tax-credit-legislative-declaration-definitionshttps://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=46

### co_military_retirement_subtraction

**Label**: Colorado military retirement subtraction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.colorado.gov/sites/tax/files/documents/DR0104AD_2022.pdf#page=1
- https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=12
- https://law.justia.com/codes/colorado/2022/title-39/article-22/part-1/section-39-22-104/

### co_modified_agi

**Label**: Colorado modified adjusted gross income for the sales tax refund
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.colorado.gov/sites/tax/files/documents/DR_0104_Book_2022.pdf#page=23

### co_non_refundable_credits

**Label**: Colorado non-refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### co_non_refundable_ctc

**Label**: Non-refundable Child Tax Credit replicated to include the Colorado limitations
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Total value of the non-refundable portion of the Child Tax Credit.

**References**:
- https://casetext.com/statute/colorado-revised-statutes/title-39-taxation/specific-taxes/income-tax/article-22-income-tax/part-1-general/section-39-22-129-child-tax-credit-legislative-declaration-definitions-repeal
- https://tax.colorado.gov/sites/tax/files/documents/DR_0104CN_2022.pdf#page=1
- https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=16

### co_oap

**Label**: Colorado Old Age Pension
**Entity**: person
**Period**: year

### co_oap_eligible

**Label**: Colorado Old Age Pension Eligible
**Entity**: person
**Period**: year

### co_pension_subtraction

**Label**: Colorado pension and annuity subtraction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### co_pension_subtraction_income

**Label**: Income for the Colorado pension and annuity subtraction
**Entity**: person
**Period**: year
**Unit**: currency-USD

### co_pension_subtraction_indv

**Label**: Colorado pension and annuity subtraction for eligible individuals
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.colorado.gov/sites/tax/files/documents/DR0104AD_2022.pdf#page=1
- https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=12
- https://law.justia.com/codes/colorado/2022/title-39/article-22/part-1/section-39-22-104/

### co_property_tax_exemption

**Label**: Colorado property tax exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://casetext.com/statute/colorado-revised-statutes/title-39-taxation/property-tax/exemptions/article-3-exemptions/part-2-property-tax-exemption-for-qualifying-seniors-and-disabled-veterans/section-39-3-203-property-tax-exemption-qualifications

### co_qualified_business_income_deduction_addback

**Label**: Colorado qualified business income deduction addback
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://casetext.com/statute/colorado-revised-statutes/title-39-taxation/specific-taxes/income-tax/article-22-income-tax/part-1-general/section-39-22-104-effective-until-official-proclamation-by-governor-income-tax-imposed-on-individuals-estates-and-trusts-single-rate-report-legislative-declaration-definitions-repeal
- https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=5
- https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2021.pdf#page=5
- https://tax.colorado.gov/individual-income-tax-guide

### co_qualified_business_income_deduction_addback_required

**Label**: Required to add back the Colorado qualified business income deduction
**Entity**: tax_unit
**Period**: year

**References**:
- https://casetext.com/statute/colorado-revised-statutes/title-39-taxation/specific-taxes/income-tax/article-22-income-tax/part-1-general/section-39-22-104-effective-until-official-proclamation-by-governor-income-tax-imposed-on-individuals-estates-and-trusts-single-rate-report-legislative-declaration-definitions-repeal
- https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=5
- https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2021.pdf#page=5
- https://tax.colorado.gov/individual-income-tax-guide

### co_quality_rating_of_child_care_facility

**Label**: Quality rating of child care facility for Colorado Child Care Assistance Program
**Entity**: person
**Period**: year

### co_refundable_credits

**Label**: Colorado refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### co_refundable_ctc

**Label**: Refundable Child Tax Credit replicated to include the Colorado limitations
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Total value of the refundable portions of the Child Tax Credit.

**References**:
- https://casetext.com/statute/colorado-revised-statutes/title-39-taxation/specific-taxes/income-tax/article-22-income-tax/part-1-general/section-39-22-129-child-tax-credit-legislative-declaration-definitions-repeal
- https://tax.colorado.gov/sites/tax/files/documents/DR_0104CN_2022.pdf#page=1
- https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=16

### co_sales_tax_refund

**Label**: Colorado sales tax refund
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.colorado.gov/sites/tax/files/documents/DR_0104_Book_2022.pdf#page=23

### co_sales_tax_refund_eligible

**Label**: Eligible for the Colorado sales tax refund
**Entity**: tax_unit
**Period**: year

**References**:
- https://tax.colorado.gov/sites/tax/files/documents/DR_0104_Book_2022.pdf#page=23

### co_social_security_subtraction_indv

**Label**: Colorado social security subtraction for eligible individuals
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.colorado.gov/sites/tax/files/documents/DR0104AD_2022.pdf#page=1
- https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=12
- https://law.justia.com/codes/colorado/2022/title-39/article-22/part-1/section-39-22-104/

### co_social_security_subtraction_indv_eligible

**Label**: Eligible for the Colorado social security subtraction for eligible individuals
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.colorado.gov/sites/tax/files/documents/DR0104AD_2022.pdf#page=1
- https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=12
- https://law.justia.com/codes/colorado/2022/title-39/article-22/part-1/section-39-22-104/

### co_state_addback

**Label**: Colorado state income tax addback
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2021.pdf#page=5https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=5

### co_state_supplement

**Label**: Colorado State Supplement
**Entity**: person
**Period**: year

### co_state_supplement_eligible

**Label**: Colorado State Supplement Eligible
**Entity**: person
**Period**: year

### co_subtractions

**Label**: Colorado subtractions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### co_tanf

**Label**: Colorado TANF
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### co_tanf_count_children

**Label**: Colorado TANF number of children
**Entity**: spm_unit
**Period**: year

### co_tanf_countable_earned_income_grant_standard

**Label**: Colorado TANF total countable earned income for grant standard
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### co_tanf_countable_earned_income_need

**Label**: Colorado TANF total countable income for need determination
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### co_tanf_countable_gross_earned_income

**Label**: Colorado TANF countable gross earned income
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### co_tanf_countable_gross_unearned_income

**Label**: Colorado TANF countable gross unearned income
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### co_tanf_eligible

**Label**: Colorado TANF eligible
**Entity**: spm_unit
**Period**: year

### co_tanf_grant_standard

**Label**: Colorado TANF grant standard
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### co_tanf_income_eligible

**Label**: Colorado TANF income eligible
**Entity**: spm_unit
**Period**: year

### co_tanf_need_standard

**Label**: Colorado TANF need standard
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### co_taxable_income

**Label**: Colorado taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### co_withheld_income_tax

**Label**: Colorado withheld income tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

### coal_expense

**Label**: Coal expense
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### cohabitating_spouses

**Label**: Cohabitating spouses
**Entity**: tax_unit
**Period**: year

Whether spouses in joint or separate tax units are cohabitating.

### commodity_supplemental_food_program

**Label**: Commodity Supplemental Food Program
**Entity**: person
**Period**: year
**Unit**: currency-USD

### commodity_supplemental_food_program_eligible

**Label**: Commodity Supplemental Food Program eligible
**Entity**: person
**Period**: year

### cooking_fuel_expense

**Label**: Cooking fuel expense
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### cost_of_attending_college

**Label**: Pell Grant cost of attendance
**Entity**: person
**Period**: year

### count_529_contribution_beneficiaries

**Label**: Number of beneficiaries to 529 college savings plan contributions
**Entity**: person
**Period**: year

### count_cdcc_eligible

**Label**: CDCC-eligible children
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### count_days_postpartum

**Label**: Number of days postpartum
**Entity**: person
**Period**: year
**Unit**: day

### count_distinct_utility_expenses

**Label**: Number of distinct utility expenses
**Entity**: spm_unit
**Period**: year

The number of distinct utility expenses.

### county

**Label**: County
**Entity**: household
**Period**: year

### county_fips

**Label**: County FIPS code
**Entity**: household
**Period**: year

County FIPS code

### county_str

**Label**: County (string)
**Entity**: household
**Period**: year

County variable, stored as a string

### cps_race

**Label**: CPS racial category
**Entity**: person
**Period**: year

This variable is the PRDTRACE variable in the Current Population Survey.

### csrs_retirement_pay

**Label**: Civil Service Retirement System (CSRS) retirement income
**Entity**: person
**Period**: year
**Unit**: currency-USD

Retirement income from the federal Civil Service Retirement System.

**References**:
- https://tax.vermont.gov/individuals/seniors-and-retirees

### ct_additions

**Label**: Connecticut additions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ct_agi

**Label**: Connecticut adjusted gross income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ct_agi_subtractions

**Label**: Connecticut subtractions from federal adjusted gross income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ct_amt

**Label**: Connecticut alternative minimum tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://portal.ct.gov/-/media/DRS/Forms/2022/Income/2022-CT-1040-Instructions_1222.pdf#page=2https://portal.ct.gov/-/media/DRS/Forms/2022/Income/CT-1040_1222.pdf#page=1https://portal.ct.gov/-/media/DRS/Forms/2022/Income/CT-6251_1222.pdf#page=1https://www.irs.gov/pub/irs-pdf/f6251.pdf#page=1https://www.irs.gov/pub/irs-pdf/i6251.pdf#page=9

### ct_child_tax_rebate

**Label**: Connecticut child tax rebate
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ct_eitc

**Label**: Connecticut Earned Income Tax Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://portal.ct.gov/-/media/DRS/Forms/2022/Income/Schedule-CT-EITC_1222.pdfhttps://www.cga.ct.gov/current/pub/chap_229.htm#sec_12-704e

### ct_income_tax

**Label**: Connecticut income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ct_income_tax_after_amt

**Label**: Connecticut income tax after the addition of the alternative minimum tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://portal.ct.gov/-/media/DRS/Forms/2022/Income/2022-CT-1040-Instructions_1222.pdf#page=2https://portal.ct.gov/-/media/DRS/Forms/2022/Income/CT-1040_1222.pdf#page=1

### ct_income_tax_after_personal_credits

**Label**: Connecticut income tax after personal tax credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ct_income_tax_before_refundable_credits

**Label**: Connecticut income tax before refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ct_income_tax_high_tax_recapture

**Label**: Connecticut income tax recapture at high brackets
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ct_income_tax_low_tax_recapture

**Label**: Connecticut income tax recapture at low brackets
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ct_income_tax_middle_tax_recapture

**Label**: Connecticut income tax recapture at middle brackets
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ct_income_tax_phase_out_add_back

**Label**: Connecticut income tax phase out add back
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ct_income_tax_recapture

**Label**: Connecticut income tax recapture
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ct_non_refundable_credits

**Label**: Connecticut non-refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ct_pension_annuity_subtraction

**Label**: Connecticut pension and annuity subtraction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.cga.ct.gov/current/pub/chap_229.htm#sec_12-701
- https://portal.ct.gov/-/media/drs/forms/2024/income/2024-ct-1040-instructions_1224.pdf#page=28

### ct_personal_credit_rate

**Label**: Connecticut personal credit rate
**Entity**: tax_unit
**Period**: year
**Unit**: 

### ct_personal_exemptions

**Label**: Connecticut Personal Exemptions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ct_property_tax_credit

**Label**: Connecticut property tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://portal.ct.gov/-/media/DRS/Forms/2021/Income/CT-1040-Online-Booklet_1221.pdf#page=30

### ct_property_tax_credit_eligible

**Label**: Eligible for the Connecticut Property Tax Credit
**Entity**: tax_unit
**Period**: year

**References**:
- https://www.cga.ct.gov/current/pub/chap_229.htm#sec_12-704c

### ct_refundable_credits

**Label**: Connecticut refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ct_section_179_expense_add_back

**Label**: Connecticut Section 179 Expense Add Back
**Entity**: tax_unit
**Period**: year

Add 80 percent of the section 179 amount deducted in determining federal AGI.

**References**:
- https://portal.ct.gov/-/media/DRS/Forms/2022/Income/2022-CT-1040-Instructions_1222.pdf#page=7

### ct_social_security_benefit_adjustment

**Label**: Connecticut social security benefit adjustment
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.cga.ct.gov/current/pub/chap_229.htm#sec_12-701https://portal.ct.gov/-/media/DRS/Forms/2022/Income/2022-CT-1040-Instructions_1222.pdf#page=24

### ct_subtractions

**Label**: Connecticut subtractions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ct_taxable_income

**Label**: Connecticut taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ct_tuition_subtraction

**Label**: Connecticut tuition subtraction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.cga.ct.gov/current/pub/chap_229.htm#sec_12-701a

### ct_withheld_income_tax

**Label**: Connecticut withheld income tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

### ctc

**Label**: Child Tax Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Total value of the non-refundable and refundable portions of the Child Tax Credit.

**References**:
- https://www.law.cornell.edu/uscode/text/26/24#a

### ctc_adult_individual_maximum

**Label**: CTC maximum amount (adult dependent)
**Entity**: person
**Period**: year
**Unit**: currency-USD

The CTC entitlement in respect of this person as an adult dependent.

**References**:
- https://www.law.cornell.edu/uscode/text/26/24#a
- https://www.law.cornell.edu/uscode/text/26/24#h
- https://www.law.cornell.edu/uscode/text/26/24#i

### ctc_arpa_addition

**Label**: Additional CTC from ARPA
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.irs.gov/pub/irs-pdf/i1040s8.pdf#page=4

### ctc_arpa_max_addition

**Label**: Maximum additional CTC from ARPA
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

ARPA capped the additional amount based on the phase-out thresholds.

**References**:
- https://www.irs.gov/pub/irs-pdf/i1040s8.pdf#page=4

### ctc_arpa_phase_out

**Label**: Phase-out of CTC ARPA addition
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ctc_arpa_phase_out_cap

**Label**: Cap on phase-out of ARPA CTC expansion
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

ARPA capped the additional amount based on the phase-out thresholds.

**References**:
- https://www.irs.gov/pub/irs-pdf/i1040s8.pdf#page=4

### ctc_arpa_phase_out_threshold

**Label**: CTC ARPA phase-out threshold
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ctc_arpa_uncapped_phase_out

**Label**: Uncapped phase-out of ARPA CTC increase
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ctc_child_individual_maximum

**Label**: CTC maximum amount (child)
**Entity**: person
**Period**: year
**Unit**: currency-USD

The CTC entitlement in respect of this person as a child.

**References**:
- https://www.law.cornell.edu/uscode/text/26/24#a
- https://www.law.cornell.edu/uscode/text/26/24#h
- https://www.law.cornell.edu/uscode/text/26/24#i

### ctc_child_individual_maximum_arpa

**Label**: CTC maximum amount (child under ARPA)
**Entity**: person
**Period**: year
**Unit**: currency-USD

The CTC entitlement in respect of this person as a child, under the American Rescue Plan Act.

### ctc_individual_maximum

**Label**: CTC individual amount maximum
**Entity**: person
**Period**: year
**Unit**: currency-USD

The Child Tax Credit entitlement in respect of this person.

**References**:
- https://www.law.cornell.edu/uscode/text/26/24#a
- https://www.law.cornell.edu/uscode/text/26/24#h
- https://www.law.cornell.edu/uscode/text/26/24#i

### ctc_limiting_tax_liability

**Label**: CTC-limiting tax liability
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

The tax liability used to determine the maximum amount of the non-refundable CTC. Excludes SALT from all calculations (this is an inaccuracy required to avoid circular dependencies).

### ctc_maximum

**Label**: Maximum CTC
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Maximum value of the Child Tax Credit, before phase-out.

### ctc_maximum_with_arpa_addition

**Label**: Maximum CTC for ARPA
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Maximum value of the Child Tax Credit, before phase-out, under ARPA.

### ctc_phase_in

**Label**: CTC phase-in
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/24#d

### ctc_phase_out

**Label**: CTC reduction from income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Reduction of the total CTC due to income.

### ctc_phase_out_threshold

**Label**: CTC phase-out threshold
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ctc_qualifying_child

**Label**: CTC-qualifying child
**Entity**: person
**Period**: year

Child qualifies for the Child Tax Credit

**References**:
- https://www.law.cornell.edu/uscode/text/26/24#c

### ctc_qualifying_children

**Label**: CTC-qualifying children
**Entity**: tax_unit
**Period**: year

Count of children that qualify for the Child Tax Credit

**References**:
- https://www.law.cornell.edu/uscode/text/26/24#c

### ctc_refundable_maximum

**Label**: Maximum refundable CTC
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

The maximum refundable CTC for this person.

**References**:
- https://www.law.cornell.edu/uscode/text/26/24#a
- https://www.law.cornell.edu/uscode/text/26/24#h
- https://www.law.cornell.edu/uscode/text/26/24#i
- https://www.irs.gov/pub/irs-prior/f1040--2021.pdf
- https://www.irs.gov/pub/irs-prior/f1040s8--2021.pdf

### ctc_social_security_tax

**Label**: Refundable Child Tax Credit Social Security Tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Social Security taxes considered in the Child Tax Credit calculation

**References**:
- https://www.law.cornell.edu/uscode/text/26/24#d_2

### ctc_value

**Label**: CTC value
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Actual value of the Child Tax Credit

### current_home_energy_use

**Label**: Current home energy use in monthly kilowatt hours
**Entity**: household
**Period**: year
**Unit**: kWh/month

**References**:
- https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=587

### current_pregnancies

**Label**: The number of children a pregnant person is expecting
**Entity**: person
**Period**: year

### current_pregnancy_month

**Label**: Current pregnancy month
**Entity**: person
**Period**: month

### dc_additions

**Label**: DC additions to federal adjusted gross income
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/52926_D-40_12.21.21_Final_Rev011122.pdf#page=63https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2022_D-40_Booklet_Final_blk_01_23_23_Ordc.pdf#page=55

### dc_agi

**Label**: DC AGI (adjusted gross income) for each person in tax unit
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/52926_D-40_12.21.21_Final_Rev011122.pdf#page=36https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2022_D-40_Booklet_Final_blk_01_23_23_Ordc.pdf#page=34

### dc_ccsp

**Label**: DC Child Care Subsidy Program (CCSP) benefit amount
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://osse.dc.gov/subsidy

### dc_ccsp_asset_eligible

**Label**: Eligible for DC Child Care Subsidy Program (CCSP) due to income
**Entity**: spm_unit
**Period**: month

**References**:
- https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/DC%20Child%20Care%20Subsidy%20Program%20Policy%20Manual.pdf#page=12

### dc_ccsp_assets

**Label**: DC Child Care Subsidy Program (CCSP) asset
**Entity**: spm_unit
**Period**: month

**References**:
- https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/DC%20Child%20Care%20Subsidy%20Program%20Policy%20Manual.pdf#page=12

### dc_ccsp_attending_days_per_month

**Label**: DC Child Care Subsidy Program (CCSP) attending days per month
**Entity**: person
**Period**: month

### dc_ccsp_child_category

**Label**: DC Child Care Subsidy Program (CCSP) child category
**Entity**: person
**Period**: month

**References**:
- https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/FY25%20Subsidy%20Reimbursement%20Rates%20English.pdf

### dc_ccsp_childcare_provider_category

**Label**: DC Child Care Subsidy Program (CCSP) child care provider category
**Entity**: person
**Period**: month

**References**:
- https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/FY25%20Subsidy%20Reimbursement%20Rates%20English.pdf

### dc_ccsp_copay

**Label**: DC Child Care Subsidy Program (CCSP) copay
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/Sliding%20Fee%20Scale.pdf

### dc_ccsp_countable_income

**Label**: DC Child Care Subsidy Program (CCSP) countable income
**Entity**: spm_unit
**Period**: month

**References**:
- https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/DC%20Child%20Care%20Subsidy%20Program%20Policy%20Manual.pdf#page=12

### dc_ccsp_eligible

**Label**: Eligible for DC Child Care Subsidy Program (CCSP)
**Entity**: spm_unit
**Period**: month

**References**:
- https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/DC%20Child%20Care%20Subsidy%20Program%20Policy%20Manual.pdf#page=8

### dc_ccsp_eligible_child

**Label**: Eligible child for DC Child Care Subsidy Program (CCSP)
**Entity**: person
**Period**: month

**References**:
- https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/DC%20Child%20Care%20Subsidy%20Program%20Policy%20Manual.pdf#page=8

### dc_ccsp_enrolled

**Label**: Whether the family is currently enrolled in DC Child Care Subsidy Program (CCSP)
**Entity**: spm_unit
**Period**: month

### dc_ccsp_first_child_copay

**Label**: DC Child Care Subsidy Program (CCSP) fist child copay amount
**Entity**: person
**Period**: month
**Unit**: currency-USD

**References**:
- https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/Sliding%20Fee%20Scale.pdf

### dc_ccsp_immigration_status_eligible_person

**Label**: Eligible person for DC Child Care Subsidy Program (CCSP) based on immigration status
**Entity**: person
**Period**: month

**References**:
- https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/DC%20Child%20Care%20Subsidy%20Program%20Policy%20Manual.pdf#page=8

### dc_ccsp_income_eligible

**Label**: Eligible for DC Child Care Subsidy Program (CCSP) due to income
**Entity**: spm_unit
**Period**: month

**References**:
- https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/DC%20Child%20Care%20Subsidy%20Program%20Policy%20Manual.pdf#page=12

### dc_ccsp_income_test_waived

**Label**: Income test exemption under DC Child Care Subsidy Program (CCSP)
**Entity**: spm_unit
**Period**: month

**References**:
- https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/DC%20Child%20Care%20Subsidy%20Program%20Policy%20Manual.pdf#page=11

### dc_ccsp_is_full_time

**Label**: Person is attending full time day care under DC Child Care Subsidy Program (CCSP)
**Entity**: person
**Period**: month

### dc_ccsp_is_second_youngest_child

**Label**: Person is the second youngest child for DC Child Care Subsidy Program (CCSP) 
**Entity**: person
**Period**: month

**References**:
- https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/Sliding%20Fee%20Scale.pdf

### dc_ccsp_is_youngest_child

**Label**: Person is the youngest child for DC Child Care Subsidy Program (CCSP) 
**Entity**: person
**Period**: month

**References**:
- https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/Sliding%20Fee%20Scale.pdf

### dc_ccsp_maximum_subsidy_amount

**Label**: DC Child Care Subsidy Program (CCSP) maximum subsidy amount per child
**Entity**: person
**Period**: month
**Unit**: currency-USD

**References**:
- https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/FY25%20Subsidy%20Reimbursement%20Rates%20English.pdf#page=2

### dc_ccsp_qualified_activity_eligible

**Label**: Eligible for DC Child Care Subsidy Program (CCSP) due to qualified activity
**Entity**: spm_unit
**Period**: month

**References**:
- https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/DC%20Child%20Care%20Subsidy%20Program%20Policy%20Manual.pdf#page=8

### dc_ccsp_qualified_activity_or_need_eligible

**Label**: Eligible for DC Child Care Subsidy Program (CCSP) due to qualified activity or need
**Entity**: spm_unit
**Period**: month

**References**:
- https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/DC%20Child%20Care%20Subsidy%20Program%20Policy%20Manual.pdf#page=8

### dc_ccsp_qualified_need_eligible

**Label**: Eligible for DC Child Care Subsidy Program (CCSP) due to qualified need
**Entity**: spm_unit
**Period**: month

**References**:
- https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/DC%20Child%20Care%20Subsidy%20Program%20Policy%20Manual.pdf#page=8

### dc_ccsp_schedule_type

**Label**: DC Child Care Subsidy Program (CCSP) schedule type
**Entity**: person
**Period**: month

**References**:
- https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/FY25%20Subsidy%20Reimbursement%20Rates%20English.pdf

### dc_ccsp_second_child_copay

**Label**: DC Child Care Subsidy Program (CCSP) second child copay amount
**Entity**: person
**Period**: month
**Unit**: currency-USD

**References**:
- https://osse.dc.gov/sites/default/files/dc/sites/osse/publication/attachments/Sliding%20Fee%20Scale.pdf

### dc_cdcc

**Label**: DC child and dependent care credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/52926_D-40_12.21.21_Final_Rev011122.pdf#page=36https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2022_D-40_Booklet_Final_blk_01_23_23_Ordc.pdf#page=34

### dc_ctc

**Label**: DC Child Tax Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://code.dccouncil.gov/us/dc/council/code/sections/47-1806.17

### dc_ctc_capped_children

**Label**: Capped number of DC CTC eligible children
**Entity**: tax_unit
**Period**: year

**References**:
- https://code.dccouncil.gov/us/dc/council/code/sections/47-1806.17

### dc_ctc_eligible_child

**Label**: Whether the child is eligible for the DC CTC
**Entity**: person
**Period**: year

**References**:
- https://code.dccouncil.gov/us/dc/council/code/sections/47-1806.17

### dc_deduction_indiv

**Label**: DC deduction for each person in tax unit
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/52926_D-40_12.21.21_Final_Rev011122.pdf#page=44https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2022_D-40_Booklet_Final_blk_01_23_23_Ordc.pdf#page=44

### dc_deduction_joint

**Label**: DC deduction for each tax unit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### dc_disability_exclusion

**Label**: DC disability exclusion
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://code.dccouncil.gov/us/dc/council/code/sections/47-1803.02#(a)(2)(M)

### dc_disabled_exclusion_subtraction

**Label**: DC disabled exclusion subtraction
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/52926_D-40_12.21.21_Final_Rev011122.pdf#page=63https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2022_D-40_Booklet_Final_blk_01_23_23_Ordc.pdf#page=55https://code.dccouncil.gov/us/dc/council/code/titles/47/chapters/18/subchapters/III

### dc_eitc

**Label**: DC EITC
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://code.dccouncil.gov/us/dc/council/code/sections/47-1806.04

### dc_eitc_with_qualifying_child

**Label**: DC EITC with qualifying children
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://code.dccouncil.gov/us/dc/council/code/sections/47-1806.04

### dc_eitc_without_qualifying_child

**Label**: DC EITC without qualifying children
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://code.dccouncil.gov/us/dc/council/code/sections/47-1806.04

### dc_files_separately

**Label**: Married couple files separately on DC tax return
**Entity**: tax_unit
**Period**: year

### dc_income_subtractions

**Label**: DC subtractions from federal adjusted gross income
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/52926_D-40_12.21.21_Final_Rev011122.pdf#page=63https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2022_D-40_Booklet_Final_blk_01_23_23_Ordc.pdf#page=55

### dc_income_tax

**Label**: DC income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/52926_D-40_12.21.21_Final_Rev011122.pdf#page=37https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2022_D-40_Booklet_Final_blk_01_23_23_Ordc.pdf#page=35

### dc_income_tax_before_credits

**Label**: DC income tax before credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/52926_D-40_12.21.21_Final_Rev011122.pdf#page=36https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2022_D-40_Booklet_Final_blk_01_23_23_Ordc.pdf#page=34

### dc_income_tax_before_credits_indiv

**Label**: DC income tax before credits when married couples file separately
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/52926_D-40_12.21.21_Final_Rev011122.pdf#page=36https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2022_D-40_Booklet_Final_blk_01_23_23_Ordc.pdf#page=34

### dc_income_tax_before_credits_joint

**Label**: DC income tax before credits when married couples file jointly
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/52926_D-40_12.21.21_Final_Rev011122.pdf#page=36https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2022_D-40_Booklet_Final_blk_01_23_23_Ordc.pdf#page=34

### dc_income_tax_before_refundable_credits

**Label**: DC income tax before refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/52926_D-40_12.21.21_Final_Rev011122.pdf#page=36https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2022_D-40_Booklet_Final_blk_01_23_23_Ordc.pdf#page=34

### dc_itemized_deductions

**Label**: DC itemized deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/52926_D-40_12.21.21_Final_Rev011122.pdf#page=18https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2022_D-40_Booklet_Final_blk_01_23_23_Ordc.pdf#page=17

### dc_kccatc

**Label**: DC keep child care affordable tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/52926_D-40_12.21.21_Final_Rev011122.pdf#page=67https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2022_D-40_Booklet_Final_blk_01_23_23_Ordc.pdf#page=59

### dc_liheap_eligible

**Label**: Eligible for the DC LIHEAP
**Entity**: spm_unit
**Period**: year

**References**:
- https://doee.dc.gov/liheap

### dc_liheap_heating_type

**Label**: Household heating types for DC LIHEAP
**Entity**: spm_unit
**Period**: year

### dc_liheap_housing_type

**Label**: Housing type for DC LIHEAP
**Entity**: spm_unit
**Period**: year

### dc_liheap_income_level

**Label**: Income level for DC LIHEAP payment
**Entity**: spm_unit
**Period**: year

**References**:
- https://doee.dc.gov/sites/default/files/dc/sites/doee/service_content/attachments/DOEE%20FY24%20LIHEAP_REGULAR_Benefits_Table-Matrix.pdf

### dc_liheap_payment

**Label**: DC LIHEAP payment
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://doee.dc.gov/sites/default/files/dc/sites/doee/service_content/attachments/DOEE%20FY24%20LIHEAP_REGULAR_Benefits_Table-Matrix.pdf

### dc_non_refundable_credits

**Label**: DC non-refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/52926_D-40_12.21.21_Final_Rev011122.pdf#page=63https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2022_D-40_Booklet_Final_blk_01_23_23_Ordc.pdf#page=55

### dc_ptc

**Label**: DC property tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/52926_D-40_12.21.21_Final_Rev011122.pdf#page=49https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2022_D-40_Booklet_Final_blk_01_23_23_Ordc.pdf#page=47

### dc_refundable_credits

**Label**: DC refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/52926_D-40_12.21.21_Final_Rev011122.pdf#page=63https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2022_D-40_Booklet_Final_blk_01_23_23_Ordc.pdf#page=55

### dc_self_employment_loss_addition

**Label**: DC excess self-employment loss addition
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/52926_D-40_12.21.21_Final_Rev011122.pdf#page=63https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2022_D-40_Booklet_Final_blk_01_23_23_Ordc.pdf#page=55

### dc_snap_temporary_local_benefit

**Label**: DC temporary local SNAP benefit amount
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

DC temporary SNAP benefit amount

**References**:
- https://dhs.dc.gov/page/give-snap-raise-heres-what-expect
- https://code.dccouncil.gov/us/dc/council/laws/24-301

### dc_standard_deduction

**Label**: DC standard deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### dc_tanf

**Label**: DC Temporary Assistance for Needy Families (TANF)
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://code.dccouncil.gov/us/dc/council/code/sections/4-205.52

### dc_tanf_childcare_deduction

**Label**: DC Temporary Assistance for Needy Families (TANF) child care deduction 
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://code.dccouncil.gov/us/dc/council/code/sections/4-205.11

### dc_tanf_countable_earned_income

**Label**: DC Temporary Assistance for Needy Families (TANF) countable earned income
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://code.dccouncil.gov/us/dc/council/code/sections/4-205.11

### dc_tanf_countable_income

**Label**: DC Temporary Assistance for Needy Families (TANF) countable income
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

### dc_tanf_countable_resources

**Label**: DC Temporary Assistance for Needy Families (TANF) countable resources
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

### dc_tanf_countable_unearned_income

**Label**: DC Temporary Assistance for Needy Families (TANF) countable unearned income
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://code.dccouncil.gov/us/dc/council/code/sections/4-205.11

### dc_tanf_demographic_eligible_person

**Label**: Eligible person for DC Temporary Assistance for Needy Families (TANF) based on demographics
**Entity**: person
**Period**: month

**References**:
- https://code.dccouncil.gov/us/dc/council/code/sections/4-205.18
- https://code.dccouncil.gov/us/dc/council/code/sections/4-205.63

### dc_tanf_earned_income_after_disregard_person

**Label**: DC Temporary Assistance for Needy Families (TANF) earned income after disregard per person
**Entity**: person
**Period**: month
**Unit**: currency-USD

**References**:
- https://code.dccouncil.gov/us/dc/council/code/sections/4-205.11

### dc_tanf_eligible

**Label**: Eligible for DC Temporary Assistance for Needy Families (TANF)
**Entity**: spm_unit
**Period**: month

**References**:
- https://dhs.dc.gov/service/tanf-district-families

### dc_tanf_gross_earned_income

**Label**: DC Temporary Assistance for Needy Families (TANF) gross earned income
**Entity**: person
**Period**: month
**Unit**: currency-USD

### dc_tanf_gross_unearned_income

**Label**: DC Temporary Assistance for Needy Families (TANF) gross unearned income
**Entity**: person
**Period**: month
**Unit**: currency-USD

### dc_tanf_immigration_status_eligible_person

**Label**: Eligible person for DC Temporary Assistance for Needy Families (TANF) based on immigration status
**Entity**: person
**Period**: month

**References**:
- https://code.dccouncil.gov/us/dc/council/code/sections/4-205.24#(a)

### dc_tanf_income_eligible

**Label**: Eligible for DC Temporary Assistance for Needy Families (TANF) due to income
**Entity**: spm_unit
**Period**: month

**References**:
- https://code.dccouncil.gov/us/dc/council/code/sections/4-205.10

### dc_tanf_resources_eligible

**Label**: Eligible for DC Temporary Assistance for Needy Families (TANF) due to resources
**Entity**: spm_unit
**Period**: month

**References**:
- https://dhs.dc.gov/sites/default/files/dc/sites/dhs/service_content/attachments/DC%20TANF%20State%20Plan_Oct-2023.pdf#page=40

### dc_tanf_standard_payment

**Label**: DC Temporary Assistance for Needy Families (TANF) standard payment
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://code.dccouncil.gov/us/dc/council/code/sections/4-205.52

### dc_taxable_income

**Label**: DC taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### dc_taxable_income_indiv

**Label**: DC taxable income (can be negative) when married couple files separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/52926_D-40_12.21.21_Final_Rev011122.pdf#page=36https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2022_D-40_Booklet_Final_blk_01_23_23_Ordc.pdf#page=34

### dc_taxable_income_joint

**Label**: DC taxable income (can be negative) when married couple files jointly
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/52926_D-40_12.21.21_Final_Rev011122.pdf#page=36https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2022_D-40_Booklet_Final_blk_01_23_23_Ordc.pdf#page=34

### dc_withheld_income_tax

**Label**: DC withheld income tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

### de_additional_standard_deduction

**Label**: Delaware additional standard deduction
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-02_Instructions.pdf#page=8

### de_additions

**Label**: Delaware adjusted gross income additions
**Entity**: person
**Period**: year
**Unit**: currency-USD

### de_aged_personal_credit

**Label**: Delaware aged personal credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://delcode.delaware.gov/title30/c011/sc02/index.html#1110

### de_agi

**Label**: Delaware adjusted gross income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### de_agi_indiv

**Label**: Delaware adjusted gross income for each individual when married filing separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

### de_agi_joint

**Label**: Delaware adjusted gross income for each individual whe married filing jointly
**Entity**: person
**Period**: year
**Unit**: currency-USD

### de_base_standard_deduction_indv

**Label**: Delaware base standard deduction when married couples are filing separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-02_Instructions.pdf#page=8

### de_base_standard_deduction_joint

**Label**: Delaware base standard deduction when married couples are filing jointly
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-02_Instructions.pdf#page=8

### de_capped_real_estate_tax

**Label**: Delaware capped real estate tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://revenuefiles.delaware.gov/2022/TY22_PIT-RSA_2022-02_PaperInteractive.pdf
- https://delcode.delaware.gov/title30/c011/sc02/index.html

### de_cdcc

**Label**: Delaware dependent care credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### de_claims_refundable_eitc

**Label**: Filer claims refundable Delaware EITC
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Whether the filer claims the refundable over the non-refundable Delaware Earned Income Tax Credit.

### de_deduction_indv

**Label**: Delaware deduction when married couples are filing separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://delcode.delaware.gov/title30/c011/sc02/index.html title 30, chapter 11, subchapter II, section 1108

### de_deduction_joint

**Label**: Delaware deduction when married filing jointly
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://delcode.delaware.gov/title30/c011/sc02/index.html title 30, chapter 11, subchapter II, section 1108

### de_eitc

**Label**: Delaware EITC
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Refundable or non-refundable Delaware EITC

**References**:
- https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-02_Instructions.pdf

### de_elderly_or_disabled_income_exclusion_eligible_person

**Label**: Eligible person for the Delaware elderly or disabled income exclusion
**Entity**: person
**Period**: year

### de_elderly_or_disabled_income_exclusion_indiv

**Label**: Delaware individual aged or disabled exclusion when married filing sepaartely
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-01_PaperInteractive.pdf#page=1

### de_elderly_or_disabled_income_exclusion_joint

**Label**: Delaware individual aged or disabled exclusion when married filing jointly
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-01_PaperInteractive.pdf#page=1

### de_files_separately

**Label**: married couple files separately on the Delaware tax return
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-02_Instructions.pdf

### de_income_tax

**Label**: Delaware personal income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### de_income_tax_before_non_refundable_credits_indv

**Label**: Delaware personal income tax before non-refundable credits when married filing separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

### de_income_tax_before_non_refundable_credits_joint

**Label**: Delaware personal income tax before non-refundable credits when married filing jointly
**Entity**: person
**Period**: year
**Unit**: currency-USD

### de_income_tax_before_non_refundable_credits_unit

**Label**: Delaware personal income tax before non-refundable credits combined
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### de_income_tax_before_refundable_credits

**Label**: Delaware personal income tax before refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### de_income_tax_if_claiming_non_refundable_eitc

**Label**: Delaware tax liability if claiming non-refundable Delaware EITC
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### de_income_tax_if_claiming_refundable_eitc

**Label**: Delaware tax liability if claiming refundable Delaware EITC
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### de_itemized_deductions

**Label**: Delaware itemized deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### de_itemized_deductions_indv

**Label**: Delaware itemized deductions when married couples are filing separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://revenuefiles.delaware.gov/2022/TY22_PIT-RSA_2022-02_PaperInteractive.pdf
- https://delcode.delaware.gov/title30/c011/sc02/index.html

### de_itemized_deductions_joint

**Label**: Delaware itemized deductions when married filing jointly
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://revenuefiles.delaware.gov/2022/TY22_PIT-RSA_2022-02_PaperInteractive.pdf
- https://delcode.delaware.gov/title30/c011/sc02/index.html

### de_itemized_deductions_unit

**Label**: Delaware itemized deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://revenuefiles.delaware.gov/2022/TY22_PIT-RSA_2022-02_PaperInteractive.pdf
- https://delcode.delaware.gov/title30/c011/sc02/index.html

### de_non_refundable_credits

**Label**: Delaware non-refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### de_non_refundable_eitc

**Label**: Delaware non-refundable EITC
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Non-refundable EITC credit reducing DE State income tax.

**References**:
- https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-02_Instructions.pdf

### de_non_refundable_eitc_if_claimed

**Label**: Delaware non-refundable EITC if claimed
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Non-refundable EITC credit reducing DE State income tax.

**References**:
- https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-02_Instructions.pdf

### de_pension_exclusion

**Label**: Delaware individual pension exclusion
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-02_Instructions.pdf#page=6
- https://delcode.delaware.gov/title30/c011/sc02/index.html

### de_pension_exclusion_income

**Label**: Income sources for the Delaware pension exclusion
**Entity**: person
**Period**: year
**Unit**: currency-USD

### de_personal_credit

**Label**: Delaware personal credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-02_Instructions.pdf

### de_pre_exclusions_agi

**Label**: Delaware individual adjusted gross income before exclusions
**Entity**: person
**Period**: year
**Unit**: currency-USD

### de_refundable_credits

**Label**: Delaware refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### de_refundable_eitc

**Label**: Delaware refundable EITC
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Refundable EITC credit reducing DE State income tax page 8.

**References**:
- https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-02_Instructions.pdf

### de_refundable_eitc_if_claimed

**Label**: Delaware refundable EITC if claimed
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Refundable EITC credit reducing DE State income tax page 8.

**References**:
- https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-02_Instructions.pdf

### de_relief_rebate

**Label**: Delaware relief rebate
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://legis.delaware.gov/BillDetail?LegislationId=99311

### de_standard_deduction

**Label**: Delaware standard deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### de_standard_deduction_indv

**Label**: Delaware standard deduction when married couples are filing separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-02_Instructions.pdf#page=8

### de_standard_deduction_joint

**Label**: Delaware standard deduction when married filing jointly
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-02_Instructions.pdf#page=8

### de_subtractions

**Label**: Delaware subtractions
**Entity**: person
**Period**: year
**Unit**: currency-USD

### de_tax_unit_itemizes

**Label**: Whether the tax unit in Delaware itemizes the deductions
**Entity**: tax_unit
**Period**: year

### de_taxable_income

**Label**: Delaware taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### de_taxable_income_indv

**Label**: Delaware taxable income when married couples are filing separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

### de_taxable_income_joint

**Label**: Delaware taxable income when married filing jointly
**Entity**: person
**Period**: year
**Unit**: currency-USD

### de_withheld_income_tax

**Label**: Delaware withheld income tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

### debt_relief

**Label**: Debt relief income
**Entity**: person
**Period**: year
**Unit**: currency-USD

Income from discharge of indebtedness.

### deductible_interest_expense

**Label**: Interest paid on all loans
**Entity**: person
**Period**: year
**Unit**: currency-USD

### deductible_mortgage_interest

**Label**: Deductible mortgage interest
**Entity**: person
**Period**: year
**Unit**: currency-USD

Under the interest deduction, the US caps the mortgage value to which interest is applied which based on the year of purchase not tax year.

### deep_poverty_gap

**Label**: deep poverty gap
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

Difference between household income and deep poverty line.

### deep_poverty_line

**Label**: deep poverty line
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

Income threshold below which a household is considered to be in deep poverty.

### dependent_care_employer_benefits

**Label**: Dependent care benefits received from an employer
**Entity**: person
**Period**: year
**Unit**: currency-USD

### detailed_occupation_recode

**Label**: CPS detailed occupation recode of previous year
**Entity**: person
**Period**: year

This variable is the POCCU2 variable in the Current Population Survey.

### disability_benefits

**Label**: disability benefits
**Entity**: person
**Period**: year
**Unit**: currency-USD

Disability benefits from employment (not Social Security), except for worker's compensation.

### disabled_head

**Label**: Tax unit head is legally disabled
**Entity**: tax_unit
**Period**: year

### disabled_spouse

**Label**: Tax unit spouse is legally disabled
**Entity**: tax_unit
**Period**: year

### disabled_tax_unit_head_or_spouse

**Label**: Head or Spouse of tax unit is disabled
**Entity**: tax_unit
**Period**: year

### dividend_income

**Label**: ordinary dividend income
**Entity**: person
**Period**: year
**Unit**: currency-USD

Qualified and non-qualified dividends

### dividend_income_reduced_by_investment_income

**Label**: Dividend income reduced by investment income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

IRS Form 1040 Schedule D worksheet (part 1 of 6)

### divorce_year

**Label**: The year that the person was divorced.
**Entity**: person
**Period**: year

### domestic_production_ald

**Label**: Domestic production activities ALD
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Above-the-line deduction from gross income for domestic production activities.

**References**:
- https://www.law.cornell.edu/uscode/text/26/199

### dwks09

**Label**: IRS Form 1040 Schedule D worksheet (part 2 of 6)
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### dwks10

**Label**: IRS Form 1040 Schedule D worksheet (part 3 of 6)
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### dwks13

**Label**: IRS Form 1040 Schedule D worksheet (part 4 of 6)
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### dwks14

**Label**: IRS Form 1040 Schedule D worksheet (part 5 of 6)
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### dwks19

**Label**: IRS Form 1040 Schedule D worksheet (part 6 of 6)
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### e00700

**Label**: e00700
**Entity**: person
**Period**: year

### e01100

**Label**: e01100
**Entity**: person
**Period**: year

### e01200

**Label**: e01200
**Entity**: person
**Period**: year

### e02000

**Label**: e02000
**Entity**: person
**Period**: year

### e03220

**Label**: e03220
**Entity**: person
**Period**: year

### e03230

**Label**: e03230
**Entity**: person
**Period**: year

### e03240

**Label**: e03240
**Entity**: person
**Period**: year

### e03270

**Label**: e03270
**Entity**: person
**Period**: year

### e03290

**Label**: e03290
**Entity**: person
**Period**: year

### e03300

**Label**: e03300
**Entity**: person
**Period**: year

### e03400

**Label**: e03400
**Entity**: person
**Period**: year

### e03500

**Label**: e03500
**Entity**: person
**Period**: year

### e07240

**Label**: e07240
**Entity**: person
**Period**: year

### e07260

**Label**: e07260
**Entity**: person
**Period**: year

### e07300

**Label**: e07300
**Entity**: person
**Period**: year

### e09700

**Label**: e09700
**Entity**: person
**Period**: year

### e09800

**Label**: e09800
**Entity**: person
**Period**: year

### e09900

**Label**: e09900
**Entity**: person
**Period**: year

### e11200

**Label**: e11200
**Entity**: person
**Period**: year

### e18500

**Label**: e18500
**Entity**: person
**Period**: year

### e19200

**Label**: e19200
**Entity**: person
**Period**: year

### e19800

**Label**: e19800
**Entity**: person
**Period**: year

### e20100

**Label**: e20100
**Entity**: person
**Period**: year

### e20400

**Label**: e20400
**Entity**: person
**Period**: year

### e24515

**Label**: e24515
**Entity**: person
**Period**: year

### e24518

**Label**: e24518
**Entity**: person
**Period**: year

### e26270

**Label**: e26270
**Entity**: person
**Period**: year

### e27200

**Label**: e27200
**Entity**: person
**Period**: year

### e32800

**Label**: e32800
**Entity**: person
**Period**: year

### e58990

**Label**: e58990
**Entity**: person
**Period**: year

### e62900

**Label**: e62900
**Entity**: person
**Period**: year

### e87521

**Label**: e87521
**Entity**: person
**Period**: year

### e87530

**Label**: e87530
**Entity**: person
**Period**: year

### early_head_start

**Label**: Amount of Early Head Start benefit
**Entity**: person
**Period**: year

### early_withdrawal_penalty

**Label**: Early savings withdrawal penalty
**Entity**: person
**Period**: year
**Unit**: currency-USD

Penalties paid due to early withdrawal of savings.

### earned_income

**Label**: Earned income
**Entity**: person
**Period**: year
**Unit**: currency-USD

Income from wages or self-employment

### earned_income_last_year

**Label**: Earned income last year
**Entity**: person
**Period**: year
**Unit**: currency-USD

Prior-year income from wages or self-employment

### ebb

**Label**: Emergency Broadband Benefit amount
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

Emergency Broadband Benefit amount

### education_credit_phase_out

**Label**: Education credit phase-out
**Entity**: tax_unit
**Period**: year
**Unit**: /1

Percentage of the American Opportunity and Lifetime Learning credits which are phased out

### education_tax_credits

**Label**: Education tax credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Education tax credits non-refundable amount from Form 8863

**References**:
- https://www.law.cornell.edu/uscode/text/26/25A

### educator_expense

**Label**: Educator expenses
**Entity**: person
**Period**: year
**Unit**: currency-USD

Expenses necessary for carrying out educator-related duties.

### eitc

**Label**: Federal earned income credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/32#a

### eitc_agi_limit

**Label**: Maximum AGI to qualify for EITC
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Used for state-level policies, not EITC computations

**References**:
- https://www.law.cornell.edu/uscode/text/26/32#a

### eitc_child_count

**Label**: EITC-qualifying children
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Number of children qualifying as children for the EITC.

**References**:
- https://www.law.cornell.edu/uscode/text/26/32#c_3_D_i

### eitc_demographic_eligible

**Label**: Meets demographic eligibility for EITC
**Entity**: tax_unit
**Period**: year

**References**:
- https://www.law.cornell.edu/uscode/text/26/32#c_1_A

### eitc_eligible

**Label**: Eligible for EITC
**Entity**: tax_unit
**Period**: year

**References**:
- https://www.law.cornell.edu/uscode/text/26/32#c_1_A

### eitc_investment_income_eligible

**Label**: Meets investment income eligibility for EITC
**Entity**: tax_unit
**Period**: year

**References**:
- https://www.law.cornell.edu/uscode/text/26/32#i

### eitc_maximum

**Label**: Maximum EITC
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/32#a

### eitc_phase_in_rate

**Label**: EITC phase-in rate
**Entity**: tax_unit
**Period**: year
**Unit**: /1

Rate at which the EITC phases in with income.

### eitc_phase_out_rate

**Label**: EITC phase-out rate
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Percentage of earnings above the phase-out threshold that reduce the EITC.

### eitc_phase_out_start

**Label**: EITC phase-out start
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Earnings above this level reduce EITC entitlement.

### eitc_phased_in

**Label**: EITC phase-in amount
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

EITC maximum amount, taking into account earnings.

### eitc_reduction

**Label**: EITC reduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/32#a_2

### eitc_relevant_investment_income

**Label**: EITC-relevant investment income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### elderly_disabled_credit

**Label**: Elderly or disabled credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Schedule R credit for the elderly and the disabled

**References**:
- https://www.law.cornell.edu/uscode/text/26/22

### elderly_disabled_credit_credit_limit

**Label**: Elderly or disabled credit credit limit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Schedule R credit for the elderly and the disabled

**References**:
- https://www.law.cornell.edu/uscode/text/26/22

### elderly_disabled_credit_potential

**Label**: Potential value of the Elderly or disabled credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Schedule R credit for the elderly and the disabled

**References**:
- https://www.law.cornell.edu/uscode/text/26/22

### electric_heat_pump_clothes_dryer_expenditures

**Label**: Expenditures on electric heat pump clother dryers
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=585

### electric_load_service_center_upgrade_expenditures

**Label**: Expenditures on electric load service center upgrades
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=585

### electric_stove_cooktop_range_or_oven_expenditures

**Label**: Expenditures on electric stoves, cooktop ranges, or ovens
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=585

### electric_wiring_expenditures

**Label**: Expenditures on electric wiring
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=585

### electricity_expense

**Label**: Electricity expense
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### emp_self_emp_ratio

**Label**: Share of earnings from wages and salaries
**Entity**: person
**Period**: year
**Unit**: /1

**References**:
- https://www.law.cornell.edu/uscode/text/26/1402

### employee_medicare_tax

**Label**: employee-side health insurance payroll tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

Total liability for employee-side health insurance payroll tax.

### employee_payroll_tax

**Label**: employee-side payroll tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### employee_social_security_tax

**Label**: employee-side OASDI payroll tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

Total liability for employee-side OASDI payroll tax.

### employer_contribution_to_health_insurance_premiums_category

**Label**: Extent to which employer paid health insurance premiums
**Entity**: person
**Period**: year

### employer_medicare_tax

**Label**: Employer-side health insurance payroll tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

Total liability for employer-side health insurance payroll tax.

### employer_social_security_tax

**Label**: Employer-side OASDI payroll tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

Total liability for employer-side OASDI payroll tax.

### employment_income

**Label**: employment income
**Entity**: person
**Period**: year
**Unit**: currency-USD

Wages and salaries, including tips and commissions.

**References**:
- https://www.law.cornell.edu/uscode/text/26/3401#a

### employment_income_before_lsr

**Label**: employment income before labor supply responses
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/3401#a

### employment_income_behavioral_response

**Label**: employment income behavioral response
**Entity**: person
**Period**: year
**Unit**: currency-USD

### employment_income_last_year

**Label**: employment income last year
**Entity**: person
**Period**: year
**Unit**: currency-USD

Wages and salaries in prior year, including tips and commissions.

### energy_efficient_central_air_conditioner_expenditures

**Label**: Expenditures on energy efficient central air conditioners
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/25C#d_3_C
- https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=342

### energy_efficient_door_expenditures

**Label**: Energy efficient door expenditures
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Expenditures on exterior doors that meet version 6.0 Energy Star program requirements.

**References**:
- https://www.law.cornell.edu/uscode/text/26/25C#c_2_B
- https://www.law.cornell.edu/uscode/text/26/25C#c_3_C

### energy_efficient_home_improvement_credit

**Label**: Energy efficient home improvement credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Residential clean energy credit

**References**:
- https://www.law.cornell.edu/uscode/text/26/25C

### energy_efficient_home_improvement_credit_credit_limit

**Label**: Energy efficient home improvement credit credit limit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Residential clean energy credit

**References**:
- https://www.law.cornell.edu/uscode/text/26/25C

### energy_efficient_home_improvement_credit_potential

**Label**: Potential value of the Energy efficient home improvement credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Residential clean energy credit

**References**:
- https://www.law.cornell.edu/uscode/text/26/25C

### energy_efficient_insulation_expenditures

**Label**: Energy efficient insulation expenditures
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Expenditures on any insulation material or system which is specifically and primarily designed to reduce the heat loss or gain of a dwelling unit when installed in or on such dwelling unit.

**References**:
- https://www.law.cornell.edu/uscode/text/26/25C#c_3_A

### energy_efficient_roof_expenditures

**Label**: Energy efficient roof expenditures
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Expenditures on metal or asphalt roof or roof products that meet Energy Star program requirements and have appropriate pigmented coatings or cooling granules which are specifically and primarily designed to reduce the heat gain of such dwelling unit.

**References**:
- https://www.law.cornell.edu/uscode/text/26/25C#c_2_A
- https://www.law.cornell.edu/uscode/text/26/25C#c_3_A

### energy_efficient_window_expenditures

**Label**: Energy efficient window expenditures
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Expenditures on exterior windows (including skylights) that meet version 6.0 Energy Star program requirements.

**References**:
- https://www.law.cornell.edu/uscode/text/26/25C#c_3_B
- https://www.law.cornell.edu/uscode/text/26/25C#c_2_B

### enrolled_in_ebb

**Label**: Enrolled for Emergency Broadband Benefit
**Entity**: spm_unit
**Period**: year

Whether a SPM unit is already enrolled in the Emergency Broadband Benefit

### equiv_household_net_income

**Label**: equivalised net income
**Entity**: household
**Period**: year
**Unit**: currency-USD

### er_visit_expense

**Label**: Emergency room visit expenses
**Entity**: person
**Period**: year
**Unit**: currency-USD

### estate_income

**Label**: estate income
**Entity**: person
**Period**: year
**Unit**: currency-USD

### estate_income_would_be_qualified

**Label**: Estate income would be qualified
**Entity**: person
**Period**: year

Whether income from estates would be considered qualified business income.

**References**:
- https://www.law.cornell.edu/uscode/text/26/199A#c_3_A

### estate_tax

**Label**: Estate tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/2001#b_1

### estate_tax_before_credits

**Label**: Estate tax before credits
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/2001#b_1

### estate_tax_credit

**Label**: Estate tax credit
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/2010

### excess_payroll_tax_withheld

**Label**: Excess payroll (FICA/RRTA) tax withheld
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### excess_withheld_payroll_tax

**Label**: excess withheld payroll tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

### exemptions

**Label**: Exemptions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Personal exemptions amount after phase-out

### exemptions_count

**Label**: Number of tax exemptions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### experienced_covid_income_loss

**Label**: Experienced Covid income loss
**Entity**: spm_unit
**Period**: year

Whether the SPM unit experienced a loss of income due to COVID-19 since February 2020

### family_id

**Label**: Unique reference for this family
**Entity**: family
**Period**: year

### family_weight

**Label**: Family weight
**Entity**: family
**Period**: year

### farm_income

**Label**: farm income
**Entity**: person
**Period**: year
**Unit**: currency-USD

Income averaging for farmers and fishermen. Schedule J. Seperate from QBI and self-employment income.

**References**:
- https://www.law.cornell.edu/uscode/text/26/1301

### farm_operations_income

**Label**: farm operations income
**Entity**: person
**Period**: year
**Unit**: currency-USD

Income from active farming operations. Schedule F. Do not include this income in self-employment income.

**References**:
- https://www.law.cornell.edu/uscode/text/26/199A#c_3_A

### farm_operations_income_would_be_qualified

**Label**: Farm operations income would be qualified
**Entity**: person
**Period**: year

Whether farm operations income would be considered qualified business income.

**References**:
- https://www.law.cornell.edu/uscode/text/26/199A#c_3_A

### farm_rent_income

**Label**: farm rental income
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/1402

### farm_rent_income_would_be_qualified

**Label**: Farm rent income would be qualified
**Entity**: person
**Period**: year

Whether farm rental income would be considered qualified business income.

**References**:
- https://www.law.cornell.edu/uscode/text/26/199A#c_3_A

### fcc_fpg_ratio

**Label**: Federal poverty ratio per FCC
**Entity**: spm_unit
**Period**: year
**Unit**: /1

SPM unit's ratio of IRS gross income to their federal poverty guideline

**References**:
- https://www.law.cornell.edu/cfr/text/47/54.400#f

### fdpir

**Label**: Food Distribution Program on Indian Reservations
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

Benefit value of the Food Distribution Program on Indian Reservations

### federal_eitc_without_age_minimum

**Label**: Federal EITC without age minimum
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

The federal EITC with the minimum age condition ignored.

**References**:
- https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-7-income-tax-credits/section-10-704-effective-until-6302023-for-earned-income

### federal_state_income_tax

**Label**: Total federal and state income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### filer_adjusted_earnings

**Label**: Filer earned income adjusted for self-employment tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### filer_meets_ctc_identification_requirements

**Label**: Filer meets CTC identification requirements
**Entity**: tax_unit
**Period**: year

### filer_meets_eitc_identification_requirements

**Label**: Filer meets EITC identification requirements
**Entity**: tax_unit
**Period**: year

**References**:
- https://www.law.cornell.edu/uscode/text/26/32#c_1_E

### filing_status

**Label**: Filing status for the tax unit
**Entity**: tax_unit
**Period**: year

### flat_tax

**Label**: Flat tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Flat income tax on federal AGI or gross income.

### foreign_earned_income_exclusion

**Label**: Foreign earned income ALD
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Income earned and any housing expense in foreign countries that is excluded from adjusted gross income under 26 U.S. Code § 911.

**References**:
- https://www.law.cornell.edu/uscode/text/26/911

### foreign_tax_credit

**Label**: Foreign tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Foreign tax credit from Form 1116

### foreign_tax_credit_credit_limit

**Label**: Foreign tax credit credit limit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Foreign tax credit from Form 1116

### foreign_tax_credit_potential

**Label**: Potential value of the Foreign tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Foreign tax credit from Form 1116

### form_4972_lumpsum_distributions

**Label**: Lump-sum distributions reported on IRS Form 4972
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Lump-sum distributions reported on IRS Form 4972.

### four_year_college_student

**Label**: Person is a full time four-year college student
**Entity**: person
**Period**: year

### free_school_meals

**Label**: free school meals
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

Value of free school meals.

### free_school_meals_reported

**Label**: Free school meals (reported)
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### fsla_overtime_occupation_exemption_category

**Label**: FSLA occupation categories for overtime exemption
**Entity**: person
**Period**: year

**References**:
- https://www.law.cornell.edu/uscode/text/29/213

### fsla_overtime_premium

**Label**: premium income from overtime hours worked
**Entity**: person
**Period**: year
**Unit**: currency-USD

### fsla_overtime_salary_threshold

**Label**: FSLA applicable salary threshold to determine eligibility for overtime pay
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/cfr/text/29/541.600

### fuel_cell_property_capacity

**Label**: Capacity of purchased fuel cells
**Entity**: tax_unit
**Period**: year
**Unit**: kW

Kilowatts of capacity of qualified fuel cell properties purchased.

**References**:
- https://www.law.cornell.edu/uscode/text/26/25D#b_1

### fuel_cell_property_expenditures

**Label**: Qualified fuel cell property expenditures
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Expenditures for qualified fuel cell property installed on or in connection with a dwelling unit located in the United States and used as a principal residence by the taxpayer.

**References**:
- https://www.law.cornell.edu/uscode/text/26/25D#d_3

### fuel_oil_expense

**Label**: Fuel oil expense
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### ga_additional_standard_deduction

**Label**: Georgia additional standard deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://apps.dor.ga.gov/FillableForms/PDFViewer/Index?form=2022GA500

### ga_additions

**Label**: Georgia additions to federal adjusted gross income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://houpl.org/wp-content/uploads/2023/01/2022-IT-511_Individual_Income_Tax_-Booklet-compressed.pdf#page=14https://www.zillionforms.com/2021/I2122607361.PDF#page14

### ga_agi

**Label**: Georgia adjusted gross income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://houpl.org/wp-content/uploads/2023/01/2022-IT-511_Individual_Income_Tax_-Booklet-compressed.pdf#page=14
- https://www.zillionforms.com/2021/I2122607361.PDF#page14

### ga_cdcc

**Label**: Georgia non-refundable dependent care credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ga_deductions

**Label**: Georgia deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/georgia/2022/title-48/chapter-7/article-2/section-48-7-27/
- https://dor.georgia.gov/document/document/2022-it-511-individual-income-tax-booklet/download

### ga_exemptions

**Label**: Georgia Exemptions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://apps.dor.ga.gov/FillableForms/PDFViewer/Index?form=2022GA500
- https://advance.lexis.com/documentpage/?pdmfid=1000516&crid=2c053fd5-32c1-4cc1-86b0-36aaade9da5b&pdistocdocslideraccess=true&config=00JAA1MDBlYzczZi1lYjFlLTQxMTgtYWE3OS02YTgyOGM2NWJlMDYKAFBvZENhdGFsb2feed0oM9qoQOMCSJFX5qkd&pddocfullpath=%2Fshared%2Fdocument%2Fstatutes-legislation%2Furn%3AcontentItem%3A6348-G0H1-DYB7-W3JT-00008-00&pdcomponentid=234187&pdtocnodeidentifier=ABWAALAADAAL&ecomp=k2vckkk&prid=4862391c-e031-443f-ad52-ae86c6bb5ce2

### ga_income_tax

**Label**: Georgia income tax after refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ga_income_tax_before_non_refundable_credits

**Label**: Georgia income tax before non-refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ga_income_tax_before_refundable_credits

**Label**: Georgia income tax before refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ga_investment_in_529_plan_deduction

**Label**: Georgia investment in 529 plan deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://dor.georgia.gov/document/document/2022-it-511-individual-income-tax-booklethttps://casetext.com/regulation/georgia-administrative-code/department-560-rules-of-department-of-revenue/chapter-560-7-income-tax-division/subject-560-7-4-net-taxable-income-individual/rule-560-7-4-04-procedures-governing-the-georgia-higher-education-savings-plan

### ga_low_income_credit

**Label**: Georgia low income credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://dor.georgia.gov/document/document/2022-it-511-individual-income-tax-booklet/download

### ga_military_retirement_exclusion

**Label**: Georgia military retirement exclusion
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://dor.georgia.gov/document/document/2022-it-511-individual-income-tax-booklet/download
- https://advance.lexis.com/documentpage/?pdmfid=1000516&crid=fb5db531-a80f-4790-bddb-eefc8327ef60&config=00JAA1MDBlYzczZi1lYjFlLTQxMTgtYWE3OS02YTgyOGM2NWJlMDYKAFBvZENhdGFsb2feed0oM9qoQOMCSJFX5qkd&pddocfullpath=%2Fshared%2Fdocument%2Fstatutes-legislation%2Furn%3AcontentItem%3A65D2-CDH3-CGX8-044N-00008-00&pdcontentcomponentid=234186&pdteaserkey=sr1&pditab=allpods&ecomp=8s65kkk&earg=sr1&prid=66f02b0a-c5ae-4162-9535-127751546807

### ga_military_retirement_exclusion_eligible_person

**Label**: Eligible person for the Georgia military retirement exclusion
**Entity**: person
**Period**: year

**References**:
- https://dor.georgia.gov/document/document/2022-it-511-individual-income-tax-booklet/download
- https://advance.lexis.com/documentpage/?pdmfid=1000516&crid=fb5db531-a80f-4790-bddb-eefc8327ef60&config=00JAA1MDBlYzczZi1lYjFlLTQxMTgtYWE3OS02YTgyOGM2NWJlMDYKAFBvZENhdGFsb2feed0oM9qoQOMCSJFX5qkd&pddocfullpath=%2Fshared%2Fdocument%2Fstatutes-legislation%2Furn%3AcontentItem%3A65D2-CDH3-CGX8-044N-00008-00&pdcontentcomponentid=234186&pdteaserkey=sr1&pditab=allpods&ecomp=8s65kkk&earg=sr1&prid=66f02b0a-c5ae-4162-9535-127751546807

### ga_military_retirement_exclusion_person

**Label**: Georgia military retirement exclusion
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://dor.georgia.gov/document/document/2022-it-511-individual-income-tax-booklet/download
- https://advance.lexis.com/documentpage/?pdmfid=1000516&crid=fb5db531-a80f-4790-bddb-eefc8327ef60&config=00JAA1MDBlYzczZi1lYjFlLTQxMTgtYWE3OS02YTgyOGM2NWJlMDYKAFBvZENhdGFsb2feed0oM9qoQOMCSJFX5qkd&pddocfullpath=%2Fshared%2Fdocument%2Fstatutes-legislation%2Furn%3AcontentItem%3A65D2-CDH3-CGX8-044N-00008-00&pdcontentcomponentid=234186&pdteaserkey=sr1&pditab=allpods&ecomp=8s65kkk&earg=sr1&prid=66f02b0a-c5ae-4162-9535-127751546807

### ga_non_refundable_credits

**Label**: Georgia non-refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ga_refundable_credits

**Label**: Georgia refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ga_retirement_exclusion

**Label**: Georgia retirement exclusion
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://dor.georgia.gov/document/booklet/2021-it-511-individual-income-tax-booklet/download
- https://dor.georgia.gov/document/document/2022-it-511-individual-income-tax-booklet/download
- https://advance.lexis.com/documentpage/?pdmfid=1000516&crid=fb5db531-a80f-4790-bddb-eefc8327ef60&config=00JAA1MDBlYzczZi1lYjFlLTQxMTgtYWE3OS02YTgyOGM2NWJlMDYKAFBvZENhdGFsb2feed0oM9qoQOMCSJFX5qkd&pddocfullpath=%2Fshared%2Fdocument%2Fstatutes-legislation%2Furn%3AcontentItem%3A65D2-CDH3-CGX8-044N-00008-00&pdcontentcomponentid=234186&pdteaserkey=sr1&pditab=allpods&ecomp=8s65kkk&earg=sr1&prid=66f02b0a-c5ae-4162-9535-127751546807

### ga_retirement_exclusion_countable_earned_income

**Label**: Countable earned income for the Georgia retirement exclusion for each person
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://dor.georgia.gov/document/booklet/2021-it-511-individual-income-tax-booklet/download
- https://dor.georgia.gov/document/document/2022-it-511-individual-income-tax-booklet/download
- https://advance.lexis.com/documentpage/?pdmfid=1000516&crid=fb5db531-a80f-4790-bddb-eefc8327ef60&config=00JAA1MDBlYzczZi1lYjFlLTQxMTgtYWE3OS02YTgyOGM2NWJlMDYKAFBvZENhdGFsb2feed0oM9qoQOMCSJFX5qkd&pddocfullpath=%2Fshared%2Fdocument%2Fstatutes-legislation%2Furn%3AcontentItem%3A65D2-CDH3-CGX8-044N-00008-00&pdcontentcomponentid=234186&pdteaserkey=sr1&pditab=allpods&ecomp=8s65kkk&earg=sr1&prid=66f02b0a-c5ae-4162-9535-127751546807

### ga_retirement_exclusion_eligible_person

**Label**: Eligible person for the Georgia retirement exclusion
**Entity**: person
**Period**: year

**References**:
- https://dor.georgia.gov/document/booklet/2021-it-511-individual-income-tax-booklet/download
- https://dor.georgia.gov/document/document/2022-it-511-individual-income-tax-booklet/download
- https://advance.lexis.com/documentpage/?pdmfid=1000516&crid=fb5db531-a80f-4790-bddb-eefc8327ef60&config=00JAA1MDBlYzczZi1lYjFlLTQxMTgtYWE3OS02YTgyOGM2NWJlMDYKAFBvZENhdGFsb2feed0oM9qoQOMCSJFX5qkd&pddocfullpath=%2Fshared%2Fdocument%2Fstatutes-legislation%2Furn%3AcontentItem%3A65D2-CDH3-CGX8-044N-00008-00&pdcontentcomponentid=234186&pdteaserkey=sr1&pditab=allpods&ecomp=8s65kkk&earg=sr1&prid=66f02b0a-c5ae-4162-9535-127751546807

### ga_retirement_exclusion_person

**Label**: Georgia retirement exclusion for each person
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://dor.georgia.gov/document/booklet/2021-it-511-individual-income-tax-booklet/download
- https://dor.georgia.gov/document/document/2022-it-511-individual-income-tax-booklet/download
- https://advance.lexis.com/documentpage/?pdmfid=1000516&crid=fb5db531-a80f-4790-bddb-eefc8327ef60&config=00JAA1MDBlYzczZi1lYjFlLTQxMTgtYWE3OS02YTgyOGM2NWJlMDYKAFBvZENhdGFsb2feed0oM9qoQOMCSJFX5qkd&pddocfullpath=%2Fshared%2Fdocument%2Fstatutes-legislation%2Furn%3AcontentItem%3A65D2-CDH3-CGX8-044N-00008-00&pdcontentcomponentid=234186&pdteaserkey=sr1&pditab=allpods&ecomp=8s65kkk&earg=sr1&prid=66f02b0a-c5ae-4162-9535-127751546807

### ga_retirement_income_exclusion_retirement_income

**Label**: Georgia retirement income for the retirement income exclusion
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://dor.georgia.gov/document/booklet/2021-it-511-individual-income-tax-booklet/download
- https://dor.georgia.gov/document/document/2022-it-511-individual-income-tax-booklet/download
- https://advance.lexis.com/documentpage/?pdmfid=1000516&crid=fb5db531-a80f-4790-bddb-eefc8327ef60&config=00JAA1MDBlYzczZi1lYjFlLTQxMTgtYWE3OS02YTgyOGM2NWJlMDYKAFBvZENhdGFsb2feed0oM9qoQOMCSJFX5qkd&pddocfullpath=%2Fshared%2Fdocument%2Fstatutes-legislation%2Furn%3AcontentItem%3A65D2-CDH3-CGX8-044N-00008-00&pdcontentcomponentid=234186&pdteaserkey=sr1&pditab=allpods&ecomp=8s65kkk&earg=sr1&prid=66f02b0a-c5ae-4162-9535-127751546807

### ga_standard_deduction

**Label**: Georgia standard deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://apps.dor.ga.gov/FillableForms/PDFViewer/Index?form=2022GA500https://advance.lexis.com/documentpage/?pdmfid=1000516&crid=fb5db531-a80f-4790-bddb-eefc8327ef60&config=00JAA1MDBlYzczZi1lYjFlLTQxMTgtYWE3OS02YTgyOGM2NWJlMDYKAFBvZENhdGFsb2feed0oM9qoQOMCSJFX5qkd&pddocfullpath=%2Fshared%2Fdocument%2Fstatutes-legislation%2Furn%3AcontentItem%3A65D2-CDH3-CGX8-044N-00008-00&pdcontentcomponentid=234186&pdteaserkey=sr1&pditab=allpods&ecomp=8s65kkk&earg=sr1&prid=66f02b0a-c5ae-4162-9535-127751546807

### ga_subtractions

**Label**: Georgia subtractions from federal adjusted gross income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://houpl.org/wp-content/uploads/2023/01/2022-IT-511_Individual_Income_Tax_-Booklet-compressed.pdf#page=14https://www.zillionforms.com/2021/I2122607361.PDF#page14

### ga_taxable_income

**Label**: Georgia taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://dor.georgia.gov/it-511-individual-income-tax-booklet

### ga_withheld_income_tax

**Label**: Georgia withheld income tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

### gambling_losses

**Label**: Gambling losses
**Entity**: person
**Period**: year
**Unit**: currency-USD

### gambling_winnings

**Label**: Gambling winnings
**Entity**: person
**Period**: year
**Unit**: currency-USD

### gas_expense

**Label**: Gas expense
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### general_assistance

**Label**: general assistance
**Entity**: person
**Period**: year
**Unit**: currency-USD

### general_business_credit

**Label**: General business credit
**Entity**: person
**Period**: year
**Unit**: currency-USD

General business credit from Form 3800

**References**:
- https://www.law.cornell.edu/uscode/text/26/38

### geothermal_heat_pump_property_expenditures

**Label**: Qualified geothermal heat pump property expenditures
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Expenditures for qualified geothermal heat pump property installed on or in connection with a dwelling unit located in the United States and used as a residence by the taxpayer.

**References**:
- https://www.law.cornell.edu/uscode/text/26/25D#d_5

### gi_cash_assistance

**Label**: guaranteed income / cash assistance income
**Entity**: person
**Period**: year
**Unit**: currency-USD

Income from guaranteed income or cash assistance pilots

### greater_age_head_spouse

**Label**: Age of head or spouse of tax unit depending on which is greater
**Entity**: tax_unit
**Period**: year
**Unit**: year

Age in years of taxpayer (i.e. primary adult) or spouse (i.e. secondary adult if present), depending on which is greater. 

### has_all_usda_elderly_disabled

**Label**: Has all USDA elderly or disabled people
**Entity**: spm_unit
**Period**: year

Whether the SPM unit's members all meet USDA definitions of elderly or disabled

### has_co_denver_dhs_elderly_disabled

**Label**: Has Denver DHS elderly or disabled people
**Entity**: spm_unit
**Period**: year

Whether the SPM unit has a person who meets Denver DHS definitions of elderly or disabled

### has_disabled_spouse

**Label**: person's marriage partner in JOINT filing unit is disabled
**Entity**: person
**Period**: year

### has_esi

**Label**: Person currently has ESI
**Entity**: person
**Period**: year

### has_heating_cooling_expense

**Label**: Has heating/cooling costs
**Entity**: spm_unit
**Period**: year

### has_itin

**Label**: Has ITIN or SSN
**Entity**: person
**Period**: year

### has_marketplace_health_coverage

**Label**: Is eligible for health insurance from an ACA Marketplace plan because has no employer-sponsored health insurance coverage.
**Entity**: person
**Period**: year

### has_never_worked

**Label**: has never worked
**Entity**: person
**Period**: year

### has_phone_expense

**Label**: Has phone costs
**Entity**: spm_unit
**Period**: year

### has_qdiv_or_ltcg

**Label**: Has qualified dividends or long-term capital gains
**Entity**: tax_unit
**Period**: year

Whether this tax unit has qualified dividend income or long-term capital gains income

### has_usda_elderly_disabled

**Label**: Has USDA elderly or disabled people
**Entity**: spm_unit
**Period**: year

Whether the SPM unit has a person who meets USDA definitions of elderly or disabled

### head_earned

**Label**: Head's adjusted earnings
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### head_is_dependent_elsewhere

**Label**: Is tax-unit head a dependent elsewhere
**Entity**: tax_unit
**Period**: year

Whether the filer for this tax unit is claimed as a dependent in another tax unit.

### head_is_disabled

**Label**: Tax unit head is disabled
**Entity**: tax_unit
**Period**: year

### head_of_household_eligible

**Label**: Qualifies for head of household filing status
**Entity**: tax_unit
**Period**: year

**References**:
- https://www.law.cornell.edu/uscode/text/26/2#b

### head_spouse_count

**Label**: Head and spouse count
**Entity**: tax_unit
**Period**: year

### head_start

**Label**: Amount of Head Start benefit
**Entity**: person
**Period**: year

### health_insurance_premiums

**Label**: Health insurance premiums
**Entity**: person
**Period**: year
**Unit**: currency-USD

### health_insurance_premiums_without_medicare_part_b

**Label**: Health insurance premiums without Medicare Part B premiums
**Entity**: person
**Period**: year
**Unit**: currency-USD

### health_savings_account_ald

**Label**: Health savings account ALD
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Above-the-line deduction from gross income for health savings account expenses.

**References**:
- https://www.law.cornell.edu/uscode/text/26/223

### health_savings_account_payroll_contributions

**Label**: Health Savings Account payroll contributions
**Entity**: person
**Period**: year
**Unit**: currency-USD

### healthcare_benefit_value

**Label**: Cash equivalent of health coverage
**Entity**: household
**Period**: year
**Unit**: currency-USD

### heat_expense_included_in_rent

**Label**: Whether heating expense is included in rent payments
**Entity**: spm_unit
**Period**: year

**References**:
- https://liheapch.acf.hhs.gov/tables/FY2016/subsidize.htm

### heat_pump_expenditures

**Label**: Expenditures on heat pumps
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/25C#d_3
- https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=339#342

### heat_pump_water_heater_expenditures

**Label**: Expenditures on heat pump water heaters
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/25C#d_3
- https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=339#342

### heating_cooling_expense

**Label**: Heating and cooling expense
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### heating_expense_last_year

**Label**: Household's heating expense last year
**Entity**: spm_unit
**Period**: year

**References**:
- https://www.mass.gov/doc/fy-2025-heap-income-eligibility-benefit-chart-may-8-2025/download

### heating_expense_person

**Label**: Heating cost for each person
**Entity**: person
**Period**: year
**Unit**: currency-USD

### heating_expenses

**Label**: Tax unit heating cost
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### hhs_smi

**Label**: State Median Income (HHS)
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

SPM unit's median income as defined by the Department of Health and Human Services, based on their state and size

### hi_additions

**Label**: Hawaii additions to federal adjusted gross income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=11

### hi_agi

**Label**: Hawaii adjusted gross income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
-  https://files.hawaii.gov/tax/forms/2022/n11ins.pdf

### hi_alternative_tax_on_capital_gains

**Label**: Hawaii alternative tax on capital gains
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### hi_alternative_tax_on_capital_gains_eligible

**Label**: Eligible for the Hawaii alternative tax on capital gains
**Entity**: tax_unit
**Period**: year

### hi_casualty_loss_deduction

**Label**: Hawaii casualty loss deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=18https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=32

### hi_cdcc

**Label**: Hawaii child and dependent care credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://files.hawaii.gov/tax/legal/hrs/hrs_235.pdf#page=40

### hi_cdcc_income_floor_eligible

**Label**: Hawaii income floor eligible
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=28https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=29https://files.hawaii.gov/tax/legal/hrs/hrs_235.pdf#page=41https://files.hawaii.gov/tax/forms/2022/schx_i.pdf#page=2

### hi_cdcc_min_head_spouse_earned

**Label**: Hawaii minimum income between head and spouse for the CDCC
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=28https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=29https://files.hawaii.gov/tax/legal/hrs/hrs_235.pdf#page=41https://files.hawaii.gov/tax/forms/2022/schx_i.pdf#page=2

### hi_deductions

**Label**: Hawaii deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=15https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=20

### hi_dependent_care_benefits

**Label**: Hawaii Dependent Care Benefits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://files.hawaii.gov/tax/legal/hrs/hrs_235.pdf#page=40https://files.hawaii.gov/tax/forms/2022/schx_i.pdf#page=1https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=28

### hi_disabled_exemptions

**Label**: Hawaii disabled exemptions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=20

### hi_eitc

**Label**: Hawaii earned income tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.capitol.hawaii.gov/hrscurrent/Vol04_Ch0201-0257/HRS0235/HRS_0235-0055_0075.htm

### hi_exemptions

**Label**: Hawaii exemptions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=20

### hi_food_excise_credit

**Label**: Hawaii Food/Excise Tax Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://files.hawaii.gov/tax/legal/hrs/hrs_235.pdf#page=44

### hi_food_excise_credit_child_receiving_public_support

**Label**: Child received support for the hawaii food excise credit
**Entity**: person
**Period**: year

### hi_food_excise_credit_minor_child_amount

**Label**: Minor child amount for the Hawaii Food/Excise Tax Credit
**Entity**: tax_unit
**Period**: year

### hi_food_excise_credit_minor_child_count

**Label**: Minor child's number for the Hawaii Food/Excise Tax Credit
**Entity**: tax_unit
**Period**: year

### hi_food_excise_exemption_amount

**Label**: Exemption amount for Hawaii Food/Excise Tax Credit
**Entity**: tax_unit
**Period**: year

### hi_income_tax

**Label**: Hawaii income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### hi_income_tax_before_non_refundable_credits

**Label**: Hawaii income tax before non-refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.hawaii.gov/forms/d_18table-on/d_18table-on_p13/

### hi_income_tax_before_refundable_credits

**Label**: Hawaii income tax before refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### hi_interest_deduction

**Label**: Hawaii interest deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=17https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=32

### hi_itemized_deductions

**Label**: Hawaii itemized deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=15https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=32

### hi_medical_expense_deduction

**Label**: Hawaii medical expense deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=15https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=32

### hi_military_pay_exclusion

**Label**: Hawaii military reserve or national guard duty pay exclusion
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=13

### hi_non_refundable_credits

**Label**: Hawaii non-refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### hi_reduced_itemized_deductions

**Label**: Hawaii reduced itemized deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=15https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=32

### hi_refundable_credits

**Label**: Hawaii refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### hi_regular_exemptions

**Label**: Hawaii regular exemptions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=20

### hi_salt_deduction

**Label**: Hawaii state and local tax deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=18https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=32

### hi_standard_deduction

**Label**: Hawaii standard deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

https://files.hawaii.gov/tax/forms/2022/n11ins.pdf

### hi_subtractions

**Label**: Hawaii subtractions from federal adjusted gross income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=13

### hi_tax_credit_for_low_income_household_renters

**Label**: Hawaii low income household renters tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### hi_tax_credit_for_low_income_household_renters_eligible

**Label**: Eligible for the Hawaii low income household renters tax credit
**Entity**: tax_unit
**Period**: year

**References**:
- https://files.hawaii.gov/tax/legal/har/har_235.pdf#page=105

### hi_taxable_income

**Label**: Hawaii taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://files.hawaii.gov/tax/forms/2022/n11ins.pdf

### hi_taxable_income_for_alternative_tax

**Label**: Hawaii eligible capital gains for the alternative tax capital gains
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### hi_total_itemized_deductions

**Label**: Hawaii total itemized deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=15https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=32

### hi_withheld_income_tax

**Label**: Hawaii withheld income tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

### high_efficiency_electric_home_rebate

**Label**: High efficiency electric home rebate
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### high_efficiency_electric_home_rebate_percent_covered

**Label**: Percent of expenditures covered by high electricity home rebate
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### home_energy_audit_expenditures

**Label**: Expenditures on home energy audits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### home_mortgage_interest

**Label**: Interest paid on a home mortgage
**Entity**: person
**Period**: year
**Unit**: currency-USD

Home mortgage interest, including both reported and not reported on federal Form 1098.

### homeowners_association_fees

**Label**: Homeowners association fees
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### homeowners_insurance

**Label**: Homeowners insurance
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### hours_worked_last_week

**Label**: weekly hours worked on the previous week
**Entity**: person
**Period**: year
**Unit**: hour

### household_benefits

**Label**: benefits
**Entity**: household
**Period**: year
**Unit**: currency-USD

### household_count

**Label**: Households represented
**Entity**: household
**Period**: year

### household_count_people

**Label**: Number of people
**Entity**: household
**Period**: year
**Unit**: person

### household_health_benefits

**Label**: Household health benefits
**Entity**: household
**Period**: year
**Unit**: currency-USD

### household_id

**Label**: Unique reference for this household
**Entity**: household
**Period**: year

### household_income_ami_ratio

**Label**: Ratio of household income to area median income
**Entity**: household
**Period**: year

### household_income_decile

**Label**: household income decile
**Entity**: household
**Period**: year

Decile of household income (person-weighted)

### household_local_benefits

**Label**: Household local benefits
**Entity**: household
**Period**: year
**Unit**: currency-USD

Benefits paid by local agencies.

### household_market_income

**Label**: market income
**Entity**: household
**Period**: year
**Unit**: currency-USD

Income from non-government sources.

### household_net_income

**Label**: net income
**Entity**: household
**Period**: year
**Unit**: currency-USD

### household_net_income_including_health_benefits

**Label**: Net income including health benefits
**Entity**: household
**Period**: year
**Unit**: currency-USD

### household_refundable_state_tax_credits

**Label**: refundable State income tax credits
**Entity**: household
**Period**: year
**Unit**: currency-USD

### household_refundable_tax_credits

**Label**: refundable tax credits
**Entity**: household
**Period**: year
**Unit**: currency-USD

### household_size

**Label**: Household size
**Entity**: household
**Period**: year

### household_state_benefits

**Label**: Household state benefits
**Entity**: household
**Period**: year
**Unit**: currency-USD

Benefits paid by State agencies.

### household_state_income_tax

**Label**: household State tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### household_state_tax_before_refundable_credits

**Label**: household State tax before refundable credits
**Entity**: household
**Period**: year
**Unit**: currency-USD

### household_tax

**Label**: total tax after refundable credits
**Entity**: household
**Period**: year
**Unit**: currency-USD

Total tax liability after refundable credits.

### household_tax_before_refundable_credits

**Label**: total tax before refundable credits
**Entity**: household
**Period**: year
**Unit**: currency-USD

Total tax liability before refundable credits.

### household_vehicles_owned

**Label**: Vehicles owned
**Entity**: household
**Period**: year

### household_vehicles_value

**Label**: Value of vehicles owned
**Entity**: household
**Period**: year

### household_weight

**Label**: Household weight
**Entity**: household
**Period**: year

### housing_assistance

**Label**: Housing assistance
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

Housing assistance

### housing_cost

**Label**: Housing cost
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### housing_designated_welfare

**Label**: Housing designated welfare
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

Housing designated welfare

### hud_adjusted_income

**Label**: HUD adjusted income
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

Adjusted income for HUD programs

**References**:
- https://www.law.cornell.edu/cfr/text/24/5.611

### hud_annual_income

**Label**: HUD annual income
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

Annual income for HUD programs

**References**:
- https://www.law.cornell.edu/cfr/text/24/5.609

### hud_especially_low_income_factor

**Label**: HUD Especially Low income factor
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

Especially Low income factor for HUD programs

### hud_gross_rent

**Label**: HUD gross rent
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

Gross rent for HUD programs

**References**:
- https://www.law.cornell.edu/cfr/text/24/982.503

### hud_hap

**Label**: HUD housing assistance payment
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

HUD housing assistance payment

**References**:
- https://www.hud.gov/sites/dfiles/PIH/documents/HCV_Guidebook_Calculating_Rent_and_HAP_Payments.pdf

### hud_income_level

**Label**: HUD income level
**Entity**: spm_unit
**Period**: year

Income level for HUD programs

### hud_low_income_factor

**Label**: HUD Low income factor
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

Low income factor for HUD programs

### hud_max_subsidy

**Label**: HUD max subsidy
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

Max subsidy for HUD programs

**References**:
- https://www.law.cornell.edu/uscode/text/42/1437a#b_2_B_5

### hud_minimum_rent

**Label**: HUD minimum rent
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

Minimum Rent for HUD programs

**References**:
- https://www.law.cornell.edu/cfr/text/24/5.630#a_3

### hud_moderate_income_factor

**Label**: HUD Moderate income factor
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

Moderate income factor for HUD programs

### hud_ttp

**Label**: HUD total tenant payment
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

Total Tenant Payment

**References**:
- https://www.law.cornell.edu/cfr/text/24/5.628

### hud_ttp_adjusted_income_share

**Label**: HUD adjusted income share for total tenant payment
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

HUD adjusted income share for Total Tenant Payment

**References**:
- https://www.law.cornell.edu/cfr/text/24/5.628#a_2

### hud_ttp_income_share

**Label**: HUD income share for total tenant payment
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

HUD income share for Total Tenant Payment

**References**:
- https://www.law.cornell.edu/cfr/text/24/5.628#a_2

### hud_utility_allowance

**Label**: HUD utility allowance
**Entity**: household
**Period**: year
**Unit**: currency-USD

Utility allowance for HUD programs

**References**:
- https://www.law.cornell.edu/cfr/text/24/982.517
- https://www.lacda.org/docs/librariesprovider25/public-documents/utility-allowance/utility-allownce-2022.pdf

### hud_very_low_income_factor

**Label**: HUD Very Low income factor
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

Very Low income factor for HUD programs

### ia_additions_consolidated

**Label**: Iowa additions to taxable income for years on or after 2023
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.legis.iowa.gov/docs/code/422.7.pdf

### ia_agi

**Label**: Iowa adjusted gross income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ia_alternate_tax_consolidated

**Label**: Iowa alternate tax for years on or after 2023
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://revenue.iowa.gov/media/2754/download?inline

### ia_alternate_tax_eligible

**Label**: Iowa alternate tax eligible
**Entity**: tax_unit
**Period**: year

**References**:
- https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf#page=53https://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf#page=53

### ia_alternate_tax_indiv

**Label**: Iowa alternate tax when married couples file separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf#page=53https://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf#page=53

### ia_alternate_tax_joint

**Label**: Iowa alternate tax when married couples file jointly
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf#page=53https://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf#page=53

### ia_alternate_tax_unit

**Label**: Iowa alternate tax calculated using worksheet
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf#page=53https://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf#page=53

### ia_amt_indiv

**Label**: Iowa alternative minimum tax when married couples file separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf#page=55https://tax.iowa.gov/sites/default/files/2021-12/IA6251%2841131%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf#page=55https://tax.iowa.gov/sites/default/files/2023-01/IA6251%2841131%29.pdf

### ia_amt_joint

**Label**: Iowa alternative minimum tax when married couples file jointly
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf#page=55https://tax.iowa.gov/sites/default/files/2021-12/IA6251%2841131%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf#page=55https://tax.iowa.gov/sites/default/files/2023-01/IA6251%2841131%29.pdf

### ia_base_tax_indiv

**Label**: Iowa base tax when married couples file separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf#page=53https://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf#page=53

### ia_base_tax_joint

**Label**: Iowa base tax when married couples file jointly
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf#page=53https://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf#page=53

### ia_basic_deduction_indiv

**Label**: Iowa deduction of either standard or itemized deductions when married couples file separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf

### ia_basic_deduction_joint

**Label**: Iowa deduction of either standard or itemized deductions when married couples file jointly
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf

### ia_cdcc

**Label**: Iowa child/dependent care credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdf#page=2https://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf#page=86https://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdf#page=2https://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf#page=86

### ia_eitc

**Label**: Iowa earned income tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdf#page=2https://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf#page=87https://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdf#page=2https://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf#page=87

### ia_exemption_credit

**Label**: Iowa exemption credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.iowa.gov/sites/default/files/2021-12/IA6251%2841131%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/IA6251%2841131%29.pdf

### ia_fedtax_deduction

**Label**: Iowa deduction for selected components of federal income tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf#page=41https://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf#page=41

### ia_files_separately

**Label**: married couple files separately on Iowa tax return
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf

### ia_gross_income

**Label**: Iowa gross income
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf

### ia_income_adjustments

**Label**: Iowa income adjustments
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf

### ia_income_tax

**Label**: Iowa income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf

### ia_income_tax_before_credits

**Label**: Iowa income tax before credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf

### ia_income_tax_before_refundable_credits

**Label**: Iowa income tax before refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf#page=60https://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf#page=60

### ia_income_tax_consolidated

**Label**: Iowa income tax for years on or after 2023
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://revenue.iowa.gov/media/2746/download?inline
- https://www.legis.iowa.gov/docs/code/422.7.pdf

### ia_income_tax_indiv

**Label**: Iowa income tax when married couples file separately
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf

### ia_income_tax_joint

**Label**: Iowa income tax when married couples file jointly
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf

### ia_is_tax_exempt

**Label**: whether or not exempt from Iowa income tax because of low income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf#page=37https://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf#page=37

### ia_itemized_deductions

**Label**: Iowa itemized deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ia_itemized_deductions_indiv

**Label**: Iowa itemized deductions for individual couples
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf

### ia_itemized_deductions_joint

**Label**: Iowa itemized deductions for joint couples
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf

### ia_itemized_deductions_unit

**Label**: Iowa itemized deductions for tax unit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf

### ia_modified_income

**Label**: Iowa modified income used in tax-exempt and alternate-tax calculations
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf#page=55https://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf#page=55

### ia_net_income

**Label**: Iowa net income
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf

### ia_nonrefundable_credits

**Label**: Iowa nonrefundable income tax credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf

### ia_pension_exclusion

**Label**: Iowa pension exclusion
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf#page=26https://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf#page=26

### ia_pension_exclusion_eligible

**Label**: Eligible for the Iowa pension exclusion
**Entity**: person
**Period**: year

**References**:
- https://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf#page=26https://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf#page=26

### ia_prorate_fraction

**Label**: Iowa joint amount proration fraction
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf

### ia_qbi_deduction

**Label**: Iowa deduction that is fraction of federal qualified business income deduction
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf

### ia_reduced_tax

**Label**: Iowa income tax reduced amount for single tax units
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf#page=60https://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf#page=60

### ia_refundable_credits

**Label**: Iowa refundable income tax credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf

### ia_regular_tax_consolidated

**Label**: Iowa regular tax for years on or after 2023
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://revenue.iowa.gov/media/2748/download?inline

### ia_regular_tax_indiv

**Label**: Iowa regular tax calculated using income tax rate schedule when married couples file separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf#page=53https://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf#page=53https://tax.iowa.gov/sites/default/files/2023-11/IA1041Inst%2863002%29.pdf#page=4

### ia_regular_tax_joint

**Label**: Iowa regular tax calculated using income tax rate schedule when married couples file jointly
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf#page=53https://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf#page=53https://tax.iowa.gov/sites/default/files/2023-11/IA1041Inst%2863002%29.pdf#page=4

### ia_reportable_social_security

**Label**: Iowa reportable social security benefits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf#page=11https://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf#page=10

### ia_standard_deduction

**Label**: Iowa standard deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ia_standard_deduction_indiv

**Label**: Iowa standard deduction when married couples file separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf

### ia_standard_deduction_joint

**Label**: Iowa standard deduction when married couples file jointly
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf

### ia_subtractions_consolidated

**Label**: Iowa subtractions from taxable income for years on or after 2023
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.legis.iowa.gov/docs/code/422.7.pdf

### ia_taxable_income

**Label**: Iowa taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ia_taxable_income_consolidated

**Label**: Iowa taxable income for years on or after 2023
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://revenue.iowa.gov/media/2746/download?inline
- https://www.legis.iowa.gov/docs/code/422.7.pdf

### ia_taxable_income_indiv

**Label**: Iowa taxable income when married couple file separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf

### ia_taxable_income_joint

**Label**: Iowa taxable income when married couple file jointly
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdfhttps://tax.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdfhttps://tax.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf

### ia_taxable_income_modifications_consolidated

**Label**: Iowa modifications to taxable income for years on or after 2023
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://revenue.iowa.gov/media/2746/download?inline
- https://www.legis.iowa.gov/docs/code/422.7.pdf

### ia_withheld_income_tax

**Label**: Iowa withheld income tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

### id_additions

**Label**: Idaho additions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### id_aged_or_disabled_credit

**Label**: Idaho aged or disabled credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### id_aged_or_disabled_credit_eligible_person

**Label**: Eligible person for the Idaho aged or disabled credit
**Entity**: person
**Period**: year

### id_aged_or_disabled_deduction

**Label**: Idaho aged or disabled deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### id_aged_or_disabled_deduction_eligible_person

**Label**: Eligible person for the Idaho aged or disabled deduction
**Entity**: person
**Period**: year

### id_agi

**Label**: Idaho adjusted gross income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### id_capital_gains_deduction

**Label**: Idaho capital gains deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://legislature.idaho.gov/statutesrules/idstat/title63/t63ch30/sect63-3022h/

### id_cdcc_limit

**Label**: Federal CDCC-relevant care expense limit for Idaho tax purposes
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.idaho.gov/governance/statutes/irc/

### id_ctc

**Label**: Idaho Child Tax Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### id_deductions

**Label**: Idaho deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://legislature.idaho.gov/statutesrules/idstat/Title63/T63CH30/SECT63-3022/
- https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_03-01-2023.pdf#page=8

### id_grocery_credit

**Label**: Idaho grocery credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/idaho/2022/title-63/chapter-30/section-63-3024a/
- https://tax.idaho.gov/wp-content/uploads/forms/EFO00089/EFO00089_12-30-2022.pdf#page=7

### id_grocery_credit_aged

**Label**: Idaho aged grocery credit
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/idaho/2022/title-63/chapter-30/section-63-3024a/
- https://tax.idaho.gov/wp-content/uploads/forms/EFO00089/EFO00089_12-30-2022.pdf#page=7

### id_grocery_credit_base

**Label**: Idaho base grocery credit
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/idaho/2022/title-63/chapter-30/section-63-3024a/
- https://tax.idaho.gov/wp-content/uploads/forms/EFO00089/EFO00089_12-30-2022.pdf#page=7

### id_grocery_credit_qualified_months

**Label**: Months qualified for the Idaho grocery credit
**Entity**: person
**Period**: year

**References**:
- https://law.justia.com/codes/idaho/2022/title-63/chapter-30/section-63-3024a/
- https://tax.idaho.gov/wp-content/uploads/forms/EFO00089/EFO00089_12-30-2022.pdf#page=7

### id_grocery_credit_qualifying_month

**Label**: Qualifies for the Idaho grocery credit in the given month
**Entity**: person
**Period**: month

**References**:
- https://law.justia.com/codes/idaho/2022/title-63/chapter-30/section-63-3024a/
- https://tax.idaho.gov/wp-content/uploads/forms/EFO00089/EFO00089_12-30-2022.pdf#page=7

### id_household_and_dependent_care_expense_deduction

**Label**: Idaho household and dependent care expense deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### id_income_tax

**Label**: Idaho income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### id_income_tax_before_non_refundable_credits

**Label**: Idaho income tax before non-refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### id_income_tax_before_refundable_credits

**Label**: Idaho income tax before refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### id_income_tax_liable

**Label**: Liable to pay income taxes in Idaho
**Entity**: tax_unit
**Period**: year

**References**:
- https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_11-15-2021.pdf#page=10

### id_itemized_deductions

**Label**: Idaho itemized deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_03-01-2023.pdf#page=8
- https://tax.idaho.gov/wp-content/uploads/forms/EFO00089/EFO00089_09-23-2021.pdf

### id_non_refundable_credits

**Label**: Idaho non-refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### id_pbf

**Label**: Idaho permanent building tax
**Entity**: tax_unit
**Period**: year

**References**:
- https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_11-15-2021.pdf#page=10

### id_pbf_liable

**Label**: Liable for the Idaho permanent building fund tax
**Entity**: tax_unit
**Period**: year

**References**:
- https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_11-15-2021.pdf#page=3

### id_receives_aged_or_disabled_credit

**Label**: Filer receives the Idaho aged or disabled credit over the deduction
**Entity**: tax_unit
**Period**: year

**References**:
- https://legislature.idaho.gov/statutesrules/idstat/title63/t63ch30/sect63-3025d/

### id_refundable_credits

**Label**: Idaho refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### id_retirement_benefits_deduction

**Label**: Idaho retirement benefits deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://legislature.idaho.gov/statutesrules/idstat/title63/t63ch30/sect63-3022a/
- https://tax.idaho.gov/wp-content/uploads/forms/EFO00088/EFO00088_03-01-2023.pdf

### id_retirement_benefits_deduction_eligible_person

**Label**: Eligible person for the Idaho retirement benefits deduction
**Entity**: person
**Period**: year

**References**:
- https://legislature.idaho.gov/statutesrules/idstat/title63/t63ch30/sect63-3022a/

### id_retirement_benefits_deduction_relevant_income

**Label**: Idaho retirement benefits deduction income sources
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://legislature.idaho.gov/statutesrules/idstat/title63/t63ch30/sect63-3022a/

### id_salt_deduction

**Label**: Idaho SALT deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_03-01-2023.pdf#page=8

### id_subtractions

**Label**: Idaho subtractions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### id_taxable_income

**Label**: Idaho taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Idaho taxable income

**References**:
- https://tax.idaho.gov/wp-content/uploads/forms/EFO00089/EFO00089_12-30-2022.pdf#page=1

### id_withheld_income_tax

**Label**: Idaho withheld income tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

### il_aabd

**Label**: Illinois Aid to the Aged, Blind or Disabled (AABD) cash benefit
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

### il_aabd_aged_blind_disabled_person

**Label**: Aged, blind, or disabled person for Illinois Aid to the Aged, Blind or Disabled (AABD)
**Entity**: person
**Period**: month

**References**:
- https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-113.30
- https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-113.40
- https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-113.50

### il_aabd_area

**Label**: Illinois Aid to the Aged, Blind or Disabled (AABD) area
**Entity**: household
**Period**: month

**References**:
- https://www.dhs.state.il.us/page.aspx?item=12668

### il_aabd_asset_value_eligible

**Label**: Eligible for Illinois Aid to the Aged, Blind or Disabled (AABD) due to asset
**Entity**: spm_unit
**Period**: month

**References**:
- https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-113.142

### il_aabd_child_care_expense_exemption

**Label**: Illinois Aid to the Aged, Blind or Disabled (AABD) childcare expense exemption
**Entity**: person
**Period**: month

**References**:
- https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-113.125

### il_aabd_countable_assets

**Label**: Illinois Aid to the Aged, Blind or Disabled (AABD) countable assets
**Entity**: spm_unit
**Period**: month

**References**:
- https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-113.140

### il_aabd_countable_income

**Label**: Illinois Aid to the Aged, Blind or Disabled (AABD) countable income
**Entity**: person
**Period**: month
**Unit**: currency-USD

### il_aabd_countable_unearned_income

**Label**: Illinois Aid to the Aged, Blind or Disabled (AABD) countable unearned income
**Entity**: person
**Period**: month

**References**:
- https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-113.120

### il_aabd_countable_vehicle_value

**Label**: Illinois Aid to the Aged, Blind or Disabled (AABD) countable vehicles value
**Entity**: spm_unit
**Period**: month

**References**:
- https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-113.141

### il_aabd_earned_income_after_exemption_person

**Label**: Illinois Aid to the Aged, Blind or Disabled (AABD) earned income after exemption per person
**Entity**: person
**Period**: month

**References**:
- https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-113.120

### il_aabd_eligible_person

**Label**: Eligible person for Illinois Aid to the Aged, Blind or Disabled (AABD)
**Entity**: person
**Period**: month

### il_aabd_expense_exemption_person

**Label**: Illinois Aid to the Aged, Blind or Disabled (AABD) expense exemption per person
**Entity**: person
**Period**: month
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-113.125

### il_aabd_financial_eligible_person

**Label**: Illinois Aid to the Aged, Blind or Disabled (AABD) eligible person due to financial criteria
**Entity**: person
**Period**: month

### il_aabd_flat_exemption_excess_over_unearned_income

**Label**: Illinois Aid to the Aged, Blind or Disabled (AABD) flat exemption excess over unearned income
**Entity**: person
**Period**: month

### il_aabd_grant_amount

**Label**: Illinois Aid to the Aged, Blind or Disabled (AABD) grant amount
**Entity**: person
**Period**: month
**Unit**: currency-USD

**References**:
- https://www.dhs.state.il.us/page.aspx?item=15948

### il_aabd_gross_earned_income

**Label**: Illinois Aid to the Aged, Blind or Disabled (AABD) gross earned income
**Entity**: person
**Period**: month
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-113.112

### il_aabd_gross_unearned_income

**Label**: Illinois Aid to the Aged, Blind or Disabled (AABD) gross unearned income
**Entity**: person
**Period**: month
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-113.100

### il_aabd_immigration_status_eligible_person

**Label**: Eligible person for Illinois Aid to the Aged, Blind or Disabled (AABD) based on immigration status
**Entity**: person
**Period**: month

**References**:
- https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-113.10

### il_aabd_institutional_status

**Label**: Illinois AABD Institutional Status
**Entity**: spm_unit
**Period**: month

**References**:
- https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-113.70

### il_aabd_is_bedfast

**Label**: Whether the person is a bedfast client under the Illinois Aid to the Aged, Blind or Disabled (AABD)
**Entity**: person
**Period**: month

**References**:
- https://www.dhs.state.il.us/page.aspx?item=15913

### il_aabd_need_standard_person

**Label**: Illinois Aid to the Aged, Blind or Disabled (AABD) need standard for each person
**Entity**: person
**Period**: month
**Unit**: currency-USD

**References**:
- https://rockfordha.org/wp-content/uploads/2020/04/Public-Benefits-Quick-Reference-Guide-Updated.pdf#page=1

### il_aabd_non_financial_eligible_person

**Label**: Eligible person for Illinois Aid to the Aged, Blind or Disabled (AABD)
**Entity**: person
**Period**: month

**References**:
- https://www.law.cornell.edu/regulations/illinois/title-89/part-113/subpart-B

### il_aabd_person

**Label**: Illinois Aid to the Aged, Blind or Disabled (AABD) cash benefit per person
**Entity**: person
**Period**: month
**Unit**: currency-USD

### il_aabd_personal_allowance

**Label**: Illinois Aid to the Aged, Blind or Disabled (AABD) personal allowance
**Entity**: person
**Period**: month
**Unit**: currency-USD

**References**:
- https://www.dhs.state.il.us/page.aspx?item=15913

### il_aabd_shelter_allowance

**Label**: Illinois Aid to the Aged, Blind or Disabled (AABD) shelter allowance
**Entity**: person
**Period**: month
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-113.248

### il_aabd_utility_allowance

**Label**: Illinois Aid to the Aged, Blind or Disabled (AABD) utility allowance
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-113.259

### il_aabd_utility_allowance_person

**Label**: Illinois Aid to the Aged, Blind or Disabled (AABD) utility allowance per person
**Entity**: person
**Period**: month
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-113.259

### il_aabd_vehicle_is_essential

**Label**: Whether the household has a vehicle which is considered essential under the Illinois Aid to the Aged, Blind or Disabled (AABD)
**Entity**: spm_unit
**Period**: month

**References**:
- https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-113.141

### il_aged_blind_exemption

**Label**: IL aged and blind exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### il_bap_eligible

**Label**: Eligible person for the Illinois Chicago Department of Aging Benefit Access Program (BAP)
**Entity**: person
**Period**: year

**References**:
- https://ilaging.illinois.gov/benefitsaccess.html

### il_base_income

**Label**: IL base income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### il_base_income_additions

**Label**: IL base income additions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### il_base_income_subtractions

**Label**: IL base income subtractions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### il_ccap_countable_income

**Label**: Illinois Child Care Assistance Program (CCAP) countable income
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-50.235

### il_ccap_eligible

**Label**: Eligible for Illinois Child Care Assistance Program (CCAP)
**Entity**: spm_unit
**Period**: month

**References**:
- https://www.dhs.state.il.us/page.aspx?item=104995

### il_ccap_eligible_child

**Label**: Eligible child for Illinois Child Care Assistance Program (CCAP)
**Entity**: person
**Period**: month

**References**:
- https://www.dhs.state.il.us/page.aspx?item=104995

### il_ccap_enrolled

**Label**: Whether the family is currently enrolled in Illinois Child Care Assistance Program (CCAP)
**Entity**: spm_unit
**Period**: month

### il_ccap_immigration_status_eligible_person

**Label**: Eligible person for Illinois Child Care Assistance Program (CCAP) based on immigration status
**Entity**: person
**Period**: month

**References**:
- https://www.dhs.state.il.us/page.aspx?item=46885

### il_ccap_income_eligible

**Label**: Eligible for Illinois Child Care Assistance Program (CCAP) due to income
**Entity**: spm_unit
**Period**: month

**References**:
- https://www.dhs.state.il.us/page.aspx?item=118832

### il_ccap_parent_meets_working_requirements

**Label**: Parent meets Illinois Child Care Assistance Program (CCAP) working requirements
**Entity**: spm_unit
**Period**: month

**References**:
- https://www.dhs.state.il.us/page.aspx?item=104995

### il_cta_benefit

**Label**: Illinois Chicago Transit Authority benefit amount
**Entity**: person
**Period**: month
**Unit**: currency-USD

**References**:
- https://www.transitchicago.com/fares/

### il_cta_children_reduced_fare_eligible

**Label**: Eligible for the Illinois Chicago Transit Authority children reduced fare
**Entity**: person
**Period**: year

**References**:
- https://www.transitchicago.com/reduced-fare-programs/#kids

### il_cta_free_ride_benefit

**Label**: Illinois Chicago Transit Authority Free Ride Program benefit
**Entity**: person
**Period**: month
**Unit**: currency-USD

**References**:
- https://www.transitchicago.com/fares/

### il_cta_free_ride_eligible

**Label**: Eligible for the Illinois Chicago Transit Authority Free Ride Program
**Entity**: person
**Period**: year

**References**:
- https://www.transitchicago.com/reduced-fare-programs/#free

### il_cta_military_service_pass_eligible

**Label**: Eligible for the Illinois Chicago Transit Authority military service pass
**Entity**: person
**Period**: year

**References**:
- https://www.transitchicago.com/military/

### il_cta_reduced_fare_benefit

**Label**: Illinois Chicago Transit Authority Reduced Fare Program benefit
**Entity**: person
**Period**: month
**Unit**: currency-USD

**References**:
- https://www.transitchicago.com/fares/

### il_cta_reduced_fare_eligible

**Label**: Eligible for the Illinois Chicago Transit Authority Reduced Fare Program
**Entity**: person
**Period**: year

**References**:
- https://www.transitchicago.com/reduced-fare-programs/

### il_cta_rta_reduced_fare_eligible

**Label**: Eligible for the Illinois Chicago Transit Authority RTA reduced fare
**Entity**: person
**Period**: year

**References**:
- https://www.transitchicago.com/reduced-fare-programs/#rtareduced

### il_cta_student_reduced_fare_eligible

**Label**: Eligible for the Illinois Chicago Transit Authority student reduced fare
**Entity**: person
**Period**: year

**References**:
- https://www.transitchicago.com/reduced-fare-programs/#students

### il_ctc

**Label**: Illinois Child Tax Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ilga.gov/legislation/fulltext.asp?DocName=&SessionId=112&GA=103&DocTypeId=HB&DocNum=4917&GAID=17&LegID=152789&SpecSess=&Session=

### il_dependent_exemption

**Label**: Illinois dependent exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### il_eitc

**Label**: IL EITC
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www2.illinois.gov/rev/programs/EIC/Pages/default.aspx

### il_income_tax

**Label**: Illinois income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### il_income_tax_before_non_refundable_credits

**Label**: IL income tax before credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### il_income_tax_before_refundable_credits

**Label**: Illinois income tax before refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### il_is_exemption_eligible

**Label**: Whether this tax unit is eligible for any exemptions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### il_k12_education_expense_credit

**Label**: Illinois K-12 Education Expense Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### il_nonrefundable_credits

**Label**: Illinois non-refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### il_pass_through_entity_tax_credit

**Label**: IL Pass-Through Entity Tax Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### il_pass_through_withholding

**Label**: IL Pass-Through Withholding
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### il_personal_exemption

**Label**: Illinois personal exemption amount
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### il_personal_exemption_eligibility_status

**Label**: Whether The Tax Unit Is Eligible For The Illinois Personal Exemption
**Entity**: tax_unit
**Period**: year

### il_property_tax_credit

**Label**: Illinois Property Tax Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### il_refundable_credits

**Label**: Illinois refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### il_schedule_m_additions

**Label**: IL Schedule M additions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www2.illinois.gov/rev/forms/incometax/Documents/currentyear/individual/il-1040-schedule-m.pdf

### il_schedule_m_subtractions

**Label**: IL Schedule M deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www2.illinois.gov/rev/forms/incometax/Documents/currentyear/individual/il-1040-schedule-m.pdf

### il_tanf

**Label**: Illinois Temporary Assistance for Needy Families (TANF)
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-112.250

### il_tanf_assistance_unit_fpg

**Label**: Illinois TANF assistance unit's federal poverty guideline
**Entity**: spm_unit
**Period**: month

### il_tanf_assistance_unit_size

**Label**: Illinois Temporary Assistance for Needy Families (TANF) assistance unit size
**Entity**: spm_unit
**Period**: month

**References**:
- https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-112.300

### il_tanf_childcare_deduction

**Label**: Illinois Temporary Assistance for Needy Families (TANF) child care deduction 
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-112.143

### il_tanf_countable_earned_income_for_grant_calculation

**Label**: Illinois Temporary Assistance for Needy Families (TANF) countable earned income for grant calculation
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://www.dhs.state.il.us/page.aspx?item=15864

### il_tanf_countable_earned_income_for_initial_eligibility

**Label**: Illinois Temporary Assistance for Needy Families (TANF) countable earned income for initial eligibility
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://www.dhs.state.il.us/page.aspx?item=15864

### il_tanf_countable_gross_earned_income

**Label**: Illinois Temporary Assistance for Needy Families (TANF) countable gross earned income
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

### il_tanf_countable_income_for_grant_calculation

**Label**: Illinois Temporary Assistance for Needy Families (TANF) countable income for grant calculation
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-112.155

### il_tanf_countable_income_for_initial_eligibility

**Label**: Illinois Temporary Assistance for Needy Families (TANF) countable income at application
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-112.155

### il_tanf_countable_unearned_income

**Label**: Illinois Temporary Assistance for Needy Families (TANF) countable unearned income
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- http://law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-112.101

### il_tanf_demographic_eligible_person

**Label**: Eligible person for Illinois Temporary Assistance for Needy Families (TANF) based on demographics
**Entity**: person
**Period**: month

**References**:
- https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-112.60

### il_tanf_eligible

**Label**: Eligible for Illinois Temporary Assistance for Needy Families (TANF)
**Entity**: spm_unit
**Period**: month

**References**:
- https://www.dhs.state.il.us/page.aspx?item=30358

### il_tanf_eligible_child

**Label**: Eligible child for Illinois Temporary Assistance for Needy Families (TANF) based on demographics
**Entity**: person
**Period**: month

**References**:
- https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-112.60

### il_tanf_gross_earned_income

**Label**: Illinois Temporary Assistance for Needy Families (TANF) gross earned income
**Entity**: person
**Period**: month
**Unit**: currency-USD

### il_tanf_gross_unearned_income

**Label**: Illinois Temporary Assistance for Needy Families (TANF) gross unearned income
**Entity**: person
**Period**: month
**Unit**: currency-USD

### il_tanf_immigration_status_eligible_person

**Label**: Eligible person for the Illinois TANF based on immigration status
**Entity**: person
**Period**: month

**References**:
- https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-112.10

### il_tanf_income_eligible

**Label**: Eligible for Illinois Temporary Assistance for Needy Families (TANF) due to income
**Entity**: spm_unit
**Period**: month

**References**:
- https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-112.155

### il_tanf_initial_employment_deduction_person

**Label**: Illinois Temporary Assistance for Needy Families (TANF) initial employment deduction per person
**Entity**: person
**Period**: month
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-112.141

### il_tanf_non_financial_eligible

**Label**: Eligible for Illinois Temporary Assistance for Needy Families (TANF) due to non financial requirements
**Entity**: spm_unit
**Period**: month

**References**:
- https://www.dhs.state.il.us/page.aspx?item=30358

### il_tanf_payment_eligible_child

**Label**: Eligible child for Illinois Temporary Assistance for Needy Families (TANF) payment
**Entity**: person
**Period**: month

**References**:
- https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-112.300

### il_tanf_payment_eligible_parent

**Label**: Eligible parent for Illinois Temporary Assistance for Needy Families (TANF) payment
**Entity**: person
**Period**: month

**References**:
- https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-112.300

### il_tanf_payment_eligible_requirements

**Label**: Eligible requirements for Illinois Temporary Assistance for Needy Families (TANF) payment
**Entity**: person
**Period**: month

**References**:
- https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-112.10
- https://www.dhs.state.il.us/page.aspx?item=13251

### il_tanf_payment_level_for_grant_calculation

**Label**: Illinois Temporary Assistance for Needy Families (TANF) payment level for grant calculation
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-112.251

### il_tanf_payment_level_for_initial_eligibility

**Label**: Illinois Temporary Assistance for Needy Families (TANF) payment level for initial eligibility
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-112.251

### il_taxable_income

**Label**: IL taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### il_total_exemptions

**Label**: IL total exemption allowance
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### il_total_tax

**Label**: Illinois total tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### il_use_tax

**Label**: IL use tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### il_withheld_income_tax

**Label**: Illinois withheld income tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

### illicit_income

**Label**: illicit income
**Entity**: person
**Period**: year
**Unit**: currency-USD

Income from bribes, corrupt gifts or other illegal activities.

### imaging_expense

**Label**: Imaging expenses
**Entity**: person
**Period**: year
**Unit**: currency-USD

### immigration_status

**Label**: U.S. immigration status as an enumeration type
**Entity**: person
**Period**: year

### immigration_status_str

**Label**: ImmigrationStatus enumeration type as an all-upper-case string
**Entity**: person
**Period**: year

### in_add_backs

**Label**: Indiana add-backs
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-1-3.5

### in_additional_exemptions

**Label**: Indiana additional exemptions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-1-3.5

### in_adoption_exemption

**Label**: Indiana adoption exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/indiana/title-6/article-3/chapter-1/section-6-3-1-3-5/

### in_aged_blind_exemptions

**Label**: Indiana exemptions for aged and or blind
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-1-3.5

### in_aged_low_agi_exemptions

**Label**: Indiana aged and low-AGI exemptions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-1-3.5

### in_agi

**Label**: Indiana adjusted gross income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-1-3.5

### in_agi_tax

**Label**: Indiana adjusted gross income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-2-1

### in_base_exemptions

**Label**: Indiana base exemptions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-1-3.5

### in_bonus_depreciation_add_back

**Label**: Indiana bonus depreciation add back
**Entity**: tax_unit
**Period**: year

Income (or loss) included in Federal AGI under Section 168(k)'s bonus depreciation less the amount that would have been included without it.

**References**:
- http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-1-3.5

### in_county_tax

**Label**: Indiana county tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-2-1

### in_deductions

**Label**: Indiana deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3

### in_deep_poverty

**Label**: in deep poverty
**Entity**: spm_unit
**Period**: year

Whether a household is in deep poverty.

### in_denver

**Label**: Is in Denver County
**Entity**: household
**Period**: year

### in_eitc

**Label**: Indiana earned income tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://iga.in.gov/laws/2021/ic/titles/6#6-3.1-21

### in_eitc_eligible

**Label**: Indiana earned income tax credit eligibility status
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://iga.in.gov/laws/2021/ic/titles/6#6-3.1-21

### in_exemptions

**Label**: Indiana exemptions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-1-3.5

### in_healthcare_sharing_deduction

**Label**: Indiana healthcare sharing ministry deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Healthcare sharing expenses paid by a qualified individual for membership in a health care sharing ministry allowable for deduction in Indiana.

**References**:
- https://iga.in.gov/laws/2024/ic/titles/6#6-3-2-28

### in_homeowners_property_tax_deduction

**Label**: Indiana homeowner's residential property tax deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3

### in_income_tax

**Label**: Indiana income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- http://iga.in.gov/legislative/laws/2021/ic/titles/6

### in_income_tax_before_refundable_credits

**Label**: Indiana income tax before refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- http://iga.in.gov/legislative/laws/2021/ic/titles/6

### in_is_qualifying_dependent_child

**Label**: Indiana additional exemption qualifying dependent child
**Entity**: person
**Period**: year

**References**:
- http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-1-3.5

### in_la

**Label**: Is in Los Angeles County
**Entity**: household
**Period**: year

### in_military_service_deduction

**Label**: Indiana military service deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-2-4

### in_nol

**Label**: Indiana NOL
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Net operating losses allowable for deduction in Indiana.

**References**:
- http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-2-2.5

### in_nol_add_back

**Label**: Indiana net operating loss add back
**Entity**: tax_unit
**Period**: year

Add back for net operating losses reported on federal Schedule 1.

**References**:
- http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-1-3.5

### in_nonpublic_school_deduction

**Label**: Indiana nonpublic school expenditures deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-2-22

### in_nyc

**Label**: Is in NYC
**Entity**: household
**Period**: year

### in_oos_municipal_obligation_interest_add_back

**Label**: Indiana out-of-state municipal obligation interest add back
**Entity**: tax_unit
**Period**: year

Add back for interest earned from a direct obligation of a state or political subdivision other than Indiana for obligations purchased after Dec. 31, 2011.

**References**:
- http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-1-3.5

### in_other_add_backs

**Label**: Indiana other add backs
**Entity**: tax_unit
**Period**: year

Other add backs including those for Conformity, Employer Student Loan Payment, Meal Deductions, Student Loan Discharges, Excess Federal Interest Deduction Modification, Federal Repatriated Dividend Deductions, Qualified Preferred Stock, and Catch-Up Modifications.

**References**:
- http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-1-3.5

### in_other_deductions

**Label**: Indiana other deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Other deductions available in Indiana including those for civil service annuities, disability retirement, government or civic group capital contributions, human services for Medicaid recipients,  infrastructure fund gifts, indiana lottery winings annuity, Indiana partnership long-term care policy premiums, military retirement income or survivor's benefits, National Guard and reserve component members, Olympic/Paralymic medal winners, qualified patents income eemption, railroad unemployment and sickness benefits, repayment of previously taxed income deductions, COVID-related employee retention credit dissalowed expenses, and Indiana-only tax-exempt bonds.

**References**:
- http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-2

### in_out_of_home_care_facility

**Label**: Is in a nonmedical out of home care facility
**Entity**: person
**Period**: year

### in_poverty

**Label**: in poverty
**Entity**: spm_unit
**Period**: year

Whether a household is in poverty.

### in_qualifying_child_count

**Label**: Indiana qualifying dependent child count
**Entity**: tax_unit
**Period**: year
**Unit**: child

Number of qualifying children for the IN additional exemption.

**References**:
- http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-1-3.5

### in_refundable_credits

**Label**: Indiana refundable income tax credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://iga.in.gov/laws/2021/ic/titles/6#6-3.1

### in_renters_deduction

**Label**: Indiana renter's deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-2-6

### in_riv

**Label**: Is in Riverside County
**Entity**: household
**Period**: year

### in_section_179_expense_add_back

**Label**: Indiana Section 179 Expense Add Back
**Entity**: tax_unit
**Period**: year

Federal IRC Section 179 expenses less IRC Section 179 expenses if they had been calculated with a $25,000 ceiling.

**References**:
- http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-1-3.5

### in_tax_add_back

**Label**: Indiana tax add back
**Entity**: tax_unit
**Period**: year

Add backs for certain taxes deducted from federal Schedules C, C-EZ, E and/or F.

**References**:
- http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-1-3.5

### in_unemployment_compensation_deduction

**Label**: Indiana unemployment compensation deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-2-10

### in_unified_elderly_tax_credit

**Label**: Indiana unified elderly tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://iga.in.gov/laws/2021/ic/titles/6#6-3-3-9https://iga.in.gov/laws/2022/ic/titles/6#6-3-3-9

### in_use_tax

**Label**: Indiana use tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://iga.in.gov/laws/2021/ic/titles/6#6-2.5-3

### in_withheld_income_tax

**Label**: Indiana withheld income tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

### income_decile

**Label**: income decile
**Entity**: person
**Period**: year

Decile of household net income. Households are sorted by disposable income, and then divided into 10 equally-populated groups.

### income_elasticity

**Label**: income elasticity of labor supply
**Entity**: person
**Period**: year
**Unit**: /1

### income_elasticity_lsr

**Label**: income elasticity of labor supply response
**Entity**: person
**Period**: year
**Unit**: /1

### income_tax

**Label**: Federal income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Total federal individual income tax liability.

### income_tax_before_credits

**Label**: income tax before credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Total (regular + AMT) income tax liability before credits

### income_tax_before_refundable_credits

**Label**: Federal income tax before refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Income tax liability (including other taxes) after non-refundable credits are used, but before refundable credits are applied

### income_tax_capped_non_refundable_credits

**Label**: non-refundable tax credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Capped value of non-refundable tax credits

### income_tax_excluding_ptc

**Label**: income tax (excluding PTC)
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### income_tax_main_rates

**Label**: Income tax main rates
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/1

### income_tax_non_refundable_credits

**Label**: federal non-refundable income tax credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### income_tax_refundable_credits

**Label**: federal refundable income tax credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### income_tax_unavailable_non_refundable_credits

**Label**: unavailable non-refundable tax credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Total value of non-refundable tax credits that were not available to the filer due to having too low income tax.

### inpatient_expense

**Label**: Inpatient expenses
**Entity**: person
**Period**: year
**Unit**: currency-USD

### interest_deduction

**Label**: Interest deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Interest expenses deducted from taxable income.

**References**:
- https://www.law.cornell.edu/uscode/text/26/163

### interest_income

**Label**: interest income
**Entity**: person
**Period**: year
**Unit**: currency-USD

Interest income from bonds, savings accounts, CDs, etc.

### investment_expenses

**Label**: Investment expenses
**Entity**: person
**Period**: year
**Unit**: currency-USD

### investment_in_529_plan

**Label**: 529 plan investment
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Amount invested in a 529 savings plan.

### investment_in_529_plan_indv

**Label**: Individual 529 plan investment amounts
**Entity**: person
**Period**: year
**Unit**: currency-USD

Amount invested in a 529 savings plan for each contributor.

### investment_income_elected_form_4952

**Label**: investment income elected on Form 4952
**Entity**: person
**Period**: year
**Unit**: currency-USD

### investment_income_form_4952

**Label**: Investment income from Form 4952
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### investment_interest_expense

**Label**: Investment interest expense
**Entity**: person
**Period**: year
**Unit**: currency-USD

### irs_employment_income

**Label**: IRS employment income
**Entity**: person
**Period**: year
**Unit**: currency-USD

Employment income less payroll deductions.

### irs_gross_income

**Label**: Gross income
**Entity**: person
**Period**: year
**Unit**: currency-USD

Gross income, as defined in the Internal Revenue Code.

**References**:
- https://www.law.cornell.edu/uscode/text/26/61

### is_aca_eshi_eligible

**Label**: Person is eligible for employer-sponsored health insurance under ACA rules
**Entity**: person
**Period**: year

### is_aca_ptc_eligible

**Label**: Person is eligible for ACA premium tax credit and pays ACA premium
**Entity**: person
**Period**: year

### is_aca_ptc_immigration_status_eligible

**Label**: Person is eligible for ACA premium tax credit and pays ACA premium due to immigration status
**Entity**: person
**Period**: year

### is_acp_eligible

**Label**: Eligible for Affordable Connectivity Program
**Entity**: spm_unit
**Period**: year

Eligible for Affordable Connectivity Program

**References**:
- https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title47-section1752&edition=prelim

### is_adult

**Label**: Is an adult
**Entity**: person
**Period**: year

### is_adult_for_medicaid

**Label**: Working-age and childless adults
**Entity**: person
**Period**: year

**References**:
- https://www.law.cornell.edu/uscode/text/42/1396a#a_10_A_i_VIII

### is_adult_for_medicaid_fc

**Label**: Medicaid adult financial criteria
**Entity**: person
**Period**: year

### is_adult_for_medicaid_nfc

**Label**: Medicaid adult non-financial criteria
**Entity**: person
**Period**: year

### is_blind

**Label**: Is blind
**Entity**: person
**Period**: year

### is_breastfeeding

**Label**: Is breastfeeding
**Entity**: person
**Period**: year

### is_ca_cvrp_increased_rebate_eligible

**Label**: Eligible for CVRP increased rebate
**Entity**: person
**Period**: year

Eligible for increased rebate for low- and middle-income participants in California's Clean Vehicle Rebate Project (CVRP)

**References**:
- https://cleanvehiclerebate.org/en/eligibility-guidelines

### is_ca_cvrp_normal_rebate_eligible

**Label**: Eligible for CVRP normal rebate
**Entity**: person
**Period**: year

Eligible for California Clean Vehicle Rebate Project (CVRP) normal rebate

**References**:
- https://cleanvehiclerebate.org/en/eligibility-guidelines

### is_ccdf_age_eligible

**Label**: Age eligibility for CCDF
**Entity**: person
**Period**: year

### is_ccdf_asset_eligible

**Label**: Asset eligibility for CCDF
**Entity**: spm_unit
**Period**: year

### is_ccdf_continuous_income_eligible

**Label**: Continuous income eligibility for CCDF
**Entity**: spm_unit
**Period**: year

### is_ccdf_eligible

**Label**: Eligibility for CCDF
**Entity**: person
**Period**: year

### is_ccdf_home_based

**Label**: Whether CCDF care is home-based versus center-based
**Entity**: person
**Period**: year

### is_ccdf_income_eligible

**Label**: Income eligibility for CCDF
**Entity**: spm_unit
**Period**: year

### is_ccdf_initial_income_eligible

**Label**: Initial income eligibility for CCDF
**Entity**: spm_unit
**Period**: year

### is_ccdf_reason_for_care_eligible

**Label**: Reason-for-care eligibility for CCDF
**Entity**: person
**Period**: year

Indicates whether child qualifies for CCDF based on parents meeting activity test or that he/she receives or needs protective services

### is_cdcc_eligible

**Label**: CDCC-eligible
**Entity**: person
**Period**: year

**References**:
- https://www.law.cornell.edu/uscode/text/26/21#b_1

### is_child

**Label**: Is a child
**Entity**: person
**Period**: year

### is_child_dependent

**Label**: Is a child dependent based on the IRS definition
**Entity**: person
**Period**: year

**References**:
- https://www.law.cornell.edu/uscode/text/26/152#c_3_A_ii

### is_child_of_tax_head

**Label**: Is a child
**Entity**: person
**Period**: year

### is_chip_eligible

**Label**: CHIP eligible
**Entity**: person
**Period**: year

### is_chip_eligible_child

**Label**: Child eligible for CHIP
**Entity**: person
**Period**: year

Determines if a child is eligible for the Children's Health Insurance Program

**References**:
- https://www.ssa.gov/OP_Home/ssact/title21/2110.htm
- https://www.medicaid.gov/medicaid/national-medicaid-chip-program-information/medicaid-childrens-health-insurance-program-basic-health-program-eligibility-levels

### is_chip_eligible_pregnant

**Label**: Pregnant person eligible for CHIP
**Entity**: person
**Period**: year

Determines if a pregnant person is eligible for the Children's Health Insurance Program through either the standard pregnant pathway or FCEP

**References**:
- https://www.ssa.gov/OP_Home/ssact/title21/2110.htm
- https://www.medicaid.gov/medicaid/national-medicaid-chip-program-information/medicaid-childrens-health-insurance-program-basic-health-program-eligibility-levels
- https://www.kff.org/affordable-care-act/state-indicator/medicaid-and-chip-income-eligibility-limits-for-pregnant-women-as-a-percent-of-the-federal-poverty-level

### is_chip_eligible_standard_pregnant_person

**Label**: Pregnant person eligible for standard CHIP
**Entity**: person
**Period**: year

Determines if a pregnant person is eligible for the standard Children's Health Insurance Program

**References**:
- https://www.ssa.gov/OP_Home/ssact/title21/2110.htm
- https://www.medicaid.gov/medicaid/national-medicaid-chip-program-information/medicaid-childrens-health-insurance-program-basic-health-program-eligibility-levels

### is_chip_fcep_eligible_person

**Label**: Pregnant person eligible for CHIP through FCEP
**Entity**: person
**Period**: year

Determines if a pregnant person is eligible for the Children's Health Insurance Program through the Family Coverage Extension Program

**References**:
- https://www.kff.org/affordable-care-act/state-indicator/medicaid-and-chip-income-eligibility-limits-for-pregnant-women-as-a-percent-of-the-federal-poverty-level

### is_co_denver_dhs_elderly

**Label**: Denver DHS elderly
**Entity**: person
**Period**: year

Is elderly per Denver DHS guidelines

### is_computer_scientist

**Label**: is employed in a computer science related occupation
**Entity**: person
**Period**: year

**References**:
- https://www.law.cornell.edu/uscode/text/29/213

### is_deaf

**Label**: Is deaf
**Entity**: person
**Period**: year

### is_deceased

**Label**: Person is deceased
**Entity**: person
**Period**: year

### is_demographic_tanf_eligible

**Label**: Demographic eligibility for TANF
**Entity**: spm_unit
**Period**: month

Whether any person in a family applying for the Temporary Assistance for Needy Families program meets demographic requirements.

### is_disabled

**Label**: Is disabled
**Entity**: person
**Period**: year

### is_early_head_start_eligible

**Label**: Eligible person for the Early Head Start program
**Entity**: person
**Period**: year

**References**:
- https://eclkc.ohs.acf.hhs.gov/policy/45-cfr-chap-xiii/1302-12-determining-verifying-documenting-eligibilityhttps://www.hhs.gov/answers/programs-for-families-and-children/how-can-i-get-my-child-into-head-start/index.html

### is_ebb_eligible

**Label**: Eligible for Emergency Broadband Benefit
**Entity**: spm_unit
**Period**: year

Eligible for Emergency Broadband Benefit

### is_eligible_for_american_opportunity_credit

**Label**: Eligible for American Opportunity Credit
**Entity**: person
**Period**: year

Whether the person is eligible for the AOC in respect of qualified tuition expenses for this tax year. The expenses must be for one of the first four years of post-secondary education, and the person must not have claimed the AOC for any four previous tax years.

**References**:
- https://www.law.cornell.edu/uscode/text/26/25A#b_2

### is_eligible_for_fsla_overtime

**Label**: is eligible for overtime pay
**Entity**: person
**Period**: year

**References**:
- https://www.law.cornell.edu/cfr/text/29/541.600 ; https://www.law.cornell.edu/uscode/text/29/213

### is_eligible_for_housing_assistance

**Label**: Is eligible for HUD voucher
**Entity**: spm_unit
**Period**: year

HUD housing assistance payment

**References**:
- https://www.hud.gov/sites/dfiles/PIH/documents/HCV_Guidebook_Calculating_Rent_and_HAP_Payments.pdf

### is_eligible_md_poverty_line_credit

**Label**: Eligible for MD Poverty Line Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/maryland/2021/tax-general/title-10/subtitle-7/section-10-709/

### is_english_proficient

**Label**: Is English Proficient
**Entity**: person
**Period**: year

### is_enrolled_in_ccdf

**Label**: CCDF enrollment status
**Entity**: person
**Period**: year

### is_executive_administrative_professional

**Label**: is employed in a bona fide executive, administrative, or professional capacity
**Entity**: person
**Period**: year

**References**:
- https://www.law.cornell.edu/uscode/text/29/213 ; https://www.congress.gov/crs-product/IF12480

### is_farmer_fisher

**Label**: is employed in a farming, fishing, cultivating, or agriculture related occupation
**Entity**: person
**Period**: year

**References**:
- https://www.law.cornell.edu/uscode/text/29/213

### is_father

**Label**: Is a father
**Entity**: person
**Period**: year

### is_female

**Label**: Is female
**Entity**: person
**Period**: year

### is_full_time_college_student

**Label**: Is a full time college student
**Entity**: person
**Period**: year

### is_full_time_student

**Label**: Is a full time student
**Entity**: person
**Period**: year

### is_fully_disabled_service_connected_veteran

**Label**: Is a fully disabled veteran who became so as a result of an injury during service
**Entity**: person
**Period**: year

### is_grandparent_of_filer_or_spouse

**Label**: Is a grandparent of the filer or spouse
**Entity**: person
**Period**: year

### is_head_start_categorically_eligible

**Label**: Early Head Start or Head Start program eligible
**Entity**: person
**Period**: year

**References**:
- https://eclkc.ohs.acf.hhs.gov/policy/45-cfr-chap-xiii/1302-12-determining-verifying-documenting-eligibilityhttps://www.hhs.gov/answers/programs-for-families-and-children/how-can-i-get-my-child-into-head-start/index.html

### is_head_start_eligible

**Label**: Eligible person for the Head Start program
**Entity**: person
**Period**: year

**References**:
- https://eclkc.ohs.acf.hhs.gov/policy/45-cfr-chap-xiii/1302-12-determining-verifying-documenting-eligibilityhttps://www.hhs.gov/answers/programs-for-families-and-children/how-can-i-get-my-child-into-head-start/index.html

### is_head_start_income_eligible

**Label**: Early Head Start or Head Start income eligible
**Entity**: person
**Period**: year

**References**:
- https://eclkc.ohs.acf.hhs.gov/policy/45-cfr-chap-xiii/1302-12-determining-verifying-documenting-eligibilityhttps://www.hhs.gov/answers/programs-for-families-and-children/how-can-i-get-my-child-into-head-start/index.html

### is_hispanic

**Label**: hispanic
**Entity**: person
**Period**: year

Whether the person is Hispanic

### is_homeless

**Label**: Is homeless
**Entity**: household
**Period**: year

Whether all members are homeless individuals and are not receiving free shelter throughout the month

### is_household_head

**Label**: is head of this household
**Entity**: person
**Period**: eternity

### is_hud_elderly_disabled_family

**Label**: HUD elderly or disabled family
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

Whether an SPM unit is deemed elderly or disabled for HUD purposes

**References**:
- https://www.law.cornell.edu/cfr/text/24/5.611

### is_in_foster_care

**Label**: Person is currently in a qualifying foster care institution
**Entity**: person
**Period**: month

### is_in_foster_care_group_home

**Label**: Person is currently in a qualifying foster care group home
**Entity**: person
**Period**: month

### is_in_k12_nonpublic_school

**Label**: Is in a K-12 nonpublic school fulltime
**Entity**: person
**Period**: year

### is_in_k12_school

**Label**: Is in a K-12 school
**Entity**: person
**Period**: year

### is_in_medicaid_medically_needy_category

**Label**: In Medicaid medically needy category
**Entity**: person
**Period**: year

Whether this person is in a Medicaid category for which there is a medically needy pathway.

### is_in_public_housing

**Label**: Whether the household is in public housing
**Entity**: household
**Period**: year

### is_in_secondary_school

**Label**: Is in secondary school (or in an equivalent level of training)
**Entity**: person
**Period**: year

### is_incapable_of_self_care

**Label**: Incapable of self-care
**Entity**: person
**Period**: year

Whether this person is physically or mentally incapable of caring for themselves.

**References**:
- https://www.law.cornell.edu/uscode/text/26/21

### is_incarcerated

**Label**: Is incarcerated
**Entity**: person
**Period**: month

Whether this person is incarcerated.

### is_infant_for_medicaid

**Label**: Infants
**Entity**: person
**Period**: year

**References**:
- https://www.law.cornell.edu/uscode/text/42/1396a#l_1_B

### is_infant_for_medicaid_fc

**Label**: Medicaid infant financial criteria
**Entity**: person
**Period**: year

### is_infant_for_medicaid_nfc

**Label**: Medicaid infant non-financial criteria
**Entity**: person
**Period**: year

### is_irs_aged

**Label**: Aged person under the IRS requirements
**Entity**: person
**Period**: year

**References**:
- https://www.law.cornell.edu/uscode/text/26/63#f

### is_lifeline_eligible

**Label**: Eligible for Lifeline
**Entity**: spm_unit
**Period**: year

Eligible for Lifeline phone or broadband subsidy

**References**:
- https://www.law.cornell.edu/cfr/text/47/54.409

### is_ma_income_tax_exempt

**Label**: MA income tax exempt
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://malegislature.gov/Laws/GeneralLaws/PartI/TitleIX/Chapter62/Section5

### is_male

**Label**: is male
**Entity**: person
**Period**: year
**Unit**: currency-USD

### is_married

**Label**: Married
**Entity**: family
**Period**: year

Whether the adults in this family are married.

### is_medicaid_eligible

**Label**: Eligible for Medicaid
**Entity**: person
**Period**: year

**References**:
- https://www.law.cornell.edu/uscode/text/42/1396a#a_10https://www.kff.org/racial-equity-and-health-policy/fact-sheet/key-facts-on-health-coverage-of-immigrants

### is_medically_needy_for_medicaid

**Label**: Medically needy
**Entity**: person
**Period**: year

**References**:
- https://www.law.cornell.edu/cfr/text/42/part-435/subpart-D

### is_medicare_eligible

**Label**: Person is eligible for Medicare
**Entity**: person
**Period**: year

CMS, Original Medicare (Part A and B) Eligibility and Enrollmenthttps://www.cms.gov/medicare/enrollment-renewal/health-plans/original-part-a-bAbove link includes the following text:  Part A coverage begins the month the individual turns age 65

### is_migratory_child

**Label**: Is migratory child
**Entity**: person
**Period**: year

Whether a child made a qualifying move in the last 36 months as, with, or to join a migratory agricultural worker or fisher

**References**:
- https://www.law.cornell.edu/uscode/text/20/6399#3

### is_military

**Label**: is employed in the US armed forces
**Entity**: person
**Period**: year

### is_mother

**Label**: Is a mother
**Entity**: person
**Period**: year

### is_older_child_for_medicaid

**Label**: Older children
**Entity**: person
**Period**: year

**References**:
- https://www.law.cornell.edu/uscode/text/42/1396a#l_1_D

### is_older_child_for_medicaid_fc

**Label**: Medicaid older child financial criteria
**Entity**: person
**Period**: year

### is_older_child_for_medicaid_nfc

**Label**: Medicaid older child non-financial criteria
**Entity**: person
**Period**: year

### is_on_cliff

**Label**: is on a tax-benefit cliff
**Entity**: person
**Period**: year

Whether this person would be worse off if their employment income were higher.

### is_on_tribal_land

**Label**: Is on tribal land
**Entity**: household
**Period**: year

### is_optional_senior_or_disabled_asset_eligible

**Label**: Asset-eligibility for State’s optional Medicaid pathway for seniors or people with disabilities
**Entity**: person
**Period**: year

**References**:
- https://www.law.cornell.edu/uscode/text/42/1396a#m

### is_optional_senior_or_disabled_for_medicaid

**Label**: Seniors or disabled people not meeting SSI rules
**Entity**: person
**Period**: year

Whether this person qualifies for Medicaid through the State's optional aged, blind, or disabled pathway (not otherwise SSI-eligible)

**References**:
- https://www.law.cornell.edu/uscode/text/42/1396a#m

### is_optional_senior_or_disabled_income_eligible

**Label**: Income-eligibility for State’s optional Medicaid pathway for seniors or people with disabilities
**Entity**: person
**Period**: year

True if the tax unit’s countable income—after the state-specific income disregard—is below the income limit that the state sets for its optional pathway for aged, blind, or disabled individuals who are not otherwise SSI-eligible.

**References**:
- https://www.law.cornell.edu/uscode/text/42/1396a#m

### is_paid_hourly

**Label**: is paid hourly
**Entity**: person
**Period**: year

### is_parent

**Label**: Is a parent
**Entity**: person
**Period**: year

### is_parent_for_medicaid

**Label**: Parents
**Entity**: person
**Period**: year

**References**:
- https://www.law.cornell.edu/uscode/text/42/1396u-1

### is_parent_for_medicaid_fc

**Label**: Medicaid parent financial criteria
**Entity**: person
**Period**: year

### is_parent_for_medicaid_nfc

**Label**: Medicaid parent non-financial criteria
**Entity**: person
**Period**: year

### is_parent_of_filer_or_spouse

**Label**: Is a parent of the filer or spouse
**Entity**: person
**Period**: year

### is_permanently_and_totally_disabled

**Label**: Is permanently and totally disabled
**Entity**: person
**Period**: year

### is_permanently_disabled_veteran

**Label**: Permanently disabled veteran
**Entity**: person
**Period**: year

### is_person_demographic_tanf_eligible

**Label**: Person demographic eligibility for TANF
**Entity**: person
**Period**: month

Whether this person meets the demographic requirements for TANF eligibility

### is_pregnant

**Label**: Is pregnant
**Entity**: person
**Period**: year

### is_pregnant_for_medicaid

**Label**: Pregnant people
**Entity**: person
**Period**: year

**References**:
- https://www.law.cornell.edu/uscode/text/42/1396a#l_1_A

### is_pregnant_for_medicaid_fc

**Label**: Medicaid pregnant financial criteria
**Entity**: person
**Period**: year

### is_pregnant_for_medicaid_nfc

**Label**: Medicaid pregnant non-financial criteria
**Entity**: person
**Period**: year

### is_retired

**Label**: Is retired
**Entity**: person
**Period**: year

### is_runaway_child

**Label**: Is runaway child
**Entity**: person
**Period**: year

Whether an individual under 18 years old leaves home or their legal residence without parental or guardian permission

**References**:
- https://www.law.cornell.edu/uscode/text/34/11279#4

### is_rural

**Label**: Is in a rural area
**Entity**: household
**Period**: year

**References**:
- https://www.law.cornell.edu/cfr/text/47/54.505#b_3_i

### is_self_employed

**Label**: Is self-employed
**Entity**: person
**Period**: year

### is_senior

**Label**: Is a senior
**Entity**: person
**Period**: year

### is_separated

**Label**: Separated
**Entity**: person
**Period**: year

Whether the person is separated from a partner.

**References**:
- https://www.law.cornell.edu/uscode/text/26/7703

### is_severely_disabled

**Label**: Is severely disabled
**Entity**: person
**Period**: year

### is_snap_eligible

**Label**: SNAP eligible
**Entity**: spm_unit
**Period**: month

Whether this SPM unit is eligible for SNAP benefits

**References**:
- https://www.law.cornell.edu/uscode/text/7/2017#a
- https://www.law.cornell.edu/uscode/text/7/2014#c

### is_snap_ineligible_student

**Label**: Is an ineligible student for SNAP
**Entity**: person
**Period**: year

Whether this person is an ineligible student for SNAP and can not be counted towards the household size

**References**:
- https://www.law.cornell.edu/uscode/text/7/2015

### is_sro

**Label**: Is single room occupancy
**Entity**: household
**Period**: year

### is_ssi_aged

**Label**: Is aged for SSI
**Entity**: person
**Period**: year

### is_ssi_aged_blind_disabled

**Label**: SSI aged, blind, or disabled
**Entity**: person
**Period**: year

Indicates whether a person is aged, blind, or disabled for the Supplemental Security Income program

**References**:
- https://www.law.cornell.edu/uscode/text/42/1382c#a_1

### is_ssi_blind_or_disabled_working_student_exclusion_eligible

**Label**: Eligible for SSI blind or disabled working student earned income exclusion
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/cfr/text/20/416.1112#c_3

### is_ssi_disabled

**Label**: SSI disabled
**Entity**: person
**Period**: year

Indicates whether a person is disabled for the Supplemental Security Income program

**References**:
- https://www.law.cornell.edu/uscode/text/42/1382c#a_3_A

### is_ssi_eligible

**Label**: Is SSI eligible person
**Entity**: person
**Period**: year

### is_ssi_eligible_individual

**Label**: Is an SSI-eligible individual
**Entity**: person
**Period**: year

### is_ssi_eligible_spouse

**Label**: Is an SSI-eligible spouse
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/42/1382c#b

### is_ssi_ineligible_child

**Label**: Is an SSI-ineligible child
**Entity**: person
**Period**: year

### is_ssi_ineligible_parent

**Label**: Is an SSI-ineligible parent in respect of a child
**Entity**: person
**Period**: year

### is_ssi_ineligible_spouse

**Label**: Is an SSI-ineligible spouse
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/42/1382c#b

### is_ssi_qualified_noncitizen

**Label**: Is an SSI qualified noncitizen
**Entity**: person
**Period**: year

**References**:
- https://secure.ssa.gov/poms.nsf/lnx/0500502100

### is_ssi_recipient_for_medicaid

**Label**: SSI recipients
**Entity**: person
**Period**: year

Qualifies for Medicaid due to receiving SSI, or if in a 209(b) state, due to meeting that state's eligibility requirements.

**References**:
- https://www.law.cornell.edu/uscode/text/42/1396a#f

### is_surviving_child_of_disabled_veteran

**Label**: Surviving child of disabled veteran
**Entity**: person
**Period**: year

### is_surviving_spouse

**Label**: surviving spouse
**Entity**: person
**Period**: year

Whether the person is surviving spouse.

### is_surviving_spouse_of_disabled_veteran

**Label**: Surviving spouse of disabled veteran
**Entity**: person
**Period**: year

### is_tafdc_related_to_head_or_spouse

**Label**: Person is related to the head or spouse under the TAFDC regulations
**Entity**: person
**Period**: year

**References**:
- https://www.law.cornell.edu/regulations/massachusetts/106-CMR-703-310

### is_tanf_enrolled

**Label**: Enrolled in TANF
**Entity**: spm_unit
**Period**: month

Whether the familiy is currently enrolled in the Temporary Assistance for Needy Families program.

### is_tanf_non_cash_eligible

**Label**: Eligibility for TANF non-cash benefit
**Entity**: spm_unit
**Period**: month

Eligibility for TANF non-cash benefit for SNAP BBCE

### is_tanf_non_cash_hheod

**Label**: Elderly or disabled for TANF non-cash benefit
**Entity**: spm_unit
**Period**: month

Whether the household is considered elderly or disabled for TANF non-cash benefit for SNAP BBCE

### is_tax_unit_dependent

**Label**: Is a dependent in the tax unit
**Entity**: person
**Period**: year

### is_tax_unit_head

**Label**: Head of tax unit
**Entity**: person
**Period**: year

### is_tax_unit_head_or_spouse

**Label**: Head or Spouse of tax unit
**Entity**: person
**Period**: year

### is_tax_unit_spouse

**Label**: Spouse of tax unit
**Entity**: person
**Period**: year

### is_tce_eligible

**Label**: Eligible person for the Tax Counseling for the Elderly program
**Entity**: person
**Period**: year

**References**:
- https://www.irs.gov/individuals/tax-counseling-for-the-elderly

### is_usda_disabled

**Label**: USDA disabled status
**Entity**: person
**Period**: year

Disabled according to USDA criteria

### is_usda_elderly

**Label**: USDA elderly
**Entity**: person
**Period**: year

Is elderly per USDA guidelines

### is_veteran

**Label**: Is veteran
**Entity**: person
**Period**: year

A person who served in the active military, naval, air, or space service, and who was discharged or released therefrom under conditions other than dishonorable.

**References**:
- https://www.law.cornell.edu/uscode/text/38/101

### is_wa_adult

**Label**: Is a working-age adult
**Entity**: person
**Period**: year

### is_wic_at_nutritional_risk

**Label**: At nutritional risk for WIC
**Entity**: person
**Period**: month

Assessed as being at nutritional risk for the Special Supplemental Nutrition Program for Women, Infants and Children (WIC)

**References**:
- https://www.law.cornell.edu/uscode/text/42/1786#b_8

### is_wic_eligible

**Label**: Is eligible for WIC
**Entity**: person
**Period**: month

Is eligible for the Special Supplemental Nutrition Program for Women, Infants and Children (WIC)

**References**:
- https://www.law.cornell.edu/cfr/text/7/246.7#c_1

### is_young_adult_for_medicaid

**Label**: Young adults
**Entity**: person
**Period**: year

**References**:
- https://www.law.cornell.edu/uscode/text/42/1396d#a_i

### is_young_adult_for_medicaid_fc

**Label**: Medicaid young adult financial criteria
**Entity**: person
**Period**: year

### is_young_adult_for_medicaid_nfc

**Label**: Medicaid young adult non-financial criteria
**Entity**: person
**Period**: year

### is_young_child_for_medicaid

**Label**: Young children
**Entity**: person
**Period**: year

**References**:
- https://www.law.cornell.edu/uscode/text/42/1396a#l_1_B

### is_young_child_for_medicaid_fc

**Label**: Medicaid young child financial criteria
**Entity**: person
**Period**: year

### is_young_child_for_medicaid_nfc

**Label**: Medicaid young child non-financial criteria
**Entity**: person
**Period**: year

### itemized_deductions_less_salt

**Label**: Itemized tax deductions other than SALT deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Non-SALT itemized deductions total.

### itemized_taxable_income_deductions

**Label**: Itemized taxable income deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### itemized_taxable_income_deductions_reduction

**Label**: Itemized taxable income deductions reduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### k12_tuition_and_fees

**Label**: K-12 Tuition and fees (from Form 8917)
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### keogh_distributions

**Label**: Keogh plan distributions
**Entity**: person
**Period**: year
**Unit**: currency-USD

### ks_additions

**Label**: Kansas AGI additions to federal AGI
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ksrevenue.gov/pdf/ip21.pdfhttps://www.ksrevenue.gov/pdf/ip22.pdf

### ks_agi

**Label**: Kansas AGI
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ksrevenue.gov/pdf/ip21.pdfhttps://www.ksrevenue.gov/pdf/ip22.pdf

### ks_agi_subtractions

**Label**: Kansas AGI subtractions from federal AGI
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ksrevenue.gov/pdf/ip21.pdfhttps://www.ksrevenue.gov/pdf/ip22.pdf

### ks_cdcc

**Label**: Kansas child and dependent care expenses credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ksrevenue.gov/pdf/ip21.pdfhttps://www.ksrevenue.gov/pdf/ip22.pdf

### ks_count_exemptions

**Label**: number of KS exemptions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ksrevenue.gov/pdf/ip21.pdfhttps://www.ksrevenue.gov/pdf/ip22.pdf

### ks_disabled_veteran_exemptions_eligible_person

**Label**: Eligible person for the Kansas disabled veteran exemption
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/kansas/chapter-79/article-32/section-79-32-121/

### ks_exemptions

**Label**: Kansas exemptions amount
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/kansas/chapter-79/article-32/section-79-32-121/

### ks_fstc

**Label**: Kansas food sales tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ksrevenue.gov/pdf/ip21.pdfhttps://www.ksrevenue.gov/pdf/ip22.pdf

### ks_income_tax

**Label**: Kansas income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ksrevenue.gov/pdf/ip21.pdfhttps://www.ksrevenue.gov/pdf/ip22.pdf

### ks_income_tax_before_credits

**Label**: Kansas income tax before credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ksrevenue.gov/pdf/ip21.pdfhttps://www.ksrevenue.gov/pdf/ip22.pdf

### ks_income_tax_before_refundable_credits

**Label**: Kansas income tax before refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ksrevenue.gov/pdf/ip21.pdfhttps://www.ksrevenue.gov/pdf/ip22.pdf

### ks_itemized_deductions

**Label**: Kansas itemized deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ksrevenue.gov/pdf/ip21.pdfhttps://www.ksrevenue.gov/pdf/ip22.pdf

### ks_nonrefundable_credits

**Label**: Kansas nonrefundable income tax credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ksrevenue.gov/pdf/ip21.pdfhttps://www.ksrevenue.gov/pdf/ip22.pdf

### ks_nonrefundable_eitc

**Label**: Kansas EITC nonrefundable amount
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ksrevenue.gov/pdf/ip21.pdfhttps://www.ksrevenue.gov/pdf/ip22.pdf

### ks_refundable_credits

**Label**: Kansas refundable income tax credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ksrevenue.gov/pdf/ip21.pdfhttps://www.ksrevenue.gov/pdf/ip22.pdf

### ks_refundable_eitc

**Label**: Kansas refundable EITC amount
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ksrevenue.gov/pdf/ip21.pdfhttps://www.ksrevenue.gov/pdf/ip22.pdf

### ks_standard_deduction

**Label**: Kansas standard deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ksrevenue.gov/pdf/ip21.pdfhttps://www.ksrevenue.gov/pdf/ip22.pdf

### ks_taxable_income

**Label**: Kansas taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ksrevenue.gov/pdf/ip21.pdfhttps://www.ksrevenue.gov/pdf/ip22.pdf

### ks_total_eitc

**Label**: Kansas total EITC amount (both nonrefundable and refundable)
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ksrevenue.gov/pdf/ip21.pdfhttps://www.ksrevenue.gov/pdf/ip22.pdf

### ks_withheld_income_tax

**Label**: Kansas withheld income tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

### ky_additions

**Label**: Kentucky additions
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=53498https://revenue.ky.gov/Forms/Schedule%20M%202022.pdf#page=1https://revenue.ky.gov/Forms/740%20Packet%20Instructions%205-9-23.pdf#page=23https://revenue.ky.gov/Forms/Schedule%20M-2021.pdf#page=1https://taxsim.nber.org/historical_state_tax_forms/KY/2021/Form%20740%20Packet%20Instructions-2021.pdf#page=27

### ky_aged_personal_tax_credits

**Label**: Kentucky personal tax credits aged amount
**Entity**: person
**Period**: year
**Unit**: currency-USD

https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=53500#page=3

### ky_agi

**Label**: Kentucky adjusted gross income
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://revenue.ky.gov/Forms/740%20Packet%20Instructions%205-9-23.pdf#page=11

### ky_blind_personal_tax_credits

**Label**: Kentucky personal tax credits blind amount
**Entity**: person
**Period**: year
**Unit**: currency-USD

https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=53500#page=3

### ky_cdcc

**Label**: Kentucky household and dependent care service credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=29058

### ky_deductions_indiv

**Label**: Kentucky income deductions when married couples file separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/kentucky/2022/chapter-141/section-141-019/

### ky_deductions_joint

**Label**: Kentucky itemized deductions when married couples file jointly
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/kentucky/2022/chapter-141/section-141-019/

### ky_family_size_tax_credit

**Label**: Kentucky family size tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: /1

**References**:
- https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=49188

### ky_family_size_tax_credit_rate

**Label**: Kentucky family size tax credit rate
**Entity**: tax_unit
**Period**: year
**Unit**: /1

**References**:
- https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=49188

### ky_files_separately

**Label**: Married couple file separately on the Kentucky tax return
**Entity**: tax_unit
**Period**: year

**References**:
- https://revenue.ky.gov/Forms/740%20Packet%20Instructions%205-9-23.pdf#page=11

### ky_filing_status

**Label**: Filing status for the tax unit in Kentucky
**Entity**: tax_unit
**Period**: year

**References**:
- https://codes.findlaw.com/ky/title-xi-revenue-and-taxation/ky-rev-st-sect-141-066.html
- https://revenue.ky.gov/Forms/740%20Packet%20Instructions%205-9-23.pdf#page=11

### ky_income_tax

**Label**: Kentucky income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ky_income_tax_before_non_refundable_credits_indiv

**Label**: Kentucky income tax before non-refundable credits when married couples are filing separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

### ky_income_tax_before_non_refundable_credits_joint

**Label**: Kentucky income tax before non-refundable credits when married filing jointly
**Entity**: person
**Period**: year
**Unit**: currency-USD

### ky_income_tax_before_non_refundable_credits_unit

**Label**: Kentucky income tax before non-refundable credits combined
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ky_income_tax_before_refundable_credits

**Label**: Kentucky income tax before refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ky_itemized_deductions

**Label**: Kentucky itemized deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ky_itemized_deductions_indiv

**Label**: Kentucky itemized deductions when married couples file separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://revenue.ky.gov/Forms/Form%20740%20Schedule%20A%202022.pdfhttps://law.justia.com/codes/kentucky/2022/chapter-141/section-141-019/

### ky_itemized_deductions_joint

**Label**: Kentucky itemized deductions when married couples file jointly
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://revenue.ky.gov/Forms/Form%20740%20Schedule%20A%202022.pdfhttps://law.justia.com/codes/kentucky/2022/chapter-141/section-141-019/

### ky_itemized_deductions_unit

**Label**: Kentucky itemized deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://revenue.ky.gov/Forms/Form%20740%20Schedule%20A%202022.pdfhttps://law.justia.com/codes/kentucky/2022/chapter-141/section-141-019/

### ky_military_personal_tax_credits

**Label**: Kentucky personal tax credits military service amount
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=53500#page=3

### ky_modified_agi

**Label**: Kentucky modified adjusted gross income for the family size tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://revenue.ky.gov/Forms/740%20Packet%20Instructions%205-9-23.pdf#page=22

### ky_non_refundable_credits

**Label**: Kentucky non-refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ky_pension_income_exclusion

**Label**: KY Pension Income Exclusion
**Entity**: person
**Period**: year

### ky_pension_income_exclusion_exemption_eligible

**Label**: KY Pension Income Exclusion Exemption Eligible
**Entity**: person
**Period**: year

**References**:
- https://revenue.ky.gov/Forms/Schedule%20P%202022.pdf

### ky_personal_tax_credits

**Label**: Kentucky personal tax credits combined
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=53500#page=3

### ky_personal_tax_credits_indiv

**Label**: Kentucky personal tax credits when married couples file separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=53500#page=3

### ky_personal_tax_credits_joint

**Label**: Kentucky personal tax credits when married couples file jointly
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=53500#page=3

### ky_refundable_credits

**Label**: Kentucky refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ky_service_credit_months_post_1997

**Label**: Kentucky service credit months after 1997
**Entity**: person
**Period**: year

### ky_service_credit_months_pre_1998

**Label**: Kentucky service credit months before 1998
**Entity**: person
**Period**: year

### ky_service_credits_percentage_pre_1998

**Label**: Share of service credit months worked before 1998
**Entity**: person
**Period**: year

### ky_standard_deduction

**Label**: Kentucky standard deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ky_standard_deduction_indiv

**Label**: Kentucky standard deduction when married couples file separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

### ky_standard_deduction_joint

**Label**: Kentucky standard deduction when married couples file jointly
**Entity**: person
**Period**: year
**Unit**: currency-USD

### ky_subtractions

**Label**: Kentucky subtractions
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=53498https://revenue.ky.gov/Forms/Schedule%20M%202022.pdf#page=1https://revenue.ky.gov/Forms/740%20Packet%20Instructions%205-9-23.pdf#page=23https://revenue.ky.gov/Forms/Schedule%20M-2021.pdf#page=1https://taxsim.nber.org/historical_state_tax_forms/KY/2021/Form%20740%20Packet%20Instructions-2021.pdf#page=27

### ky_tax_unit_itemizes

**Label**: Whether the tax unit in Kentucky itemizes the deductions when married filing separately
**Entity**: tax_unit
**Period**: year

### ky_taxable_income

**Label**: Kentucky taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ky_taxable_income_indiv

**Label**: Kentucky taxable income when married couples file separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://revenue.ky.gov/Forms/740%20Packet%20Instructions%205-9-23.pdf#page=11

### ky_taxable_income_joint

**Label**: Kentucky taxable income when married couples file jointly
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://revenue.ky.gov/Forms/740%20Packet%20Instructions%205-9-23.pdf#page=11

### ky_tuition_tax_credit

**Label**: Kentucky tuition tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ky_tuition_tax_credit_eligible

**Label**: Eligible for the Kentucky tuition tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ky_withheld_income_tax

**Label**: Kentucky withheld income tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

### la_aged_exemption

**Label**: Louisiana aged exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### la_agi

**Label**: Louisiana adjusted gross income income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### la_agi_exempt_income

**Label**: Louisiana income that is exempt from the adjusted gross income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://revenue.louisiana.gov/TaxForms/IT540i(2021)%20Instructions.pdf#page=9
- https://revenue.louisiana.gov/TaxForms/IT540WEB(2021)%20F.pdf

### la_blind_exemption

**Label**: Louisiana blind exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.louisiana.gov/taxforms/6935(11_02)F.pdf#page=1
- https://revenue.louisiana.gov/TaxForms/IT540iWEB(2022)D1.pdf#page=2

### la_blind_exemption_person

**Label**: Louisiana blind exemption for each individual
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.louisiana.gov/taxforms/6935(11_02)F.pdf#page=1
- https://revenue.louisiana.gov/TaxForms/IT540iWEB(2022)D1.pdf#page=2

### la_dependents_exemption

**Label**: Louisiana qualified dependents exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.louisiana.gov/taxforms/6935(11_02)F.pdf#page=1
- https://revenue.louisiana.gov/TaxForms/IT540iWEB(2022)D1.pdf#page=2

### la_disability_income_exemption_person

**Label**: Louisiana disability income exemption for each person
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.legis.la.gov/legis/Law.aspx?d=102133

### la_eitc

**Label**: Louisiana Earned Income Tax Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.legis.la.gov/legis/Law.aspx?d=453085

### la_exemptions

**Label**: Louisiana exemptions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### la_federal_tax_deduction

**Label**: Louisiana federal tax deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://revenue.louisiana.gov/TaxForms/IT540iWEB(2022)D1.pdf#page=2
- https://revenue.louisiana.gov/TaxForms/IT540i(2021)%20Instructions.pdf#page=3
- https://law.justia.com/codes/louisiana/2021/revised-statutes/title-47/rs-298/

### la_general_relief

**Label**: Los Angeles County General Relief
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://drive.google.com/file/d/1Oc7UuRFxJj-eDwTeox92PtmRVGnG9RjW/view?usp=sharing

### la_general_relief_age_eligible

**Label**: Eligible for the Los Angeles County General Relief based on the age requirements
**Entity**: spm_unit
**Period**: month

**References**:
- https://drive.google.com/file/d/1Oc7UuRFxJj-eDwTeox92PtmRVGnG9RjW/view?usp=sharing

### la_general_relief_base_amount

**Label**: Los Angeles County General Relief base amount
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://drive.google.com/file/d/1Oc7UuRFxJj-eDwTeox92PtmRVGnG9RjW/view?usp=sharing

### la_general_relief_cash_asset_eligible

**Label**: Eligible for the Los Angeles County General Relief based on the cash asset requirements
**Entity**: spm_unit
**Period**: year

**References**:
- https://drive.google.com/file/d/1Oc7UuRFxJj-eDwTeox92PtmRVGnG9RjW/view?usp=sharing

### la_general_relief_cash_asset_limit

**Label**: Limit for the Los Angeles County General Relief cash asset requirements
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://drive.google.com/file/d/1Oc7UuRFxJj-eDwTeox92PtmRVGnG9RjW/view?usp=sharing

### la_general_relief_disability_eligible

**Label**: Eligible for the Los Angeles County General Relief based on the disability requirements
**Entity**: spm_unit
**Period**: month

**References**:
- https://drive.google.com/file/d/1Oc7UuRFxJj-eDwTeox92PtmRVGnG9RjW/view?usp=sharing

### la_general_relief_eligible

**Label**: Eligible for the Los Angeles County General Relief
**Entity**: spm_unit
**Period**: month

**References**:
- https://drive.google.com/file/d/1Oc7UuRFxJj-eDwTeox92PtmRVGnG9RjW/view?usp=sharing

### la_general_relief_gross_income

**Label**: Gross Income sources accounted for under the Los Angeles County General Relief
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://drive.google.com/file/d/1Oc7UuRFxJj-eDwTeox92PtmRVGnG9RjW/view?usp=sharing

### la_general_relief_home_value_eligible

**Label**: Eligible for the Los Angeles County General Relief based on the home value requirements
**Entity**: spm_unit
**Period**: year

**References**:
- https://drive.google.com/file/d/1Oc7UuRFxJj-eDwTeox92PtmRVGnG9RjW/view?usp=sharing

### la_general_relief_housing_subsidy

**Label**: Los Angeles County General Relief Housing Subsidy
**Entity**: spm_unit
**Period**: month

**References**:
- https://dpss.lacounty.gov/en/cash/gr/housing.html

### la_general_relief_housing_subsidy_base_amount_eligible

**Label**: Eligible for the Los Angeles County General Relief Housing Subsidy based on the base amount requirements
**Entity**: spm_unit
**Period**: month

**References**:
- https://dpss.lacounty.gov/en/cash/gr/housing.html

### la_general_relief_housing_subsidy_eligible

**Label**: Eligible for the Los Angeles County General Relief Housing Subsidy
**Entity**: spm_unit
**Period**: year

**References**:
- https://dpss.lacounty.gov/en/cash/gr/housing.html

### la_general_relief_housing_subsidy_program_eligible

**Label**: Eligible for the Los Angeles County General Relief Housing Subsidy based on the program eligibility
**Entity**: spm_unit
**Period**: year

**References**:
- https://dpss.lacounty.gov/en/cash/gr/housing.html

### la_general_relief_immigration_status_eligible

**Label**: Eligible for the Los Angeles County General Relief based on the immigration status requirements
**Entity**: spm_unit
**Period**: year

**References**:
- http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FGR%2FGR%2F42-404_Immigrant_Eligibility_Chart%2F42-404_Immigrant_Eligibility_Chart.htm

### la_general_relief_immigration_status_eligible_person

**Label**: Eligible Person for the Los Angeles County General Relief based on the immigration status requirements
**Entity**: person
**Period**: year

**References**:
- http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FGR%2FGR%2F42-404_Immigrant_Eligibility_Chart%2F42-404_Immigrant_Eligibility_Chart.htm

### la_general_relief_motor_vehicle_value_eligible

**Label**: Eligible for the Los Angeles County General Relief based on the motor vehicle value requirements
**Entity**: spm_unit
**Period**: year

**References**:
- https://drive.google.com/file/d/1Oc7UuRFxJj-eDwTeox92PtmRVGnG9RjW/view?usp=sharing

### la_general_relief_net_income

**Label**: Net Income under the Los Angeles County General Relief after state and federal deductions
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://drive.google.com/file/d/1Oc7UuRFxJj-eDwTeox92PtmRVGnG9RjW/view?usp=sharing

### la_general_relief_net_income_eligible

**Label**: Eligible for the Los Angeles County General Relief based on the net income requirements
**Entity**: spm_unit
**Period**: month

**References**:
- https://drive.google.com/file/d/1Oc7UuRFxJj-eDwTeox92PtmRVGnG9RjW/view?usp=sharing

### la_general_relief_net_income_limit

**Label**: Limit for the Los Angeles County General Relief net income requirements
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://drive.google.com/file/d/1Oc7UuRFxJj-eDwTeox92PtmRVGnG9RjW/view?usp=sharing

### la_general_relief_personal_property_eligible

**Label**: Eligible for the Los Angeles County General Relief based on the personal property value requirements
**Entity**: spm_unit
**Period**: year

**References**:
- https://drive.google.com/file/d/1Oc7UuRFxJj-eDwTeox92PtmRVGnG9RjW/view?usp=sharing

### la_general_relief_recipient

**Label**: Recipient of the Los Angeles County General Relief
**Entity**: spm_unit
**Period**: year

**References**:
- https://drive.google.com/file/d/1Oc7UuRFxJj-eDwTeox92PtmRVGnG9RjW/view?usp=sharing

### la_general_relief_rent_contribution

**Label**: Los Angeles County General Relief rent contribution
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://drive.google.com/file/d/1Oc7UuRFxJj-eDwTeox92PtmRVGnG9RjW/view?usp=sharing

### la_income_tax

**Label**: Louisiana income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### la_income_tax_before_non_refundable_credits

**Label**: Louisiana income tax before non-refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.legis.la.gov/legis/Law.aspx?d=101946

### la_income_tax_before_refundable_credits

**Label**: Louisiana income tax before refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### la_itemized_deductions

**Label**: Louisiana itemized deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://revenue.louisiana.gov/TaxForms/IT540iWEB(2022)D1.pdf#page=2
- https://revenue.louisiana.gov/TaxForms/IT540i(2021)%20Instructions.pdf#page=3
- https://www.legis.la.gov/Legis/Law.aspx?d=101760

### la_military_pay_exclusion

**Label**: Louisiana military pay exclusion
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- http://www.legis.la.gov/legis/Law.aspx?d=101760

### la_non_refundable_cdcc

**Label**: Louisiana non-refundable Child and Dependent Care Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- http://legis.la.gov/Legis/Law.aspx?d=101769

### la_non_refundable_credits

**Label**: Louisiana non-refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### la_personal_exemption

**Label**: Louisiana personal exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.legis.la.gov/legis/Law.aspx?d=101761

### la_quality_rating_of_child_care_facility

**Label**: Quality rating of child care facility for the Louisiana school readiness tax credit
**Entity**: person
**Period**: year

**References**:
- https://www.revenue.louisiana.gov/IndividualIncomeTax/SchoolReadinessTaxCredit

### la_receives_blind_exemption

**Label**: Filer receives the Louisiana blind exemption over the subtraction
**Entity**: person
**Period**: year

**References**:
- https://www.legis.la.gov/legis/Law.aspx?d=102133

### la_refundable_cdcc

**Label**: Louisiana refundable Child and Dependent Care Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- http://legis.la.gov/Legis/Law.aspx?d=101769

### la_refundable_credits

**Label**: Louisiana refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### la_retirement_exemption_person

**Label**: Louisiana retirement exemption for each person
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.legis.la.gov/legis/Law.aspx?d=102133

### la_school_readiness_credit

**Label**: Louisiana school readiness tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.louisiana.gov/IndividualIncomeTax/SchoolReadinessTaxCredit

### la_school_readiness_credit_eligible_child

**Label**: Eligible child for the Louisiana school readiness tax credit
**Entity**: person
**Period**: year

**References**:
- https://revenue.louisiana.gov/TaxForms/IT540WEB(2022)%20F%20D2.pdf#page=15

### la_school_readiness_credit_non_refundable

**Label**: Louisiana non-refundable school readiness tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.louisiana.gov/IndividualIncomeTax/SchoolReadinessTaxCredit

### la_school_readiness_credit_refundable

**Label**: Louisiana refundable school readiness tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.louisiana.gov/IndividualIncomeTax/SchoolReadinessTaxCredit

### la_school_readiness_credit_refundable_eligible

**Label**: Louisiana refundable school readiness tax credit eligibility
**Entity**: tax_unit
**Period**: year

**References**:
- https://www.revenue.louisiana.gov/IndividualIncomeTax/SchoolReadinessTaxCredit

### la_standard_deduction

**Label**: Louisiana standard deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### la_surviving_spouse_exemption

**Label**: Louisiana qualifying surviving spouse exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.louisiana.gov/taxforms/6935(11_02)F.pdf#page=1

### la_taxable_income

**Label**: Louisiana taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### la_withheld_income_tax

**Label**: Louisiana withheld income tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

### lab_expense

**Label**: Lab expenses
**Entity**: person
**Period**: year
**Unit**: currency-USD

### labor_supply_behavioral_response

**Label**: earnings-related labor supply change
**Entity**: person
**Period**: year
**Unit**: currency-USD

### lifeline

**Label**: Lifeline
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

Amount of Lifeline phone and broadband benefit

**References**:
- https://www.law.cornell.edu/cfr/text/47/54.403

### lifetime_learning_credit

**Label**: Lifetime Learning Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Value of the non-refundable Lifetime Learning Credit

**References**:
- https://www.law.cornell.edu/uscode/text/26/25A#c

### lifetime_learning_credit_credit_limit

**Label**: Lifetime Learning Credit credit limit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Value of the non-refundable Lifetime Learning Credit

**References**:
- https://www.law.cornell.edu/uscode/text/26/25A#c

### lifetime_learning_credit_potential

**Label**: Potential value of the Lifetime Learning Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Value of the non-refundable Lifetime Learning Credit

**References**:
- https://www.law.cornell.edu/uscode/text/26/25A#c

### limited_capital_loss

**Label**: Limited capital loss deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

The capital loss deductible from gross income.

**References**:
- https://www.law.cornell.edu/uscode/text/26/1211

### lives_in_vehicle

**Label**: Lives in vehicle
**Entity**: household
**Period**: year

Whether a household is using their vehicle as their primary residence 

### living_arrangements_allow_for_food_preparation

**Label**: Living arrangements allow for food preparation
**Entity**: household
**Period**: year

### local_income_tax

**Label**: Local income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### local_sales_tax

**Label**: Local sales tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### long_term_capital_gains

**Label**: long-term capital gains
**Entity**: person
**Period**: year
**Unit**: currency-USD

Net gains made from sales of assets held for more than one year (losses are expressed as negative gains).

**References**:
- {'title': '26 U.S. Code § 1222(3)', 'href': 'https://www.law.cornell.edu/uscode/text/26/1222#3'}

### long_term_capital_gains_before_response

**Label**: capital gains before responses
**Entity**: person
**Period**: year
**Unit**: currency-USD

### long_term_capital_gains_on_collectibles

**Label**: Long-term capital gains on collectibles
**Entity**: person
**Period**: year
**Unit**: currency-USD

Portion of capital_gains_28_percent_rate_gain associated with collectibles.

**References**:
- {'title': '26 U.S. Code § 1(h)(4)', 'href': 'https://www.law.cornell.edu/uscode/text/26/1#h_4'}

### long_term_capital_gains_on_small_business_stock

**Label**: Long-term capital gains on small business stock sales, etc
**Entity**: person
**Period**: year
**Unit**: currency-USD

Portion of capital_gains_28_percent_rate_gain not associated with collectibles.

**References**:
- {'title': '26 U.S. Code § 1(h)(4)', 'href': 'https://www.law.cornell.edu/uscode/text/26/1#h_4'}

### long_term_health_insurance_premiums

**Label**: Long-term health insurance premiums
**Entity**: person
**Period**: year
**Unit**: currency-USD

### loss_ald

**Label**: Business loss ALD
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Above-the-line deduction from gross income for business losses.

**References**:
- https://www.law.cornell.edu/uscode/text/26/165

### loss_limited_net_capital_gains

**Label**: Loss-limited net capital gains
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ma_agi

**Label**: MA adjusted gross income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.mass.gov/info-details/mass-general-laws-c62-ss-2

### ma_child_and_family_credit

**Label**: Massachusetts child and family tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.mass.gov/info-details/massachusetts-child-and-family-tax-credit

### ma_child_and_family_credit_or_dependent_care_credit

**Label**: MA dependent or dependent care credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

The CFTC replaces the Dependent Care Tax Credit and the Household Dependent Tax Credit with Child and Family Tax Credit for tax years beginning on or after January 1, 2023.

**References**:
- https://www.mass.gov/info-details/mass-general-laws-c62-ss-6

### ma_covid_19_essential_employee_premium_pay_program

**Label**: MA COVID 19 Essential Employee Premium Pay Program
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.mass.gov/info-details/covid-19-essential-employee-premium-pay-program

### ma_dependent_care_credit

**Label**: MA dependent care credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.mass.gov/info-details/mass-general-laws-c62-ss-6

### ma_eaedc

**Label**: Massachusetts EAEDC
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/regulations/massachusetts/department-106-CMR/title-106-CMR-701.000

### ma_eaedc_assets_limit_eligible

**Label**: Eligible based on the asset limit for the Massachusetts EAEDC
**Entity**: spm_unit
**Period**: month

**References**:
- https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-110

### ma_eaedc_countable_assets

**Label**: Massachusetts EAEDC countable assets
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

### ma_eaedc_countable_earned_income

**Label**: Massachusetts EAEDC countable earned income
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-500

### ma_eaedc_dependent_care_deduction

**Label**: Massachusetts EAEDC dependent care deduction
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-275

### ma_eaedc_dependent_care_deduction_person

**Label**: Massachusetts EAEDC dependent care deduction for each person
**Entity**: person
**Period**: month
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-275

### ma_eaedc_earned_income_after_disregard_person

**Label**: Massachusetts EAEDC earned income after disregard for each person
**Entity**: person
**Period**: month
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-500

### ma_eaedc_eligible

**Label**: Eligible for the Massachusetts EAEDC
**Entity**: spm_unit
**Period**: month

**References**:
- https://www.law.cornell.edu/regulations/massachusetts/106-CMR-703-010

### ma_eaedc_eligible_caretaker_family

**Label**: Eligible caretaker family for the Massachusetts EAEDC
**Entity**: spm_unit
**Period**: month

**References**:
- https://www.law.cornell.edu/regulations/massachusetts/106-CMR-703-700

### ma_eaedc_eligible_dependent

**Label**: Eligible dependent for the Massachusetts EAEDC dependent care deduction
**Entity**: person
**Period**: month

**References**:
- https://www.law.cornell.edu/regulations/massachusetts/106-CMR-703-200

### ma_eaedc_eligible_disabled_dependent_present

**Label**: Disabled dependent present for Massachusetts EAEDC
**Entity**: spm_unit
**Period**: month

**References**:
- https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-340

### ma_eaedc_eligible_disabled_head_or_spouse

**Label**: Disabled head or spouse present for Massachusetts EAEDC
**Entity**: spm_unit
**Period**: month

**References**:
- https://www.law.cornell.edu/regulations/massachusetts/106-CMR-703-010

### ma_eaedc_eligible_elderly_present

**Label**: Eligible elderly present for the Massachusetts EAEDC
**Entity**: spm_unit
**Period**: month

**References**:
- https://www.law.cornell.edu/regulations/massachusetts/106-CMR-703-600

### ma_eaedc_financial_eligible

**Label**: Financial eligible for Massachusetts EAEDC
**Entity**: spm_unit
**Period**: month

**References**:
- https://www.law.cornell.edu/regulations/massachusetts/department-106-CMR/title-106-CMR-704.000

### ma_eaedc_if_claimed

**Label**: Massachusetts EAEDC benefit amount if claimed
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/regulations/massachusetts/department-106-CMR/title-106-CMR-701.000

### ma_eaedc_immigration_status_eligible

**Label**: Eligible for the Massachusetts EAEDC based on immigration status
**Entity**: spm_unit
**Period**: month

**References**:
- https://www.law.cornell.edu/regulations/massachusetts/106-CMR-703-440

### ma_eaedc_income_eligible

**Label**: Eligible for the Massachusetts EAEDC based on income
**Entity**: spm_unit
**Period**: month

**References**:
- https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-285

### ma_eaedc_living_arrangement

**Label**: Massachusetts EAEDC living arrangement
**Entity**: spm_unit
**Period**: month

**References**:
- https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-435

### ma_eaedc_net_income

**Label**: Massachusetts EAEDC net income
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-500

### ma_eaedc_non_financial_eligible

**Label**: Non-financial eligible for Massachusetts EAEDC
**Entity**: spm_unit
**Period**: month

**References**:
- https://www.law.cornell.edu/regulations/massachusetts/106-CMR-703-010

### ma_eaedc_standard_assistance

**Label**: Massachusetts EAEDC standard assistance
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://www.mass.gov/lists/emergency-aid-to-the-elderly-disabled-and-children-eaedc-grant-calculation

### ma_eitc

**Label**: MA EITC
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.mass.gov/info-details/mass-general-laws-c62-ss-6

### ma_gross_income

**Label**: MA gross income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.mass.gov/info-details/mass-general-laws-c62-ss-2

### ma_income_tax

**Label**: MA income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Massachusetts State income tax.

**References**:
- https://www.mass.gov/doc/2021-form-1-massachusetts-resident-income-tax-return/download

### ma_income_tax_before_credits

**Label**: MA income tax before credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://malegislature.gov/Laws/GeneralLaws/PartI/TitleIX/Chapter62/Section4

### ma_income_tax_before_refundable_credits

**Label**: MA income tax before refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://malegislature.gov/Laws/GeneralLaws/PartI/TitleIX/Chapter62/Section4

### ma_income_tax_exemption_threshold

**Label**: MA income tax exemption threshold
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

MA AGI threshold below which an individual is exempt from State income tax.

**References**:
- https://malegislature.gov/Laws/GeneralLaws/PartI/TitleIX/Chapter62/Section5

### ma_liheap

**Label**: Massachusetts LIHEAP payment
**Entity**: spm_unit
**Period**: year

**References**:
- https://www.mass.gov/doc/fy-2025-heap-income-eligibility-benefit-chart-may-8-2025/download

### ma_liheap_benefit_level

**Label**: Benefit Level for Massachusetts LIHEAP payment
**Entity**: spm_unit
**Period**: year

**References**:
- https://www.mass.gov/doc/fy-2025-heap-income-eligibility-benefit-chart-may-8-2025/download

### ma_liheap_eligible

**Label**: Eligible for the Massachusetts LIHEAP
**Entity**: spm_unit
**Period**: year

**References**:
- https://www.mass.gov/info-details/learn-about-home-energy-assistance-heap
- https://liheapch.acf.gov/tables/subsidize.htm#MA

### ma_liheap_eligible_subsidized_housing

**Label**: Massachusetts LIHEAP eligible subsidized housing
**Entity**: spm_unit
**Period**: year

**References**:
- https://liheapch.acf.gov/tables/subsidize.htm#MA

### ma_liheap_fpg

**Label**: Massachusetts LIHEAP federal poverty guideline
**Entity**: spm_unit
**Period**: year

**References**:
- https://www.mass.gov/doc/fy-2025-heap-income-eligibility-benefit-chart-may-8-2025/download

### ma_liheap_heating_type

**Label**: Massachusetts LIHEAP household's heating type
**Entity**: spm_unit
**Period**: year

**References**:
- https://www.mass.gov/doc/fy-2025-heap-income-eligibility-benefit-chart-may-8-2025/download

### ma_liheap_hecs_eligible

**Label**: Eligible for Massachusetts LIHEAP High Energy Cost Supplement (HECS)
**Entity**: spm_unit
**Period**: year

**References**:
- https://www.mass.gov/doc/fy-2025-heap-income-eligibility-benefit-chart-may-8-2025/download

### ma_liheap_hecs_payment

**Label**: Massachusetts LIHEAP High Energy Cost Supplement (HECS) payment
**Entity**: spm_unit
**Period**: year

**References**:
- https://www.mass.gov/doc/fy-2025-heap-income-eligibility-benefit-chart-may-8-2025/download

### ma_liheap_income

**Label**: Massachusetts LIHEAP income
**Entity**: spm_unit
**Period**: year

**References**:
- https://www.mass.gov/info-details/learn-about-home-energy-assistance-heap

### ma_liheap_income_eligible

**Label**: Eligible for Massachusetts LIHEAP due to income
**Entity**: spm_unit
**Period**: year

**References**:
- https://www.mass.gov/info-details/learn-about-home-energy-assistance-heap

### ma_liheap_standard_payment

**Label**: Massachusetts LIHEAP standard payment
**Entity**: spm_unit
**Period**: year

**References**:
- https://www.mass.gov/doc/fy-2025-heap-income-eligibility-benefit-chart-may-8-2025/download

### ma_liheap_state_median_income_threshold

**Label**: Massachusetts LIHEAP state median income threshold
**Entity**: spm_unit
**Period**: year

**References**:
- https://www.mass.gov/info-details/learn-about-home-energy-assistance-heap

### ma_liheap_utility_category

**Label**: Massachusetts LIHEAP household's utility category
**Entity**: spm_unit
**Period**: year

**References**:
- https://www.mass.gov/doc/fy-2025-heap-income-eligibility-benefit-chart-may-8-2025/download

### ma_limited_income_tax_credit

**Label**: MA Limited Income Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.mass.gov/doc/2021-schedule-nts-l-nrpy-no-tax-status-and-limited-income-credit/download

### ma_maximum_state_supplement

**Label**: Massachusetts maximum State Supplement payment amount
**Entity**: person
**Period**: year
**Unit**: currency-USD

### ma_mbta_enrolled_in_applicable_programs

**Label**: Enrolled in applicable programs to receive the Massachusetts Bay Transportation Authority income-eligible reduced fare program
**Entity**: person
**Period**: year

**References**:
- https://www.mbta.com/fares/reduced/income-eligible

### ma_mbta_income_eligible_reduced_fare_eligible

**Label**: Eligible for the Massachusetts Bay Transportation Authority income-eligible reduced fare program
**Entity**: person
**Period**: year

**References**:
- https://www.mbta.com/fares/reduced/income-eligible

### ma_mbta_senior_charlie_card_eligible

**Label**: Eligible for the Massachusetts Bay Transportation Authority Senior Charlie Card program
**Entity**: person
**Period**: year

**References**:
- https://www.mbta.com/fares/reduced/senior-charliecard

### ma_mbta_tap_charlie_card_eligible

**Label**: Eligible for the Massachusetts Bay Transportation Authority Transportation Access Pass (TAP) Charlie Card program
**Entity**: person
**Period**: year

**References**:
- https://www.mbta.com/fares/reduced/transportation-access-pass

### ma_non_refundable_credits

**Label**: MA non-refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.mass.gov/doc/2021-form-1-massachusetts-resident-income-tax-return/download

### ma_part_a_agi

**Label**: MA Part A AGI
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.mass.gov/info-details/mass-general-laws-c62-ss-2

### ma_part_a_cg_excess_exemption

**Label**: MA Part A (short-term) capital gains excess exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.mass.gov/service-details/view-massachusetts-personal-income-tax-exemptions

### ma_part_a_div_excess_exemption

**Label**: MA Part A dividends excess exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.mass.gov/service-details/view-massachusetts-personal-income-tax-exemptions

### ma_part_a_gross_income

**Label**: MA Part A gross income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.mass.gov/info-details/mass-general-laws-c62-ss-2

### ma_part_a_taxable_capital_gains_income

**Label**: MA Part A taxable income from short-term capital gains
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.mass.gov/service-details/view-massachusetts-personal-income-tax-exemptions

### ma_part_a_taxable_dividend_income

**Label**: MA Part A taxable income from dividends
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.mass.gov/service-details/view-massachusetts-personal-income-tax-exemptions

### ma_part_a_taxable_income

**Label**: MA Part A taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.mass.gov/service-details/view-massachusetts-personal-income-tax-exemptions

### ma_part_b_agi

**Label**: MA Part B AGI
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.mass.gov/info-details/mass-general-laws-c62-ss-2

### ma_part_b_excess_exemption

**Label**: MA Part B excess exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.mass.gov/service-details/view-massachusetts-personal-income-tax-exemption

### ma_part_b_gross_income

**Label**: MA Part B gross income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.mass.gov/info-details/mass-general-laws-c62-ss-2

### ma_part_b_taxable_income

**Label**: MA Part B taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.mass.gov/service-details/view-massachusetts-personal-income-tax-exemptions

### ma_part_b_taxable_income_before_exemption

**Label**: MA Part B taxable income before exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.mass.gov/doc/2021-form-1-massachusetts-resident-income-tax-return/download

### ma_part_b_taxable_income_deductions

**Label**: MA Part B taxable income deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.mass.gov/info-details/mass-general-laws-c62-ss-3

### ma_part_b_taxable_income_exemption

**Label**: MA Part B taxable income exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.mass.gov/service-details/view-massachusetts-personal-income-tax-exemption

### ma_part_c_agi

**Label**: MA Part C AGI
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.mass.gov/info-details/mass-general-laws-c62-ss-2

### ma_part_c_gross_income

**Label**: MA Part C gross income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.mass.gov/info-details/mass-general-laws-c62-ss-2

### ma_part_c_taxable_income

**Label**: MA Part C taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.mass.gov/service-details/view-massachusetts-personal-income-tax-exemptions

### ma_refundable_credits

**Label**: MA refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.mass.gov/doc/2021-form-1-massachusetts-resident-income-tax-return/download

### ma_scb_total_income

**Label**: Total income for the MA Senior Circuit Breaker
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.mass.gov/info-details/mass-general-laws-c62-ss-6

### ma_senior_circuit_breaker

**Label**: MA Senior Circuit Breaker Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.mass.gov/info-details/mass-general-laws-c62-ss-6

### ma_state_living_arrangement

**Label**: Massachusetts State Living Arrangement
**Entity**: household
**Period**: year

**References**:
- https://www.law.cornell.edu/regulations/massachusetts/106-CMR-327-220

### ma_state_supplement

**Label**: Massachusetts State Supplement payment amount
**Entity**: person
**Period**: year

**References**:
- https://www.law.cornell.edu/regulations/massachusetts/106-CMR-327-330

### ma_tafdc

**Label**: Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC)
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://www.mass.gov/how-to/transitional-aid-to-families-with-dependent-children-tafdc

### ma_tafdc_age_limit

**Label**: Applicable age limit for the Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC)
**Entity**: person
**Period**: year

**References**:
- https://www.law.cornell.edu/regulations/massachusetts/106-CMR-703-200

### ma_tafdc_applicable_income_for_financial_eligibility

**Label**: Applicable income for the Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) financial eligibility check
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-280

### ma_tafdc_applicable_income_grant_amount

**Label**: Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) countable income
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-210

### ma_tafdc_child_support_deduction

**Label**: Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) child support deduction
**Entity**: person
**Period**: month
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-250

### ma_tafdc_clothing_allowance

**Label**: Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) clothing allowance
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.masslegalservices.org/content/75-how-much-will-you-get-each-month

### ma_tafdc_countable_earned_income

**Label**: Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) countable earned income
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-281

### ma_tafdc_countable_unearned_income

**Label**: Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) countable unearned income
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://www.masslegalservices.org/content/62-what-income-counted

### ma_tafdc_dependent_care_deduction

**Label**: Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) dependent care deduction
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-275

### ma_tafdc_dependent_care_deduction_person

**Label**: Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) dependent care deduction for each person
**Entity**: person
**Period**: month
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-275

### ma_tafdc_dependent_criteria_eligible

**Label**: Eligible based on the dependent criteria for the Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC)
**Entity**: spm_unit
**Period**: year

**References**:
- https://www.law.cornell.edu/regulations/massachusetts/106-CMR-703-210

### ma_tafdc_earned_income_after_deductions

**Label**: Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) earned income after deductions
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-280

### ma_tafdc_eligible

**Label**: Eligible for Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC)
**Entity**: spm_unit
**Period**: month

**References**:
- https://www.law.cornell.edu/regulations/massachusetts/106-CMR-703-010
- https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-000

### ma_tafdc_eligible_dependent

**Label**: Eligible dependent for the Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC)
**Entity**: person
**Period**: year

**References**:
- https://www.law.cornell.edu/regulations/massachusetts/106-CMR-703-200

### ma_tafdc_eligible_infant

**Label**: Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) eligible infant
**Entity**: person
**Period**: year

**References**:
- https://www.law.cornell.edu/regulations/massachusetts/106-CMR-705-600

### ma_tafdc_exceeds_eaedc

**Label**: Whether the TAFDC value exceeds the EAEDC value
**Entity**: spm_unit
**Period**: month

**References**:
- https://www.mass.gov/how-to/transitional-aid-to-families-with-dependent-children-tafdc

### ma_tafdc_financial_eligible

**Label**: Eligible for Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) due to income
**Entity**: spm_unit
**Period**: month

**References**:
- https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-000

### ma_tafdc_full_earned_income_disregard_eligible

**Label**: Is eligible for the full earned income disregard under the Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC)
**Entity**: person
**Period**: year

**References**:
- https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-281

### ma_tafdc_if_claimed

**Label**: Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) benefit amount if claimed
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://www.mass.gov/how-to/transitional-aid-to-families-with-dependent-children-tafdc

### ma_tafdc_immigration_status_eligible

**Label**: Eligible for Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) due to immigration status
**Entity**: spm_unit
**Period**: year

**References**:
- https://www.law.cornell.edu/regulations/massachusetts/106-CMR-703-400

### ma_tafdc_infant_benefit

**Label**: Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) infant benefit
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/regulations/massachusetts/106-CMR-705-600

### ma_tafdc_non_financial_eligible

**Label**: Eligible for Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC)
**Entity**: spm_unit
**Period**: month

**References**:
- https://www.law.cornell.edu/regulations/massachusetts/106-CMR-703-010

### ma_tafdc_partially_disregarded_earned_income

**Label**: Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) partially disregarded earned income
**Entity**: person
**Period**: month
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-281

### ma_tafdc_payment_standard

**Label**: Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) payment standard
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-420

### ma_tafdc_potential_main_benefit

**Label**: Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) potential main benefit
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://www.mass.gov/how-to/transitional-aid-to-families-with-dependent-children-tafdc

### ma_tafdc_pregnancy_eligible

**Label**: Eligible for Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) due to pregnancy
**Entity**: person
**Period**: year

**References**:
- https://www.law.cornell.edu/regulations/massachusetts/106-CMR-703-210

### ma_tafdc_work_related_expense_deduction

**Label**: Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) work-related expense deduction
**Entity**: person
**Period**: month
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-270

### ma_tcap_gross_earned_income

**Label**: Massachusetts Transitional Cash Assistance Program (TCAP) gross earned income
**Entity**: person
**Period**: month
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-210

### ma_tcap_gross_unearned_income

**Label**: Massachusetts Transitional Cash Assistance Program (TCAP) gross unearned income
**Entity**: person
**Period**: month
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-210

### ma_withheld_income_tax

**Label**: Massachusetts withheld income tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

### marginal_tax_rate

**Label**: marginal tax rate
**Entity**: person
**Period**: year
**Unit**: /1

Fraction of marginal income gains that do not increase household net income.

### marginal_tax_rate_including_health_benefits

**Label**: Marginal tax rate including health benefits
**Entity**: person
**Period**: year
**Unit**: /1

Fraction of marginal income gains that do not increase household net income.

### marginal_tax_rate_on_capital_gains

**Label**: capital gains marginal tax rate
**Entity**: person
**Period**: year
**Unit**: /1

Percent of marginal capital gains that do not increase household net income.

### marital_unit_id

**Label**: Marital unit ID
**Entity**: marital_unit
**Period**: year

### marital_unit_weight

**Label**: Marital unit weight
**Entity**: marital_unit
**Period**: year

### market_income

**Label**: Market income
**Entity**: person
**Period**: year
**Unit**: currency-USD

Income from all non-government sources

### md_aged_blind_exemptions

**Label**: MD aged blind exemptions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://govt.westlaw.com/mdc/Document/NF59A76006EA511E8ABBEE50DE853DFF4?viewType=FullText&originationContext=documenttoc&transitionType=CategoryPageItem&contextData=(sc.Default)

### md_aged_dependent_exemption

**Label**: MD aged dependent exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://govt.westlaw.com/mdc/Document/NF59A76006EA511E8ABBEE50DE853DFF4?viewType=FullText&originationContext=documenttoc&transitionType=CategoryPageItem&contextData=(sc.Default)

### md_aged_exemption

**Label**: MD aged exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://govt.westlaw.com/mdc/Document/NF59A76006EA511E8ABBEE50DE853DFF4?viewType=FullText&originationContext=documenttoc&transitionType=CategoryPageItem&contextData=(sc.Default)

### md_agi

**Label**: MD AGI
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://govt.westlaw.com/mdc/Browse/Home/Maryland/MarylandCodeCourtRules?guid=NAE804370A64411DBB5DDAC3692B918BC&transitionType=Default&contextData=%28sc.Default%29

### md_blind_exemption

**Label**: MD blind exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://govt.westlaw.com/mdc/Document/NF59A76006EA511E8ABBEE50DE853DFF4?viewType=FullText&originationContext=documenttoc&transitionType=CategoryPageItem&contextData=(sc.Default)

### md_capital_gains_surtax

**Label**: Maryland capital gains surtax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://mgaleg.maryland.gov/2025RS/Chapters_noln/CH_604_hb0352e.pdf#page=162

### md_capital_gains_surtax_applies

**Label**: Maryland capital gains surtax applies
**Entity**: tax_unit
**Period**: year

**References**:
- https://mgaleg.maryland.gov/2025RS/Chapters_noln/CH_604_hb0352e.pdf#page=162

### md_cdcc

**Label**: MD CDCC
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Maryland Child and Dependent Care Tax Credit

**References**:
- https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-7-income-tax-credits/section-10-716-for-child-care-or-dependent-care

### md_ctc

**Label**: Maryland Child Tax Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-7-income-tax-credits/section-10-751-effective-until-712026-tax-credit-for-qualified-child
- https://law.justia.com/codes/maryland/2022/tax-general/title-10/subtitle-7/section-10-751/
- https://mgaleg.maryland.gov/2025RS/Chapters_noln/CH_604_hb0352e.pdf#page=169

### md_ctc_eligible

**Label**: Eligible for the Maryland Child Tax Credit
**Entity**: tax_unit
**Period**: year

**References**:
- https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-7-income-tax-credits/section-10-751-effective-until-712026-tax-credit-for-qualified-child
- https://law.justia.com/codes/maryland/2022/tax-general/title-10/subtitle-7/section-10-751/
- https://mgaleg.maryland.gov/2025RS/Chapters_noln/CH_604_hb0352e.pdf#page=169

### md_deductions

**Label**: MD deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://govt.westlaw.com/mdc/Document/N05479690A64A11DBB5DDAC3692B918BC?viewType=FullText&originationContext=documenttoc&transitionType=CategoryPageItem&contextData=(sc.Default)https://www.marylandtaxes.gov/forms/21_forms/Resident_Booklet.pdf#page=5https://www.marylandtaxes.gov/forms/22_forms/Resident_Booklet.pdf#page=5

### md_dependent_care_subtraction

**Label**: MD depdendent care subtraction from AGI
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-2-maryland-taxable-income-calculations-for-individual/part-ii-maryland-adjusted-gross-income/section-10-208-effective-until-712024-subtractions-from-federal-adjusted-gross-income-state-adjustmentshttps://www.marylandtaxes.gov/forms/21_forms/Resident_Booklet.pdf#page=13https://www.marylandtaxes.gov/forms/21_forms/Resident_Booklet.pdf#page=13

### md_eitc

**Label**: MD total EITC
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Refundable and non-refundable Maryland EITC

**References**:
- https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-7-income-tax-credits/section-10-704-effective-until-6302023-for-earned-income

### md_exemptions

**Label**: MD exemptions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### md_hundred_year_subtraction

**Label**: Maryland hundred year subtraction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://trackbill.com/bill/maryland-house-bill-186-income-tax-subtraction-modification-for-centenarians/2173534/

### md_hundred_year_subtraction_eligible

**Label**: Eligible for the Maryland hundred year subtraction
**Entity**: person
**Period**: year

**References**:
- https://trackbill.com/bill/maryland-house-bill-186-income-tax-subtraction-modification-for-centenarians/2173534/

### md_hundred_year_subtraction_person

**Label**: Maryland hundred year subtraction per person
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://trackbill.com/bill/maryland-house-bill-186-income-tax-subtraction-modification-for-centenarians/2173534/

### md_income_tax

**Label**: MD income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### md_income_tax_before_credits

**Label**: MD income tax before credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### md_income_tax_before_refundable_credits

**Label**: MD income tax after non-refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### md_itemized_deductions

**Label**: Maryland itemized deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://govt.westlaw.com/mdc/Document/N05479690A64A11DBB5DDAC3692B918BC?viewType=FullText&originationContext=documenttoc&transitionType=CategoryPageItem&contextData=(sc.Default)
- https://www.marylandtaxes.gov/forms/21_forms/Resident_Booklet.pdf#page=5
- https://www.marylandtaxes.gov/forms/22_forms/Resident_Booklet.pdf#page=5
- https://mgaleg.maryland.gov/2025RS/Chapters_noln/CH_604_hb0352e.pdf#page=167

### md_local_income_tax_before_credits

**Label**: MD local income tax before credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### md_married_or_has_child_non_refundable_eitc

**Label**: Maryland non-refundable EITC for filers who are married or have qualifying child
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-7-income-tax-credits/section-10-704-effective-until-6302023-for-earned-income

### md_married_or_has_child_refundable_eitc

**Label**: Maryland refundable EITC for filers who are married or have qualifying child
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.marylandtaxes.gov/forms/21_forms/Resident_Booklet.pdf#page=23

### md_montgomery_eitc

**Label**: Montgomery County, Maryland EITC
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www3.montgomerycountymd.gov/311/Solutions.aspx?SolutionId=1-4DAM0I

### md_non_refundable_credits

**Label**: MD non-refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Maryland non-refundable tax credits

### md_non_refundable_eitc

**Label**: MD EITC non-refundable State tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Non-refundable EITC credit reducing MD State income tax.

**References**:
- https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-7-income-tax-credits/section-10-704-effective-until-6302023-for-earned-income

### md_pension_subtraction

**Label**: MD pension subtraction from AGI
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.marylandtaxes.gov/forms/21_forms/Resident_Booklet.pdf#page=13

### md_pension_subtraction_amount

**Label**: MD pension subtraction from AGI
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.marylandtaxes.gov/forms/21_forms/Resident_Booklet.pdf#page=13

### md_personal_exemption

**Label**: MD value per personal exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-2-maryland-taxable-income-calculations-for-individual/part-iii-exemptions/section-10-211-individuals-other-than-fiduciaries?searchWithin=true&listingIndexId=code-of-maryland.article-tax-general&q=blind&type=statute&sort=relevance&p=1

### md_poverty_line_credit

**Label**: MD Poverty Line Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/maryland/2021/tax-general/title-10/subtitle-7/section-10-709/

### md_qualifies_for_unmarried_childless_eitc

**Label**: Qualifies for the MD unmarried childless EITC
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-7-income-tax-credits/section-10-704-effective-until-6302023-for-earned-income

### md_refundable_cdcc

**Label**: MD refundable CDCC
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Maryland refundable Child and Dependent Care Tax Credit

**References**:
- https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-7-income-tax-credits/section-10-716-for-child-care-or-dependent-care

### md_refundable_credits

**Label**: MD refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Maryland refundable tax credits

### md_refundable_eitc

**Label**: MD EITC refundable State tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Refundable EITC credit reducing MD State income tax.

**References**:
- https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-7-income-tax-credits/section-10-704-effective-until-6302023-for-earned-income

### md_senior_tax_credit

**Label**: Maryland Senior Tax Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.marylandtaxes.gov/forms/22_forms/Resident_Booklet.pdf#page=15

### md_senior_tax_credit_eligible

**Label**: Eligible for the Maryland Senior Tax Credit
**Entity**: tax_unit
**Period**: year

**References**:
- https://www.marylandtaxes.gov/forms/22_forms/Resident_Booklet.pdf#page=15

### md_snap_elderly_present

**Label**: Elderly person is present for the Maryland SNAP minimum allotment
**Entity**: spm_unit
**Period**: year

### md_snap_is_elderly

**Label**: Is an elderly person for Maryland SNAP minimum allotment
**Entity**: person
**Period**: year

### md_socsec_subtraction

**Label**: MD social security subtraction from AGI
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.marylandtaxes.gov/forms/21_forms/Resident_Booklet.pdf#page=14

### md_socsec_subtraction_amount

**Label**: MD social security subtraction from AGI
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.marylandtaxes.gov/forms/21_forms/Resident_Booklet.pdf#page=14

### md_standard_deduction

**Label**: MD standard deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://govt.westlaw.com/mdc/Document/NC8EB19606F6911E8A99BCF2C90B83D38?viewType=FullText&originationContext=documenttoc&transitionType=CategoryPageItem&contextData=(sc.Default)#co_anchor_I552E3B107DF711ECA8F2FF3A9E62BB69
- https://mgaleg.maryland.gov/2025RS/Chapters_noln/CH_604_hb0352e.pdf#page=165

### md_tanf_count_children

**Label**: Maryland TANF number of children
**Entity**: spm_unit
**Period**: year

### md_tanf_eligible

**Label**: Maryland TANF eligible
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### md_tanf_gross_earned_income_deduction

**Label**: Maryland TANF earned income deduction
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### md_tanf_maximum_benefit

**Label**: Maryland TANF maximum benefit
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### md_tax_unit_earned_income

**Label**: MD tax unit earned income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### md_taxable_income

**Label**: MD taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### md_total_additions

**Label**: MD total additions to AGI
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### md_total_personal_exemptions

**Label**: MD total personal exemptions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### md_total_subtractions

**Label**: MD total subtractions from AGI
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### md_two_income_subtraction

**Label**: MD two-income married couple subtraction from AGI
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.marylandtaxes.gov/forms/21_forms/Resident_Booklet.pdf#page=16https://govt.westlaw.com/mdc/Document/NF93A7BD2E6C811ECA065A3F5EAA0E5C9?viewType=FullText&originationContext=documenttoc&transitionType=CategoryPageItem&contextData=(sc.Default)

### md_unmarried_childless_non_refundable_eitc

**Label**: Maryland unmarried childless non-refundable EITC
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-7-income-tax-credits/section-10-704-effective-until-6302023-for-earned-income

### md_unmarried_childless_refundable_eitc

**Label**: Maryland unmarried childless refundable EITC
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.marylandtaxes.gov/forms/21_forms/Resident_Booklet.pdf#page=19

### md_withheld_income_tax

**Label**: Maryland withheld income tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

### me_additions

**Label**: Maine AGI additions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Additions to ME AGI over federal AGI.

**References**:
- {'title': 'Schedule 1A, Income Addition Modifications', 'href': 'https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/22_1040me_sched_1a_ff.pdf'}

### me_agi

**Label**: Maine adjusted gross income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/22_1040me_dwnld_ff.pdf

### me_agi_subtractions

**Label**: ME AGI subtractions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Subtractions from ME AGI over federal AGI.

**References**:
- https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/22_1040me_sched_1s_ff.pdf

### me_child_care_credit

**Label**: Maine child care credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.mainelegislature.org/legis/statutes/36/title36sec5218.html
- https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/22_1040me_sched_a_ff.pdf#page=2

### me_deduction_phaseout_percentage

**Label**: Maine deduction phaseout percentage
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.mainelegislature.org/legis/statutes/36/title36sec5124-C.html
- https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/22_item_stand_%20ded_phaseout_wksht.pdf

### me_deductions

**Label**: Maine income deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.mainelegislature.org/legis/statutes/36/title36sec5124-C.html
- https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/22_item_stand_%20ded_phaseout_wksht.pdf

### me_dependent_exemption_credit

**Label**: Maine dependent exemption credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.mainelegislature.org/legis/statutes/36/title36sec5219-SS.html

### me_eitc

**Label**: Maine EITC
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.mainelegislature.org/legis/statutes/36/title36sec5219-S.html

### me_exemptions

**Label**: Maine income exemptions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.mainelegislature.org/legis/statutes/36/title36sec5126-A.html

### me_income_tax

**Label**: Maine income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### me_income_tax_before_credits

**Label**: Maine main income tax (before credits and supplemental tax)
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### me_income_tax_before_refundable_credits

**Label**: Maine income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### me_itemized_deductions_pre_phaseout

**Label**: Maine itemized deductions before phaseout
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/22_1040me_sched_2_ff.pdf
- https://www.mainelegislature.org/legis/statutes/36/title36sec5125.html

### me_non_refundable_child_care_credit

**Label**: Maine non-refundable child care credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

The portion of the Maine Child Care Credit that is non-refundable.

**References**:
- https://www.mainelegislature.org/legis/statutes/36/title36sec5218.html
- https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/22_1040me_sched_a_ff.pdf#page=2

### me_non_refundable_credits

**Label**: Maine non refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### me_pension_income_deduction

**Label**: Maine pension income deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Maine pension income deduction, which subtracts from federal AGI to compute Maine AGI.

**References**:
- https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/22_1040me_sched_1s_ff.pdf

### me_personal_exemption_deduction

**Label**: Maine personal exemption deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### me_property_tax_fairness_credit

**Label**: Maine property tax fairness credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/23_1040me_sched_pstfc_ff.pdf#page=1
- https://legislature.maine.gov/statutes/36/title36sec5219-KK.html

### me_property_tax_fairness_credit_base_cap

**Label**: Maine property tax fairness credit base cap
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### me_property_tax_fairness_credit_benefit_base

**Label**: Maine property tax fairness credit benefit base
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### me_property_tax_fairness_credit_cap

**Label**: Maine property tax fairness credit cap
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### me_property_tax_fairness_credit_countable_rent

**Label**: Countable rent for Maine property tax fairness credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/22_1040me_sched_pstfc_ff.pdf#page=2

### me_property_tax_fairness_credit_countable_rent_property_tax

**Label**: Countable rent and property tax for Maine property tax fairness credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### me_property_tax_fairness_credit_eligible

**Label**: Eligible for the maine property tax fairness credit
**Entity**: tax_unit
**Period**: year

### me_property_tax_fairness_credit_veterans_cap

**Label**: Veterans cap for Maine property tax fairness credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### me_refundable_child_care_credit

**Label**: Maine refundable child care credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Refundable portion of the Maine child care credit

**References**:
- https://www.mainelegislature.org/legis/statutes/36/title36sec5218.html
- https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/22_1040me_sched_a_ff.pdf#page=2

### me_refundable_credits

**Label**: Maine refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### me_sales_and_property_tax_fairness_credit_income

**Label**: Maine sales and property tax fairness credit total income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://legislature.maine.gov/statutes/36/title36sec5219-KK.html

### me_sales_tax_fairness_credit

**Label**: Maine sales tax fairness credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://legislature.maine.gov/statutes/36/title36sec5213-A.html

### me_sales_tax_fairness_credit_eligible

**Label**: Eligible for the Maine sales tax fairness credit
**Entity**: tax_unit
**Period**: year

**References**:
- https://legislature.maine.gov/statutes/36/title36sec5213-A.html

### me_step_4_share_of_child_care_expenses

**Label**: Maine step 4 share of child care expenses
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Share of child care expenses that are from programs classified as Step 4 in Maine

**References**:
- https://www.mainelegislature.org/legis/statutes/36/title36sec5218.html
- https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/22_1040me_sched_a_ff.pdf#page=2

### me_taxable_income

**Label**: Maine taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

ME AGI less taxable income deductions

**References**:
- https://www.nysenate.gov/legislation/laws/TAX/611

### me_withheld_income_tax

**Label**: Maine withheld income tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

### medicaid

**Label**: Medicaid
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/42/1396a

### medicaid_category

**Label**: Medicaid category
**Entity**: person
**Period**: year

### medicaid_cost

**Label**: Medicaid_cost
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/42/1396a

### medicaid_cost_if_enrolled

**Label**: Per capita Medicaid cost by eligibility group & state
**Entity**: person
**Period**: year
**Unit**: currency-USD

### medicaid_enrolled

**Label**: Medicaid enrolled
**Entity**: person
**Period**: year

**References**:
- https://www.law.cornell.edu/uscode/text/42/1396a

### medicaid_group

**Label**: Medicaid spending group
**Entity**: person
**Period**: year

### medicaid_income_level

**Label**: Medicaid/CHIP-related income level
**Entity**: person
**Period**: year
**Unit**: /1

Modified AGI as a fraction of current-year federal poverty line.

### medicaid_magi

**Label**: Medicaid/CHIP/ACA-related Modified AGI
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Medicaid/CHIP/ACA-related modified AGI for this tax unit.

**References**:
- https://www.law.cornell.edu/uscode/text/42/1396a#e_14_G
- https://www.law.cornell.edu/uscode/text/26/36B#d_2

### medicaid_rating_area

**Label**: Medicaid rating area
**Entity**: household
**Period**: year

### medicaid_take_up_seed

**Label**: Randomly assigned seed for Medicaid take-up
**Entity**: person
**Period**: year

### medicaid_work_requirement_eligible

**Label**: Eligible person for Medicaid via work requirement
**Entity**: person
**Period**: year

**References**:
- https://www.congress.gov/bill/119th-congress/house-bill/1/text

### medical_expense_deduction

**Label**: Medical expense deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Medical expenses deducted from taxable income.

**References**:
- https://www.law.cornell.edu/uscode/text/26/213

### medical_out_of_pocket_expenses

**Label**: Medical out of pocket expenses
**Entity**: person
**Period**: year
**Unit**: currency-USD

### medicare_part_b_premiums

**Label**: Medicare Part B premiums
**Entity**: person
**Period**: year
**Unit**: currency-USD

### meets_ccdf_activity_test

**Label**: Activity test for CCDF
**Entity**: spm_unit
**Period**: year

Indicates whether parent or parents meet activity test (working/in job training/in educational program)

### meets_ctc_child_identification_requirements

**Label**: Child meets CTC identification requirements
**Entity**: person
**Period**: year

**References**:
- https://www.law.cornell.edu/uscode/text/26/24#h_7

### meets_ctc_identification_requirements

**Label**: Person meets CTC identification requirements
**Entity**: person
**Period**: year

**References**:
- https://www.congress.gov/bill/119th-congress/house-bill/1/text

### meets_eitc_identification_requirements

**Label**: Person meets EITC identification requirements
**Entity**: person
**Period**: year

**References**:
- https://www.law.cornell.edu/uscode/text/26/32#c_1_E
- https://www.law.cornell.edu/uscode/text/26/32#c_3_D_i
- https://www.law.cornell.edu/uscode/text/26/32#m
- https://www.ssa.gov/OP_Home/ssact/title02/0205.htm

### meets_school_meal_categorical_eligibility

**Label**: School meal categorical eligibility
**Entity**: spm_unit
**Period**: year

Whether this SPM unit is eligible for free school meal via participation in other programs

**References**:
- https://www.law.cornell.edu/cfr/text/7/245.2

### meets_snap_abawd_work_requirements

**Label**: Person is eligible for SNAP benefits via Able-Bodied Adult Without Dependents (ABAWD) work requirements
**Entity**: person
**Period**: month

**References**:
- https://www.law.cornell.edu/cfr/text/7/273.24

### meets_snap_asset_test

**Label**: Meets SNAP asset test
**Entity**: spm_unit
**Period**: year

Whether the SPM unit's financial resources are within SNAP's allowable limit

### meets_snap_categorical_eligibility

**Label**: SNAP categorical eligibility
**Entity**: spm_unit
**Period**: month

Whether this SPM unit is eligible for SNAP benefits via participation in other programs

**References**:
- https://fns-prod.azureedge.net/sites/default/files/resource-files/fna-2008-amended-through-pl-116-94.pdf#page=11

### meets_snap_general_work_requirements

**Label**: Person is eligible for SNAP benefits via general work requirements
**Entity**: person
**Period**: month

**References**:
- https://www.law.cornell.edu/cfr/text/7/273.7

### meets_snap_gross_income_test

**Label**: Meets SNAP gross income test
**Entity**: spm_unit
**Period**: month

Whether this SPM unit meets the SNAP gross income test

**References**:
- https://www.law.cornell.edu/uscode/text/7/2017#a
- https://www.law.cornell.edu/uscode/text/7/2014#c

### meets_snap_net_income_test

**Label**: Meets SNAP net income test
**Entity**: spm_unit
**Period**: month

Whether this SPM unit meets the SNAP net income test

**References**:
- https://www.law.cornell.edu/uscode/text/7/2017#a
- https://www.law.cornell.edu/uscode/text/7/2014#c

### meets_snap_work_requirements

**Label**: SPM Unit is eligible for SNAP benefits via work requirements
**Entity**: spm_unit
**Period**: month

**References**:
- https://www.fns.usda.gov/snap/work-requirements

### meets_ssi_resource_test

**Label**: Meets SSI resource test
**Entity**: person
**Period**: year
**Unit**: currency-USD

### meets_tanf_non_cash_asset_test

**Label**: Meets asset test for TANF non-cash benefit
**Entity**: spm_unit
**Period**: month

Asset eligibility for TANF non-cash benefit for SNAP BBCE

### meets_tanf_non_cash_gross_income_test

**Label**: Meets gross income test for TANF non-cash benefit
**Entity**: spm_unit
**Period**: month

Income eligibility (gross income as a percent of the poverty line) for TANF non-cash benefit for SNAP BBCE

### meets_tanf_non_cash_net_income_test

**Label**: Meets net income test for TANF non-cash benefit
**Entity**: spm_unit
**Period**: month

Income eligibility (net income as a percent of the poverty line) for TANF non-cash benefit for SNAP BBCE

### meets_wic_categorical_eligibility

**Label**: Meets WIC categorical (program participation) eligibility
**Entity**: person
**Period**: month

Meets the program participation eligibility criteria for WIC

**References**:
- https://www.law.cornell.edu/uscode/text/42/1786#d_2_A

### meets_wic_income_test

**Label**: Meets WIC income test
**Entity**: spm_unit
**Period**: month

Meets income test for the Special Supplemental Nutrition Program for Women, Infants and Children (WIC)

**References**:
- https://www.law.cornell.edu/uscode/text/42/1786#d_2_A_i

### metered_gas_expense

**Label**: Metered gas expense
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### mi_additions

**Label**: Michigan taxable income additions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/Schedule-1.pdf
- https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf
- https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/MI-1040.pdf

### mi_allowable_homestead_property_tax_credit

**Label**: Michigan allowable homestead property tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- http://legislature.mi.gov/doc.aspx?mcl-206-508
- https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/MI-1040CR.pdf#page=2

### mi_alternate_home_heating_credit

**Label**: Michigan alternate home heating credit amount
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.michigan.gov/-/media/Project/Websites/taxes/2022RM/IIT/MI-1040CR7.pdf?rev=84f72df3f8664b96903aa6b655dc34d2http://www.legislature.mi.gov/(S(keapvg1h2vndkn25rtmpyyse))/mileg.aspx?page=getObject&objectName=mcl-206-527a

### mi_alternate_home_heating_credit_eligible

**Label**: Eligible for the Michigan alternate home heating credit
**Entity**: tax_unit
**Period**: year

**References**:
- https://www.michigan.gov/-/media/Pxroject/Websites/taxes/2022RM/IIT/MI-1040CR7.pdf?rev=84f72df3f8664b96903aa6b655dc34d2http://www.legislature.mi.gov/(S(keapvg1h2vndkn25rtmpyyse))/mileg.aspx?page=getObject&objectName=mcl-206-527a

### mi_disabled_exemption_eligible_person

**Label**: Eligible person for the Michigan disabled exemptions
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- http://legislature.mi.gov/doc.aspx?mcl-206-30
- https://www.legislature.mi.gov/Publications/TaxpayerGuide.pdf

### mi_eitc

**Label**: Michigan Earned Income Tax Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### mi_exemptions

**Label**: Michigan exemptions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- http://legislature.mi.gov/doc.aspx?mcl-206-30
- https://www.legislature.mi.gov/Publications/TaxpayerGuide.pdf

### mi_exemptions_count

**Label**: Michigan exemptions count
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- http://legislature.mi.gov/doc.aspx?mcl-206-30
- https://www.legislature.mi.gov/Publications/TaxpayerGuide.pdf
- https://www.michigan.gov/-/media/Project/Websites/taxes/2022RM/IIT/MI-1040CR7.pdf
- https://www.michigan.gov/-/media/Project/Websites/taxes/2022RM/IIT/BOOK_MI-1040CR-7.pdf#page=7

### mi_expanded_retirement_benefits_deduction

**Label**: Michigan expanded retirement benefits deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- http://legislature.mi.gov/doc.aspx?mcl-206-30
- https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits/michigan-standard-deduction
- https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2023/2023-IIT-Forms/BOOK_MI-1040.pdf#page=25

### mi_expanded_retirement_benefits_deduction_eligible

**Label**: Eligible for the Michigan expanded retirement benefits deduction
**Entity**: tax_unit
**Period**: year

**References**:
- http://legislature.mi.gov/doc.aspx?mcl-206-30
- https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits/michigan-standard-deduction
- https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2023/2023-IIT-Forms/BOOK_MI-1040.pdf#page=20

### mi_home_heating_credit

**Label**: Michigan home heating credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.michigan.gov/taxes/iit/accordion/credits/table-a-2022-home-heating-credit-mi-1040cr-7-standard-allowancehttp://www.legislature.mi.gov/(S(keapvg1h2vndkn25rtmpyyse))/mileg.aspx?page=getObject&objectName=mcl-206-527a

### mi_home_heating_credit_eligible_rate

**Label**: Eligible for the Michigan home heating credit
**Entity**: tax_unit
**Period**: year

### mi_homestead_property_tax_credit

**Label**: Michigan homestead property tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/MI-1040CR.pdf#page=2
- https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=34

### mi_homestead_property_tax_credit_alternate_senior_amount

**Label**: Michigan alternate senior renter homestead property tax credit amount
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/MI-1040CR.pdf#page=2
- https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=34

### mi_homestead_property_tax_credit_countable_property_tax

**Label**: Michigan homestead property tax credit countable property tax (including rent equivalent)
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- http://legislature.mi.gov/doc.aspx?mcl-206-520
- https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/MI-1040CR.pdf#page=1

### mi_homestead_property_tax_credit_eligible

**Label**: Eligible for the Michigan homestead property tax credit
**Entity**: tax_unit
**Period**: year

**References**:
- http://legislature.mi.gov/doc.aspx?mcl-206-508
- https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/MI-1040CR.pdf#page=1
- https://www.legislature.mi.gov/Publications/TaxpayerGuide.pdf#page=16

### mi_homestead_property_tax_credit_household_resource_exemption

**Label**: Michigan homestead property tax credit household resource exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- http://legislature.mi.gov/doc.aspx?mcl-206-508
- https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/MI-1040CR.pdf#page=2

### mi_homestead_property_tax_credit_pre_alternate_senior_amount

**Label**: Michigan homestead property tax credit per alternate senior credit amount
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- http://legislature.mi.gov/doc.aspx?mcl-206-508
- https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/MI-1040CR.pdf#page=2
- https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=34

### mi_household_resources

**Label**: Michigan household resources
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/michigan/2022/chapter-206/statute-act-281-of-1967/division-281-1967-1/division-281-1967-1-9/section-206-508/

### mi_income_tax

**Label**: Michigan income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### mi_income_tax_before_non_refundable_credits

**Label**: Michigan income tax before non-refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### mi_income_tax_before_refundable_credits

**Label**: Michigan income tax before refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### mi_interest_dividends_capital_gains_deduction

**Label**: Michigan interest, dividends, and capital gains deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Michigan interest, dividends, and capital gains deduction of qualifying age.

**References**:
- http://legislature.mi.gov/doc.aspx?mcl-206-30
- https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=16

### mi_interest_dividends_capital_gains_deduction_eligible

**Label**: Eligible for the Michigan interest dividends capital gains deduction
**Entity**: tax_unit
**Period**: year

**References**:
- http://legislature.mi.gov/doc.aspx?mcl-206-30
- https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=16

### mi_is_senior_for_tax

**Label**: Michigan filer is a senior
**Entity**: tax_unit
**Period**: year

**References**:
- http://legislature.mi.gov/doc.aspx?mcl-206-514

### mi_non_refundable_credits

**Label**: Michigan non-refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### mi_pension_benefit

**Label**: Michigan pension benefit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Michigan retirement and pension benefits of qualifying age.

**References**:
- http://legislature.mi.gov/doc.aspx?mcl-206-30
- https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=18
- https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits

### mi_personal_exemptions

**Label**: Michigan personal and stillborn exemptions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- http://legislature.mi.gov/doc.aspx?mcl-206-30
- https://www.legislature.mi.gov/Publications/TaxpayerGuide.pdf

### mi_refundable_credits

**Label**: Michigan refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### mi_retirement_benefits_deduction_tier_one

**Label**: Michigan retirement benefits deduction for tier one
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- http://legislature.mi.gov/doc.aspx?mcl-206-30
- https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=17
- https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits
- https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/4884.pdf#page=2

### mi_retirement_benefits_deduction_tier_one_amount

**Label**: Michigan retirement benefits deduction amount for tier one, regardless of eligiblity
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- http://legislature.mi.gov/doc.aspx?mcl-206-30
- https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=17
- https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits
- https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/4884.pdf#page=2

### mi_retirement_benefits_deduction_tier_one_eligible

**Label**: Eligible for the Michigan tier one retirement benefits deduction
**Entity**: tax_unit
**Period**: year

**References**:
- http://legislature.mi.gov/doc.aspx?mcl-206-30
- https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=17
- https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits

### mi_retirement_benefits_deduction_tier_three

**Label**: Michigan retirement benefits deduction for tier three
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- http://legislature.mi.gov/doc.aspx?mcl-206-30
- https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=17
- https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits

### mi_retirement_benefits_deduction_tier_three_eligible

**Label**: Eligible for the Michigan tier three retirement benefits deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- http://legislature.mi.gov/doc.aspx?mcl-206-30
- https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=17
- https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits

### mi_retirement_benefits_deduction_tier_three_ss_exempt_not_retired

**Label**: Michigan non-retired tier three retirement benefits deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- http://legislature.mi.gov/doc.aspx?mcl-206-30
- https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=17
- https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits
- https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/4884.pdf
- https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/Form-4884-Section-C-worksheet.pdf

### mi_retirement_benefits_deduction_tier_three_ss_exempt_not_retired_eligible_people

**Label**: Number of eligible people for the Michigan non-retired tier three retirement benefits deduction
**Entity**: tax_unit
**Period**: year

**References**:
- http://legislature.mi.gov/doc.aspx?mcl-206-30
- https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=17
- https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits

### mi_retirement_benefits_deduction_tier_three_ss_exempt_retired

**Label**: Michigan retired tier three retirement benefits deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- http://legislature.mi.gov/doc.aspx?mcl-206-30
- https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=21
- https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits
- https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/4884.pdf

### mi_retirement_benefits_deduction_tier_three_ss_exempt_retired_eligible_people

**Label**: Eligible for the Michigan tier three retired retirement benefits deduction
**Entity**: tax_unit
**Period**: year

**References**:
- http://legislature.mi.gov/doc.aspx?mcl-206-30
- https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=18
- https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits

### mi_standard_deduction

**Label**: Michigan standard deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Michigan standard deduction of qualifying age.

**References**:
- http://legislature.mi.gov/doc.aspx?mcl-206-30
- https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits/michigan-standard-deduction
- https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=18

### mi_standard_deduction_tier_three

**Label**: Michigan tier three standard deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- http://legislature.mi.gov/doc.aspx?mcl-206-30
- https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits/michigan-standard-deduction
- https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=16

### mi_standard_deduction_tier_three_eligible

**Label**: Eligible for the Michigan standard deduction
**Entity**: tax_unit
**Period**: year

**References**:
- http://legislature.mi.gov/doc.aspx?mcl-206-30
- https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits/michigan-standard-deduction
- https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=16

### mi_standard_deduction_tier_two

**Label**: Michigan tier two standard deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- http://legislature.mi.gov/doc.aspx?mcl-206-30
- https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits/michigan-standard-deduction
- https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=15

### mi_standard_deduction_tier_two_eligible

**Label**: Eligible for the Michigan tier two standard deduction
**Entity**: tax_unit
**Period**: year

**References**:
- http://legislature.mi.gov/doc.aspx?mcl-206-30
- https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits/michigan-standard-deduction
- https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=15

### mi_standard_deduction_tier_two_increase_eligible_people

**Label**: Number of eligible people for the Michigan tier two standard deduction increase
**Entity**: tax_unit
**Period**: year

**References**:
- http://legislature.mi.gov/doc.aspx?mcl-206-30
- https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits/michigan-standard-deduction
- https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=15

### mi_standard_home_heating_credit

**Label**: Michigan standard home heating credit amount
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.michigan.gov/taxes/iit/accordion/credits/table-a-2022-home-heating-credit-mi-1040cr-7-standard-allowancehttp://www.legislature.mi.gov/(S(keapvg1h2vndkn25rtmpyyse))/mileg.aspx?page=getObject&objectName=mcl-206-527a

### mi_standard_home_heating_credit_eligible

**Label**: Eligible for the Michigan home heating standard credit
**Entity**: tax_unit
**Period**: year

### mi_subtractions

**Label**: Michigan taxable income subtractions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/Schedule-1.pdf
- https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf
- https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/MI-1040.pdf

### mi_taxable_income

**Label**: Michigan taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/Schedule-1.pdf
- https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf
- https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/MI-1040.pdf

### mi_withheld_income_tax

**Label**: Michigan withheld income tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

### military_basic_pay

**Label**: Military basic pay
**Entity**: person
**Period**: year
**Unit**: currency-USD

### military_disabled_head

**Label**: Tax unit head is legally disabled as a result of military service
**Entity**: tax_unit
**Period**: year

### military_disabled_spouse

**Label**: Tax unit spouse is legally disabled as a result of military service
**Entity**: tax_unit
**Period**: year

### military_retirement_pay

**Label**: Military retirement pay
**Entity**: person
**Period**: year
**Unit**: currency-USD

The benefits received under a United States military retirement plan, including survivor benefits.

**References**:
- https://militarypay.defense.gov/Pay/Retirement/

### military_retirement_pay_survivors

**Label**: Military retirement income paid to surviving spouses
**Entity**: person
**Period**: year
**Unit**: currency-USD

### military_service_income

**Label**: Military service income
**Entity**: person
**Period**: year
**Unit**: currency-USD

Military pay from active duty, National Guard, and/or the reserve component of the armed forces.

### min_head_spouse_earned

**Label**: Less of head and spouse's earnings
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### misc_deduction

**Label**: Miscellaneous deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/67#b

### miscellaneous_income

**Label**: Miscellaneous income
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/cfr/text/26/1.61-14

### mn_additions

**Label**: Minnesota additions to federal AGI
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.taxformfinder.org/forms/2021/2021-minnesota-form-m1m.pdfhttps://www.revenue.state.mn.us/sites/default/files/2023-01/m1m_22.pdf

### mn_amt

**Label**: Minnesota alternative minimum tax (AMT)
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.state.mn.us/sites/default/files/2023-02/m1mt_21.pdfhttps://www.revenue.state.mn.us/sites/default/files/2023-01/m1mt_22.pdf

### mn_amt_taxable_income

**Label**: Minnesota alternative minimum tax (AMT) taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.state.mn.us/sites/default/files/2023-02/m1mt_21.pdfhttps://www.revenue.state.mn.us/sites/default/files/2023-01/m1mt_22.pdf

### mn_basic_tax

**Label**: Minnesota basic tax calculated using tax rate schedules
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.state.mn.us/sites/default/files/2023-01/m1_inst_21.pdfhttps://www.revenue.state.mn.us/sites/default/files/2023-03/m1_inst_22.pdf

### mn_cdcc

**Label**: Minnesota child and dependent care expense credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.state.mn.us/sites/default/files/2023-02/m1cd_21.pdfhttps://www.revenue.state.mn.us/sites/default/files/2023-01/m1cd_22_0.pdf

### mn_charity_subtraction

**Label**: Minnesota charity subtraction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.taxformfinder.org/forms/2021/2021-minnesota-form-m1m.pdfhttps://www.revenue.state.mn.us/sites/default/files/2023-01/m1m_22.pdf

### mn_child_and_working_families_credits

**Label**: Minnesota child and working families credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revisor.mn.gov/statutes/cite/290.0661#stat.290.0661.4https://www.revisor.mn.gov/statutes/cite/290.0671https://www.revenue.state.mn.us/sites/default/files/2024-01/m1cwfc-23_1.pdf

### mn_deductions

**Label**: Minnesota deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.state.mn.us/sites/default/files/2021-12/m1_21_0.pdfhttps://www.revenue.state.mn.us/sites/default/files/2023-01/m1_inst_21.pdfhttps://www.revenue.state.mn.us/sites/default/files/2022-12/m1_22.pdfhttps://www.revenue.state.mn.us/sites/default/files/2023-03/m1_inst_22.pdf

### mn_elderly_disabled_subtraction

**Label**: Minnesota elderly/disabled subtraction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.state.mn.us/sites/default/files/2023-01/m1r_21.pdfhttps://www.revenue.state.mn.us/sites/default/files/2023-01/m1r_22.pdf

### mn_exemptions

**Label**: Minnesota exemptions amount
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.state.mn.us/sites/default/files/2021-12/m1_21_0.pdfhttps://www.revenue.state.mn.us/sites/default/files/2023-01/m1_inst_21.pdfhttps://www.revenue.state.mn.us/sites/default/files/2022-12/m1_22.pdfhttps://www.revenue.state.mn.us/sites/default/files/2023-03/m1_inst_22.pdf

### mn_income_tax

**Label**: Minnesota income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.state.mn.us/sites/default/files/2021-12/m1_21_0.pdfhttps://www.revenue.state.mn.us/sites/default/files/2023-01/m1_inst_21.pdfhttps://www.revenue.state.mn.us/sites/default/files/2022-12/m1_22.pdfhttps://www.revenue.state.mn.us/sites/default/files/2023-03/m1_inst_22.pdf

### mn_income_tax_before_credits

**Label**: Minnesota income tax before credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.state.mn.us/sites/default/files/2023-01/m1_inst_21.pdfhttps://www.revenue.state.mn.us/sites/default/files/2023-03/m1_inst_22.pdf

### mn_income_tax_before_refundable_credits

**Label**: Minnesota income tax before refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.state.mn.us/sites/default/files/2021-12/m1_21_0.pdfhttps://www.revenue.state.mn.us/sites/default/files/2023-01/m1_inst_21.pdfhttps://www.revenue.state.mn.us/sites/default/files/2022-12/m1_22.pdfhttps://www.revenue.state.mn.us/sites/default/files/2023-03/m1_inst_22.pdf

### mn_itemized_deductions

**Label**: Minnesota itemized deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.state.mn.us/sites/default/files/2021-12/m1_21_0.pdfhttps://www.revenue.state.mn.us/sites/default/files/2023-01/m1_inst_21.pdfhttps://www.revenue.state.mn.us/sites/default/files/2022-12/m1_22.pdfhttps://www.revenue.state.mn.us/sites/default/files/2023-03/m1_inst_22.pdf

### mn_itemizing

**Label**: whether or not itemizing Minnesota deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.state.mn.us/sites/default/files/2021-12/m1_21_0.pdfhttps://www.revenue.state.mn.us/sites/default/files/2023-01/m1_inst_21.pdfhttps://www.revenue.state.mn.us/sites/default/files/2022-12/m1_22.pdfhttps://www.revenue.state.mn.us/sites/default/files/2023-03/m1_inst_22.pdf

### mn_marriage_credit

**Label**: Minnesota marriage credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.state.mn.us/sites/default/files/2023-01/m1ma_21.pdfhttps://www.revenue.state.mn.us/sites/default/files/2023-01/m1ma_22.pdf

### mn_niit

**Label**: Minnesota Net Investment Income Tax (NIIT)
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.state.mn.us/sites/default/files/2024-12/m1m-24.pdfhttps://www.revisor.mn.gov/statutes/cite/290.033

### mn_nonrefundable_credits

**Label**: Minnesota nonrefundable income tax credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.state.mn.us/sites/default/files/2023-01/m1c_21.pdfhttps://www.revenue.state.mn.us/sites/default/files/2023-01/m1c_22.pdf

### mn_public_pension_subtraction

**Label**: Minnesota public pension subtraction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.taxformfinder.org/forms/2021/2021-minnesota-form-m1m.pdfhttps://www.revenue.state.mn.us/sites/default/files/2023-01/m1m_22.pdf

### mn_refundable_credits

**Label**: Minnesota refundable income tax credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.state.mn.us/sites/default/files/2023-01/m1ref_21.pdfhttps://www.revenue.state.mn.us/sites/default/files/2023-01/m1ref_22.pdf

### mn_social_security_subtraction

**Label**: Minnesota social security subtraction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.taxformfinder.org/forms/2021/2021-minnesota-form-m1m.pdfhttps://www.revenue.state.mn.us/sites/default/files/2023-01/m1m_22.pdf

### mn_standard_deduction

**Label**: Minnesota standard deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.state.mn.us/sites/default/files/2023-01/m1_inst_21.pdfhttps://www.revenue.state.mn.us/sites/default/files/2023-03/m1_inst_22.pdf

### mn_subtractions

**Label**: Minnesota subtractions from federal AGI
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.state.mn.us/sites/default/files/2021-12/m1_21_0.pdfhttps://www.revenue.state.mn.us/sites/default/files/2023-01/m1_inst_21.pdfhttps://www.revenue.state.mn.us/sites/default/files/2022-12/m1_22.pdfhttps://www.revenue.state.mn.us/sites/default/files/2023-03/m1_inst_22.pdf

### mn_taxable_income

**Label**: Minnesota taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.state.mn.us/sites/default/files/2021-12/m1_21_0.pdfhttps://www.revenue.state.mn.us/sites/default/files/2023-01/m1_inst_21.pdfhttps://www.revenue.state.mn.us/sites/default/files/2022-12/m1_22.pdfhttps://www.revenue.state.mn.us/sites/default/files/2023-03/m1_inst_22.pdf

### mn_wfc

**Label**: Minnesota working family credit amount
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revisor.mn.gov/statutes/2021/cite/290.0671https://www.revisor.mn.gov/statutes/cite/290.0671

### mn_wfc_eligible

**Label**: Minnesota working family credit eligibilty status
**Entity**: tax_unit
**Period**: year

**References**:
- https://www.revisor.mn.gov/statutes/2021/cite/290.0671https://www.revisor.mn.gov/statutes/cite/290.0671

### mn_withheld_income_tax

**Label**: Minnesota withheld income tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

### mo_adjusted_gross_income

**Label**: Missouri adjusted gross income
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://dor.mo.gov/forms/MO-1040%20Fillable%20Calculating_2021.pdf
- https://revisor.mo.gov/main/OneSection.aspx?section=143.121

### mo_business_income_deduction

**Label**: Missouri business income deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://dor.mo.gov/forms/MO-1040%20Instructions_2023.pdf#page=16
- https://revisor.mo.gov/main/OneSection.aspx?section=143.022

### mo_federal_income_tax_deduction

**Label**: Missouri Federal income tax deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://dor.mo.gov/forms/MO-1040%20Instructions_2021.pdf#page=7
- https://revisor.mo.gov/main/OneSection.aspx?section=143.171&bid=49937&hl=federal+income+tax+deduction%u2044

### mo_income_tax

**Label**: Missouri income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://dor.mo.gov/forms/MO-1040%20Instructions_2021.pdf
- https://www.revisor.mo.gov/main/OneChapter.aspx?chapter=143
- https://revisor.mo.gov/main/OneSection.aspx?section=135.020&bid=6437
- https://revisor.mo.gov/main/OneSection.aspx?section=143.177&bid=49978&hl=

### mo_income_tax_before_credits

**Label**: Missouri income tax before credits
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://dor.mo.gov/forms/MO-1040%20Print%20Only_2021.pdf
- https://www.revisor.mo.gov/main/OneChapter.aspx?chapter=143

### mo_income_tax_before_refundable_credits

**Label**: Missouri income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://dor.mo.gov/forms/MO-1040%20Instructions_2021.pdf
- https://www.revisor.mo.gov/main/OneChapter.aspx?chapter=143
- https://revisor.mo.gov/main/OneSection.aspx?section=135.020&bid=6437
- https://revisor.mo.gov/main/OneSection.aspx?section=143.177&bid=49978&hl=

### mo_income_tax_exempt

**Label**: Missouri income tax exempt
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://revisor.mo.gov/main/OneSection.aspx?section=143.021

### mo_itemized_deductions

**Label**: Sum of itemized deductions applicable to Missouri taxable income calculation
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://dor.mo.gov/forms/MO-A_2021.pdf
- https://dor.mo.gov/forms/4711_2021.pdf#page=11
- https://revisor.mo.gov/main/OneSection.aspx?section=143.141&bid=7212

### mo_net_state_income_taxes

**Label**: Missouri net state income taxes
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://dor.mo.gov/forms/MO-A_2021.pdf#page=2
- https://revisor.mo.gov/main/OneSection.aspx?section=143.141&bid=7212

### mo_non_refundable_credits

**Label**: Missouri non-refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### mo_pension_and_ss_or_ssd_deduction

**Label**: Missouri Pension and Social Security or SS Disability Deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://dor.mo.gov/forms/MO-A_2021.pdf#page=3
- https://dor.mo.gov/forms/MO-1040%20Fillable%20Calculating_2021.pdf#page=2
- https://revisor.mo.gov/main/OneSection.aspx?section=143.124

### mo_pension_and_ss_or_ssd_deduction_section_a

**Label**: Missouri Pension and Social Security or SS Disability Deduction
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://dor.mo.gov/forms/MO-A_2021.pdf#page=3
- https://dor.mo.gov/forms/MO-1040%20Fillable%20Calculating_2021.pdf#page=2
- https://revisor.mo.gov/main/OneSection.aspx?section=143.124

### mo_pension_and_ss_or_ssd_deduction_section_b

**Label**: Missouri Pension and Social Security or SS Disability Deduction
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://dor.mo.gov/forms/MO-A_2021.pdf#page=3
- https://dor.mo.gov/forms/MO-1040%20Fillable%20Calculating_2021.pdf#page=2
- https://revisor.mo.gov/main/OneSection.aspx?section=143.124

### mo_pension_and_ss_or_ssd_deduction_section_c

**Label**: Missouri Pension and Social Security or SS Disability Deduction
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://dor.mo.gov/forms/MO-A_2021.pdf#page=3
- https://dor.mo.gov/forms/MO-1040%20Fillable%20Calculating_2021.pdf#page=2
- https://revisor.mo.gov/main/OneSection.aspx?section=143.124

### mo_property_tax_credit

**Label**: Missouri property tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://dor.mo.gov/forms/MO-PTS_2021.pdf
- https://revisor.mo.gov/main/OneSection.aspx?section=135.010&bid=6435
- https://revisor.mo.gov/main/OneSection.aspx?section=135.030&bid=6439

### mo_ptc_gross_income

**Label**: Missouri property tax credit gross income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://dor.mo.gov/forms/MO-PTS_2021.pdf
- https://dor.mo.gov/forms/4711_2021.pdf
- https://revisor.mo.gov/main/OneSection.aspx?section=135.010&bid=6435&hl=property+tax+credit%u2044

### mo_ptc_income_offset

**Label**: Missouri property tax credit gross income offset amount
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://dor.mo.gov/forms/MO-PTS_2021.pdf
- https://revisor.mo.gov/main/OneSection.aspx?section=135.025&bid=6438
- https://revisor.mo.gov/main/OneSection.aspx?section=135.030&bid=6439

### mo_ptc_net_income

**Label**: Missouri property tax credit net income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://dor.mo.gov/forms/MO-PTS_2021.pdf
- https://dor.mo.gov/forms/4711_2021.pdf
- https://revisor.mo.gov/main/OneSection.aspx?section=135.010&bid=6435&hl=property+tax+credit%u2044

### mo_ptc_taxunit_eligible

**Label**: Missouri property tax credit taxunit eligible
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://dor.mo.gov/forms/MO-PTS_2021.pdf
- https://revisor.mo.gov/main/OneSection.aspx?section=135.010&bid=6435

### mo_qualified_health_insurance_premiums

**Label**: Missouri qualified healh insurance premiums
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://dor.mo.gov/forms/5695.pdf
- https://www.irs.gov/pub/irs-pdf/f1040sa.pdf
- https://www.irs.gov/pub/irs-pdf/f1040.pdf

### mo_refundable_credits

**Label**: Missouri refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### mo_tanf_income_limit

**Label**: Missouri TANF income limit / maximum benefit
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### mo_taxable_income

**Label**: Missouri AGI minus deductions
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://dor.mo.gov/forms/MO-A_2021.pdfhttps://dor.mo.gov/forms/MO-1040%20Instructions_2021.pdf#page=8https://dor.mo.gov/forms/MO-1040%20Instructions_2022.pdf#page=8https://www.revisor.mo.gov/main/OneSection.aspx?section=143.111&bid=7201&hl=

### mo_wftc

**Label**: Missouri Working Families Tax Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://revisor.mo.gov/main/OneSection.aspx?section=143.177&bid=49978&hl=

### mo_withheld_income_tax

**Label**: Missouri withheld income tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

### monthly_age

**Label**: Monthly age
**Entity**: person
**Period**: month

### monthly_hours_worked

**Label**: Average monthly hours worked
**Entity**: person
**Period**: year
**Unit**: hour

### months_receiving_social_security_disability

**Label**: Number of months person has received social security disability
**Entity**: person
**Period**: year

### mortgage_interest

**Label**: Mortgage interest
**Entity**: person
**Period**: year
**Unit**: currency-USD

### mortgage_payments

**Label**: Mortgage payments
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### ms_aged_exemption

**Label**: Mississippi aged exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ms_agi

**Label**: Mississippi adjusted gross income
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf#page=14
- https://www.dor.ms.gov/sites/default/files/Forms/Individual/80105228.pdf

### ms_agi_adjustments

**Label**: Mississippi adjustments to federal adjusted gross income
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf#page=13
- https://www.dor.ms.gov/sites/default/files/Forms/Individual/80105228.pdf

### ms_blind_exemption

**Label**: Mississippi blind exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ms_cdcc

**Label**: Mississippi child and dependent care credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://legiscan.com/MS/text/HB1671/id/2767768

### ms_cdcc_eligible

**Label**: Eligible for the Mississippi child and dependent care credit
**Entity**: tax_unit
**Period**: year

**References**:
- https://legiscan.com/MS/text/HB1671/id/2767768

### ms_charitable_contributions_credit

**Label**: Mississippi charitable contributions credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100211_0.pdf#page=18
- https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100231.pdf#page=3

### ms_charitable_contributions_to_qualifying_foster_care_organizations

**Label**: Charitable contributions to qualifying foster care organizations in Mississippi
**Entity**: tax_unit
**Period**: year

**References**:
- https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100231.pdf#page=3

### ms_deductions_indiv

**Label**: Mississippi deductions when married couples file separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.dor.ms.gov/sites/default/files/Forms/Individual/80108228.pdf#page=1https://www.law.cornell.edu/regulations/mississippi/35-Miss-Code-R-SS-3-02-11-103

### ms_deductions_joint

**Label**: Mississippi deductions when married couples file jointly
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.dor.ms.gov/sites/default/files/Forms/Individual/80108228.pdf#page=1https://www.law.cornell.edu/regulations/mississippi/35-Miss-Code-R-SS-3-02-11-103

### ms_dependents_exemption

**Label**: Mississippi qualified and other dependent children exemption
**Entity**: tax_unit
**Period**: year

**References**:
- https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf#page=5

### ms_files_separately

**Label**: married couple files separately on Mississippi tax return
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ms_income_tax

**Label**: Mississippi income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ms_income_tax_before_credits_indiv

**Label**: Mississippi income tax before credits when married couples file separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

### ms_income_tax_before_credits_joint

**Label**: Mississippi income tax before credits when married couples file jointly
**Entity**: person
**Period**: year
**Unit**: currency-USD

### ms_income_tax_before_credits_unit

**Label**: Mississippi income tax before credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ms_itemized_deductions

**Label**: Mississippi itemized deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ms_itemized_deductions_indiv

**Label**: Mississippi itemized deductions for individual couples
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf#page=15https://www.dor.ms.gov/sites/default/files/Forms/Individual/80108228.pdf, # Line 7https://casetext.com/statute/mississippi-code-1972/title-27-taxation-and-finance/chapter-7-income-tax-and-withholding/article-1-income-tax/section-27-7-17-deductions-allowed?__cf_chl_rt_tk=8Kelu8kHpIXTp_FnAJLHvqa7rtrZYE1U.NAeBM8L.Nc-1692990420-0-gaNycGzNEmU

### ms_itemized_deductions_joint

**Label**: Mississippi itemized deductions for joint couples
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf#page=15https://www.dor.ms.gov/sites/default/files/Forms/Individual/80108228.pdf, # Line 7https://casetext.com/statute/mississippi-code-1972/title-27-taxation-and-finance/chapter-7-income-tax-and-withholding/article-1-income-tax/section-27-7-17-deductions-allowed?__cf_chl_rt_tk=8Kelu8kHpIXTp_FnAJLHvqa7rtrZYE1U.NAeBM8L.Nc-1692990420-0-gaNycGzNEmU

### ms_itemized_deductions_unit

**Label**: Mississippi itemized deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf#page=15https://www.dor.ms.gov/sites/default/files/Forms/Individual/80108228.pdf, # Line 7https://casetext.com/statute/mississippi-code-1972/title-27-taxation-and-finance/chapter-7-income-tax-and-withholding/article-1-income-tax/section-27-7-17-deductions-allowed?__cf_chl_rt_tk=8Kelu8kHpIXTp_FnAJLHvqa7rtrZYE1U.NAeBM8L.Nc-1692990420-0-gaNycGzNEmU

### ms_national_guard_or_reserve_pay_adjustment

**Label**: Mississippi national guard or reserve pay adjustment
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf#page=12
- https://law.justia.com/codes/mississippi/2020/title-27/chapter-7/article-1/section-27-7-18/

### ms_non_refundable_credits

**Label**: Mississippi non-refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ms_pre_deductions_taxable_income_indiv

**Label**: Mississippi pre deductions taxable income when married couple file separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf#page=13
- https://www.dor.ms.gov/sites/default/files/Forms/Individual/80105228.pdf

### ms_prorate_fraction

**Label**: Share of Mississippi AGI within tax unit
**Entity**: person
**Period**: year
**Unit**: currency-USD

### ms_real_estate_tax_deduction

**Label**: Mississippi real estate tax deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf#page=15

### ms_refundable_credits

**Label**: Mississippi refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ms_regular_exemption

**Label**: Mississippi regular exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ms_retirement_income_exemption

**Label**: Mississippi retirement income exemption
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/mississippi/title-27/chapter-7/article-1/section-27-7-15/
- https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf#page=11
- https://www.dor.ms.gov/sites/default/files/Forms/Individual/2024/80105248.pdf

### ms_self_employment_adjustment

**Label**: Mississippi self employment adjustment
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf#page=13
- https://law.justia.com/codes/mississippi/2020/title-27/chapter-7/article-1/section-27-7-18/

### ms_standard_deduction

**Label**: Mississippi standard deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ms_standard_deduction_indiv

**Label**: Mississippi standard deduction when married couples file separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

### ms_standard_deduction_joint

**Label**: Mississippi personal standard deduction for married couples filing jointly
**Entity**: person
**Period**: year
**Unit**: currency-USD

### ms_tax_unit_itemizes

**Label**: Whether the tax unit in Mississippi itemizes the deductions when married filing separately
**Entity**: tax_unit
**Period**: year

### ms_taxable_income

**Label**: Mississippi taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ms_taxable_income_indiv

**Label**: Mississippi taxable income when married couple file separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf#page=13
- https://www.dor.ms.gov/sites/default/files/Forms/Individual/80105228.pdf

### ms_taxable_income_joint

**Label**: Mississippi taxable income when married couple file jointly
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf#page=13
- https://www.dor.ms.gov/sites/default/files/Forms/Individual/80105228.pdf

### ms_total_exemptions

**Label**: Mississippi total exemptions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf#page=6

### ms_total_exemptions_indiv

**Label**: Mississippi total exemptions when married couples file separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf#page=6

### ms_total_exemptions_joint

**Label**: Mississippi total exemptions when married couples file jointly
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf#page=6

### ms_withheld_income_tax

**Label**: Mississippi withheld income tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

### mt_additions

**Label**: Montana additions to federal adjusted gross income
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://rules.mt.gov/gateway/Subchapterhome.asp?scn=42%2E15%2E2
- https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2023/05/Montana-Idividiual-Income-Tax-Return-Form-2-2022v6.2.pdf#page=4

### mt_aged_exemption_eligible_person

**Label**: Montana aged exemptions when married couples file separately
**Entity**: person
**Period**: year

**References**:
- https://regulations.justia.com/states/montana/department-42/chapter-42-15/subchapter-42-15-4/rule-42-15-402/

### mt_agi

**Label**: Montana Adjusted Gross Income for each individual
**Entity**: person
**Period**: year
**Unit**: currency-USD

### mt_applicable_ald_deductions

**Label**: Montana applicable above-the-line deductions 
**Entity**: person
**Period**: year
**Unit**: currency-USD

### mt_capital_gain_credit

**Label**: Montana capital gain credit
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://rules.mt.gov/gateway/RuleNo.asp?RN=42%2E4%2E502

### mt_capital_gains_tax_applicable_threshold_indiv

**Label**: Montana applicable threshold for the capital gains tax when married couples file separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2023/12/Form_2_2023_Instructions.pdf#page=6

### mt_capital_gains_tax_applicable_threshold_joint

**Label**: Montana applicable threshold for the capital gains tax when married couples file jointly
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2023/12/Form_2_2023_Instructions.pdf#page=6

### mt_capital_gains_tax_indiv

**Label**: Montana net long-term capital gains tax when married couples file separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2023/12/Form_2_2023_Instructions.pdf#page=6

### mt_capital_gains_tax_joint

**Label**: Montana net long-term capital gains tax when married couples file jointly
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2023/12/Form_2_2023_Instructions.pdf#page=6

### mt_child_dependent_care_expense_deduction

**Label**: Montana child dependent care expense deduction
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://casetext.com/statute/montana-code/title-15-taxation/chapter-30-individual-income-tax/part-21-rate-and-general-provisions/section-15-30-2131-repealed-effective-112024-temporary-deductions-allowed-in-computing-net-income

### mt_child_dependent_care_expense_deduction_eligible_child

**Label**: Eligible child for the Montana child dependent care expense deduction
**Entity**: person
**Period**: year

### mt_child_dependent_care_expense_deduction_eligible_children

**Label**: Eligible children for the Montana child dependent care expense deduction 
**Entity**: tax_unit
**Period**: year

**References**:
- https://casetext.com/statute/montana-code/title-15-taxation/chapter-30-individual-income-tax/part-21-rate-and-general-provisions/section-15-30-2131-repealed-effective-112024-temporary-deductions-allowed-in-computing-net-income

### mt_deductions_indiv

**Label**: The total amount of Montana deductions and exemptions when married filing separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

### mt_dependent_exemptions_person

**Label**: Montana dependent exemption for each dependent
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://regulations.justia.com/states/montana/department-42/chapter-42-15/subchapter-42-15-4/rule-42-15-403/

### mt_disability_income_exclusion

**Label**: Montana disability income exclusion
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://rules.mt.gov/gateway/RuleNo.asp?RN=42%2E15%2E217

### mt_disability_income_exclusion_eligible_person

**Label**: Montana disability income exclusion eligible person
**Entity**: person
**Period**: year

**References**:
- https://rules.mt.gov/gateway/RuleNo.asp?RN=42%2E15%2E217

### mt_disability_income_exclusion_person

**Label**: Montana disability income exclusion for each person
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2022/12/Form-2-2022-Instructions.pdf#page=31

### mt_eitc

**Label**: Montana EITC
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://leg.mt.gov/bills/mca/title_0150/chapter_0300/part_0230/section_0180/0150-0300-0230-0180.html

### mt_elderly_homeowner_or_renter_credit

**Label**: Montana Elderly Homeowner/Renter Credit
**Entity**: person
**Period**: year
**Unit**: currency-USD

### mt_elderly_homeowner_or_renter_credit_eligible

**Label**: Eligible for the Montana Elderly Homeowner/Renter Credit
**Entity**: person
**Period**: year

### mt_elderly_homeowner_or_renter_credit_gross_household_income

**Label**: Montana gross household income for the elderly homeowner/renter credit
**Entity**: person
**Period**: year
**Unit**: currency-USD

### mt_elderly_homeowner_or_renter_credit_net_household_income

**Label**: Net household income for Montana elderly homeowner or renter credit
**Entity**: person
**Period**: year
**Unit**: currency-USD

### mt_federal_income_tax_deduction_indiv

**Label**: Montana federal income tax deduction when married couples are filing separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/montana/2021/title-15/chapter-30/part-21/section-15-30-2131/

### mt_federal_income_tax_deduction_unit

**Label**: Montana federal income tax deduction for the entire tax unit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/montana/2021/title-15/chapter-30/part-21/section-15-30-2131/

### mt_files_separately

**Label**: married couple files separately on Montana tax return
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### mt_income_tax

**Label**: Montana income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### mt_income_tax_before_non_refundable_credits_indiv

**Label**: Montana income tax before refundable credits when married couples file separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

### mt_income_tax_before_non_refundable_credits_joint

**Label**: Montana income tax before refundable credits when married couples file jointly
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### mt_income_tax_before_refundable_credits_indiv

**Label**: Montana income tax before refundable credits when married couples are filing separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

### mt_income_tax_before_refundable_credits_joint

**Label**: Montana income tax before refundable credits when married couples are filing jointly
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### mt_income_tax_before_refundable_credits_unit

**Label**: Montana income tax before refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### mt_income_tax_indiv

**Label**: Montana income tax when married couples are filing separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

### mt_income_tax_joint

**Label**: Montana income tax when married couples are filing jointly
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### mt_income_tax_rebate

**Label**: Montana 2023 income tax rebate
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://archive.legmt.gov/bills/mca/title_0150/chapter_0300/part_0210/section_0910/0150-0300-0210-0910.html

### mt_interest_exemption

**Label**: Montana interest exemption for the tax unit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2022/12/Form-2-2022-Instructions.pdf#page=25

### mt_interest_exemption_eligible_person

**Label**: Eligible for the Montana interest exemption
**Entity**: person
**Period**: year

**References**:
- https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2022/12/Form-2-2022-Instructions.pdf#page=25

### mt_interest_exemption_person

**Label**: Montana interest exemption for each person
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2022/12/Form-2-2022-Instructions.pdf#page=25

### mt_itemized_deductions

**Label**: Montana itemized deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### mt_itemized_deductions_indiv

**Label**: Montana itemized deductions when married couples are filing separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2023/05/Montana-Idividiual-Income-Tax-Return-Form-2-2022v6.2.pdf#page=7https://law.justia.com/codes/montana/2022/title-15/chapter-30/part-21/section-15-30-2131/

### mt_itemized_deductions_joint

**Label**: Montana itemized deductions when married couples are filing jointly
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2023/05/Montana-Idividiual-Income-Tax-Return-Form-2-2022v6.2.pdf#page=7https://law.justia.com/codes/montana/2022/title-15/chapter-30/part-21/section-15-30-2131/

### mt_medical_expense_deduction_indiv

**Label**: Montana medical expense deduction when married couples are filing separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2023/05/Montana-Idividiual-Income-Tax-Return-Form-2-2022v6.2.pdf#page=7
- https://law.justia.com/codes/montana/2022/title-15/chapter-30/part-21/section-15-30-2131/

### mt_medical_expense_deduction_joint

**Label**: Montana medical expense deduction when married couples are filing jointly
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2023/05/Montana-Idividiual-Income-Tax-Return-Form-2-2022v6.2.pdf#page=7
- https://law.justia.com/codes/montana/2022/title-15/chapter-30/part-21/section-15-30-2131/

### mt_misc_deductions

**Label**: Montana miscellaneous deductions
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2023/05/Montana-Idividiual-Income-Tax-Return-Form-2-2022v6.2.pdf#page=7https://law.justia.com/codes/montana/2022/title-15/chapter-30/part-21/section-15-30-2131/

### mt_non_refundable_credits

**Label**: Montana refundable credits
**Entity**: person
**Period**: year
**Unit**: currency-USD

### mt_old_age_subtraction

**Label**: Montana old age subtraction
**Entity**: person
**Period**: year
**Unit**: currency-USD

### mt_personal_exemptions_indiv

**Label**: Montana exemptions when married couples file separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

### mt_personal_exemptions_joint

**Label**: Montana exemptions when married couple files jointly
**Entity**: person
**Period**: year
**Unit**: currency-USD

### mt_pre_dependent_exemption_taxable_income_indiv

**Label**: Montana taxable income before the dependent exemption when married couples are filing separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2023/05/Montana-Idividiual-Income-Tax-Return-Form-2-2022v6.2.pdf#page=1
- https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2022/12/Form-2-2022-Instructions.pdf#page=16

### mt_property_tax_rebate

**Label**: Montana property tax rebate
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2023/12/Form_2_2023_Instructions.pdf#page=5

### mt_refundable_credits

**Label**: Montana refundable credits
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2022/12/Form-2-2022-Instructions.pdf#page=48

### mt_refundable_credits_before_renter_credit

**Label**: Montana refundable credits before adding the elderly homeowner or renter credit
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2022/12/Form-2-2022-Instructions.pdf#page=48

### mt_regular_income_tax_indiv

**Label**: Montana income (subtracting capital gains before 2024) tax before refundable credits, when married couples file separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

### mt_regular_income_tax_joint

**Label**: Montana income (subtracting capital gains since 2024) tax before refundable credits, when married couples file separately
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### mt_salt_deduction

**Label**: Montana state and local tax deduction
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2023/05/Montana-Idividiual-Income-Tax-Return-Form-2-2022v6.2.pdf#page=7https://law.justia.com/codes/montana/2022/title-15/chapter-30/part-21/section-15-30-2131/

### mt_standard_deduction

**Label**: Montana standard deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### mt_standard_deduction_indiv

**Label**: Montana standard deduction when married couples are filing separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

### mt_standard_deduction_joint

**Label**: Montana standard deduction when married couples are filing jointly
**Entity**: person
**Period**: year
**Unit**: currency-USD

### mt_subtractions

**Label**: Montana subtractions from federal adjusted gross income
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/montana/2022/title-15/chapter-30/part-21/section-15-30-2110/
- https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2023/05/Montana-Idividiual-Income-Tax-Return-Form-2-2022v6.2.pdf#page=5

### mt_tax_unit_itemizes

**Label**: Whether the tax unit in Montana itemizes the deductions when married filing separately
**Entity**: tax_unit
**Period**: year

### mt_taxable_income

**Label**: Montana taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### mt_taxable_income_indiv

**Label**: Montana taxable income when married couples are filing separately
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2023/05/Montana-Idividiual-Income-Tax-Return-Form-2-2022v6.2.pdf#page=1
- https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2022/12/Form-2-2022-Instructions.pdf#page=16

### mt_taxable_income_joint

**Label**: Montana taxable income when married couples file jointly
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2023/05/Montana-Idividiual-Income-Tax-Return-Form-2-2022v6.2.pdf#page=1
- https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2022/12/Form-2-2022-Instructions.pdf#page=16

### mt_taxable_social_security

**Label**: Montana taxable social security benefits
**Entity**: person
**Period**: year

**References**:
- https://mtrevenue.gov/wp-content/uploads/mdocs/form%202%202021.pdf#page=6

### mt_tuition_subtraction

**Label**: Montana tuition subtraction
**Entity**: tax_unit
**Period**: year

**References**:
- https://leg.mt.gov/bills/mca/title_0150/chapter_0300/part_0210/section_0200/0150-0300-0210-0200.html

### mt_tuition_subtraction_person

**Label**: Montana tuition subtraction
**Entity**: person
**Period**: year

**References**:
- https://leg.mt.gov/bills/mca/title_0150/chapter_0300/part_0210/section_0200/0150-0300-0210-0200.html

### mt_withheld_income_tax

**Label**: Montana withheld income tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

### nc_additions

**Label**: North Carolina additions to the adjusted gross income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nc_child_deduction

**Label**: North Carolina child deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nc_ctc

**Label**: North Carolina credit for children
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ncdor.gov/taxes-forms/individual-income-tax/credit-children

### nc_deductions

**Label**: North Carolina deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ncdor.gov/taxes-forms/individual-income-tax/north-carolina-standard-deduction-or-north-carolina-itemized-deductions

### nc_demographic_tanf_eligible

**Label**: North Carolina Demographic eligibility for TANF
**Entity**: spm_unit
**Period**: year

Whether any person in a family applying for the Temporary Assistance for Needy Families program meets demographic requirements.

### nc_income_tax

**Label**: North Carolina income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nc_income_tax_before_credits

**Label**: North Carolina income tax before credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nc_itemized_deductions

**Label**: North Carolina itemized deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ncdor.gov/taxes-forms/individual-income-tax/north-carolina-standard-deduction-or-north-carolina-itemized-deductions 

### nc_military_retirement_deduction

**Label**: North Carolina military retirement deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ncdor.gov/2022-d-401-individual-income-tax-instructions/open#page=18
- https://law.justia.com/codes/north-carolina/chapter-105/article-4/section-105-153-5/

### nc_military_retirement_deduction_eligible

**Label**: North Carolina military retirement deduction eligible
**Entity**: person
**Period**: year

**References**:
- https://www.ncdor.gov/2022-d-401-individual-income-tax-instructions/open#page=18
- https://law.justia.com/codes/north-carolina/chapter-105/article-4/section-105-153-5/

### nc_non_refundable_credits

**Label**: North Carolina non-refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nc_scca

**Label**: North Carolina Subsidized Child Care Assistance Program
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

### nc_scca_age_group

**Label**: North Carolina SCCA age group
**Entity**: person
**Period**: year

**References**:
- https://ncchildcare.ncdhhs.gov/Portals/0/documents/pdf/M/Market_Rates_Centers_Eff_10-1.pdf?ver=9w52alSPhmrmo0N9gGVMEw%3d%3d

### nc_scca_child_age_eligible

**Label**: North Carolina child age eligibility for Subsidized Child Care Assistance (SCCA) program
**Entity**: person
**Period**: year

**References**:
- https://ncchildcare.ncdhhs.gov/Portals/0/documents/pdf/A/ACF-118_CCDF_FFY_2022-2024_For_North_Carolina_Amendment_1.pdf?ver=C9YfIUPAFekeBA3I1mN8aA%3d%3d#page=83

### nc_scca_countable_income

**Label**: North Carolina Subsidized Child Care Assistance program countable income
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://policies.ncdhhs.gov/wp-content/uploads/FINAL-Chapter-7-Family-definition-and-determining-income-eligibility-08-05-24.pdf#page=11

### nc_scca_entry_eligible

**Label**: North Carolina entry eligibility for Subsidized Child Care Assistance Program
**Entity**: spm_unit
**Period**: month

**References**:
- https://ncchildcare.ncdhhs.gov/Portals/0/documents/pdf/A/ACF-118_CCDF_FFY_2022-2024_For_North_Carolina_Amendment_1.pdf?ver=C9YfIUPAFekeBA3I1mN8aA%3d%3d#page=83

### nc_scca_entry_income_eligible

**Label**: North Carolina entry income eligibility for Subsidized Child Care Assistance program
**Entity**: spm_unit
**Period**: month

**References**:
- https://policies.ncdhhs.gov/wp-content/uploads/chapter-8-parental-fees-7.pdf#page=8

### nc_scca_fpg_rate

**Label**: North Carolina Subsidized Child Care Assistance (SCCA) program income limits compared to the FPL
**Entity**: spm_unit
**Period**: year

**References**:
- https://policies.ncdhhs.gov/wp-content/uploads/chapter-8-parental-fees-7.pdf#page=8

### nc_scca_has_eligible_child

**Label**: Any eligible child for North Carolina Subsidized Child Care Assistance program
**Entity**: spm_unit
**Period**: year

**References**:
- https://ncchildcare.ncdhhs.gov/Portals/0/documents/pdf/A/ACF-118_CCDF_FFY_2022-2024_For_North_Carolina_Amendment_1.pdf?ver=C9YfIUPAFekeBA3I1mN8aA%3d%3d#page=83

### nc_scca_is_school_age

**Label**: North Carolina SCCA school age determination
**Entity**: person
**Period**: year

**References**:
- https://ncchildcare.ncdhhs.gov/Portals/0/documents/pdf/A/ACF-118_CCDF_FFY_2022-2024_For_North_Carolina_Amendment_1.pdf?ver=C9YfIUPAFekeBA3I1mN8aA%3d%3d#page=83

### nc_scca_market_rate

**Label**: North Carolina Subsidized Child Care Assistance (SCCA) program market rate
**Entity**: person
**Period**: month

**References**:
- https://ncchildcare.ncdhhs.gov/Portals/0/documents/pdf/M/Market_Rates_Centers_Eff_10-1.pdf?ver=9w52alSPhmrmo0N9gGVMEw%3d%3dhttps://docs.google.com/spreadsheets/d/1y7p8qkiOrMAM42rtSwT_ZXeA5tzew4edNkrTXACxf4M/edit?gid=1339413807#gid=1339413807

### nc_scca_parent_fee

**Label**: North Carolina Subsidized Child Care Assistance Program parent fee
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

**References**:
- https://policies.ncdhhs.gov/wp-content/uploads/chapter-8-parental-fees-7.pdf#page=2

### nc_standard_deduction

**Label**: North Carolina standard deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nc_standard_or_itemized_deductions

**Label**: North Carolina standard or itemized deductions amount
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ncdor.gov/2021-d-401-individual-income-tax-instructions/open#page=14https://www.ncdor.gov/2022-d-401-individual-income-tax-instructions/open#page=14

### nc_tanf

**Label**: North Carolina TANF
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### nc_tanf_countable_earned_income

**Label**: North Carolina TANF countable earned income
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### nc_tanf_countable_gross_unearned_income

**Label**: North Carolina TANF countable gross unearned income
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### nc_tanf_eligible

**Label**: North Carolina TANF eligible
**Entity**: spm_unit
**Period**: year

### nc_tanf_income_eligible

**Label**: North Carolina TANF income eligible
**Entity**: spm_unit
**Period**: year

### nc_tanf_need_standard

**Label**: North Carolina TANF need standard
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### nc_tanf_reduced_need_standard

**Label**: North Carolina TANF reduced need standard
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### nc_taxable_income

**Label**: North Carolina taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nc_use_tax

**Label**: North Carolina use tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nc_withheld_income_tax

**Label**: North Carolina withheld income tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

### nd_additions

**Label**: North Dakota additions to federal taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2021-iit/form-nd-1-2021.pdf#page=1https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2021-iit/individual-income-tax-booklet-2021.pdf#page=14https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2022-iit/form-nd-1-2022.pdf#page=1https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2022-iit/2022-individual-income-tax-booklet.pdf#page=14

### nd_income_tax

**Label**: North Dakota income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2021-iit/form-nd-1-2021.pdfhttps://www.tax.nd.gov/sites/www/files/documents/forms/individual/2021-iit/individual-income-tax-booklet-2021.pdfhttps://www.tax.nd.gov/sites/www/files/documents/forms/individual/2022-iit/form-nd-1-2022.pdfhttps://www.tax.nd.gov/sites/www/files/documents/forms/individual/2022-iit/2022-individual-income-tax-booklet.pdf

### nd_income_tax_before_credits

**Label**: North Dakota income tax before credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://casetext.com/statute/north-dakota-century-code/title-57-taxation/chapter-57-38-income-tax/section-57-38-303-individual-estate-and-trust-income-tax

### nd_income_tax_before_refundable_credits

**Label**: North Dakota income tax before refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2021-iit/form-nd-1-2021.pdfhttps://www.tax.nd.gov/sites/www/files/documents/forms/individual/2021-iit/individual-income-tax-booklet-2021.pdfhttps://www.tax.nd.gov/sites/www/files/documents/forms/individual/2022-iit/form-nd-1-2022.pdfhttps://www.tax.nd.gov/sites/www/files/documents/forms/individual/2022-iit/2022-individual-income-tax-booklet.pdf

### nd_ltcg_subtraction

**Label**: North Dakota long-term capital gains subtraction from federal taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2021-iit/form-nd-1-2021.pdf#page=1https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2021-iit/individual-income-tax-booklet-2021.pdf#page=14https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2022-iit/form-nd-1-2022.pdf#page=1https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2022-iit/2022-individual-income-tax-booklet.pdf#page=14

### nd_mpc

**Label**: North Dakota marriage-penalty nonrefundable credit amount
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2021-iit/form-nd-1-2021.pdf#page=2https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2021-iit/2021-individual-income-tax-booklet.pdf#page=16https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2022-iit/form-nd-1-2022.pdf#page=2https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2022-iit/2022-individual-income-tax-booklet.pdf#page=16

### nd_nonrefundable_credits

**Label**: North Dakota nonrefundable income tax credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2021-iit/form-nd-1-2021.pdf#page=2https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2021-iit/individual-income-tax-booklet-2021.pdf#page=16https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2022-iit/form-nd-1-2022.pdf#page=2https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2022-iit/2022-individual-income-tax-booklet.pdf#page=16

### nd_qdiv_subtraction

**Label**: North Dakota qualified dividends subtraction from federal taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2021-iit/form-nd-1-2021.pdf#page=1https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2021-iit/individual-income-tax-booklet-2021.pdf#page=15https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2022-iit/form-nd-1-2022.pdf#page=1https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2022-iit/2022-individual-income-tax-booklet.pdf#page=15

### nd_refundable_credits

**Label**: North Dakota refundable income tax credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2021-iit/form-nd-1-2021.pdfhttps://www.tax.nd.gov/sites/www/files/documents/forms/individual/2021-iit/individual-income-tax-booklet-2021.pdfhttps://www.tax.nd.gov/sites/www/files/documents/forms/individual/2022-iit/form-nd-1-2022.pdfhttps://www.tax.nd.gov/sites/www/files/documents/forms/individual/2022-iit/2022-individual-income-tax-booklet.pdf

### nd_rtrc

**Label**: North Dakota resident-tax-relief nonrefundable credit amount
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2021-iit/form-nd-1-2021.pdf#page=2https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2021-iit/individual-income-tax-booklet-2021.pdf#page=14https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2022-iit/form-nd-1-2022.pdf#page=2https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2022-iit/2022-individual-income-tax-booklet.pdf#page=14

### nd_subtractions

**Label**: North Dakota subtractions from federal taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2021-iit/form-nd-1-2021.pdf#page=1https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2021-iit/individual-income-tax-booklet-2021.pdf#page=14https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2022-iit/form-nd-1-2022.pdf#page=1https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2022-iit/2022-individual-income-tax-booklet.pdf#page=14

### nd_taxable_income

**Label**: North Dakota taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2021-iit/form-nd-1-2021.pdf#page=1https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2021-iit/individual-income-tax-booklet-2021.pdf#page=14https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2022-iit/form-nd-1-2022.pdf#page=1https://www.tax.nd.gov/sites/www/files/documents/forms/individual/2022-iit/2022-individual-income-tax-booklet.pdf#page=14

### nd_withheld_income_tax

**Label**: North Dakota withheld income tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

### ne_additions

**Label**: Nebraska AGI additions to federal AGI
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://revenue.nebraska.gov/files/doc/tax-forms/2021/f_1040n_booklet.pdfhttps://revenue.nebraska.gov/files/doc/2022_Ne_Individual_Income_Tax_Booklet_8-307-2022_final_5.pdf

### ne_agi

**Label**: NE AGI
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://revenue.nebraska.gov/files/doc/tax-forms/2021/f_1040n_booklet.pdfhttps://revenue.nebraska.gov/files/doc/2022_Ne_Individual_Income_Tax_Booklet_8-307-2022_final_5.pdf

### ne_agi_subtractions

**Label**: Nebraska subtractions from federal adjusted gross income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://revenue.nebraska.gov/files/doc/tax-forms/2021/f_1040n_booklet.pdfhttps://revenue.nebraska.gov/files/doc/2022_Ne_Individual_Income_Tax_Booklet_8-307-2022_final_5.pdfhttps://revenue.nebraska.gov/about/2023-nebraska-legislative-changeshttps://www.nebraskalegislature.gov/FloorDocs/108/PDF/Slip/LB754.pdf#page=10

### ne_base_standard_deduction

**Label**: Nebraska standard deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://revenue.nebraska.gov/files/doc/tax-forms/2021/f_1040n_booklet.pdfhttps://revenue.nebraska.gov/files/doc/2022_Ne_Individual_Income_Tax_Booklet_8-307-2022_final_5.pdf

### ne_cdcc_nonrefundable

**Label**: Nebraska nonrefundable cdcc
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://revenue.nebraska.gov/files/doc/tax-forms/2021/f_1040n_booklet.pdfhttps://revenue.nebraska.gov/files/doc/2022_Ne_Individual_Income_Tax_Booklet_8-307-2022_final_5.pdf

### ne_cdcc_refundable

**Label**: Nebraska refundable cdcc
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://revenue.nebraska.gov/files/doc/tax-forms/2021/f_2441n.pdfhttps://revenue.nebraska.gov/sites/revenue.nebraska.gov/files/doc/Form_2441N_Ne_Child_and_Dependent_Care_Expenses_8-618-2022_final_2.pdf

### ne_cdcc_refundable_eligible

**Label**: Eligible for the Nebraska refundable CDCC
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://revenue.nebraska.gov/files/doc/tax-forms/2021/f_2441n.pdfhttps://revenue.nebraska.gov/sites/revenue.nebraska.gov/files/doc/Form_2441N_Ne_Child_and_Dependent_Care_Expenses_8-618-2022_final_2.pdf

### ne_child_care_subsidies

**Label**: Nebraska child care subsidies
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### ne_child_care_subsidy

**Label**: Nebraska Child Care Subsidy
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### ne_child_care_subsidy_eligible

**Label**: Eligible for the Nebraska Child Care Subsidy program
**Entity**: spm_unit
**Period**: year

**References**:
- https://nebraskalegislature.gov/laws/statutes.php?statute=68-1206
- https://dhhs.ne.gov/Pages/Child-Care-Subsidy-Information-for-Parents.aspx

### ne_child_care_subsidy_eligible_child

**Label**: Nebraska Child Care Subsidy program eligible child
**Entity**: person
**Period**: year

**References**:
- https://nebraskalegislature.gov/laws/statutes.php?statute=68-1206
- https://dhhs.ne.gov/Pages/Child-Care-Subsidy-Information-for-Parents.aspx

### ne_child_care_subsidy_eligible_parent

**Label**: Nebraska Child Care Subsidy program eligible parent
**Entity**: person
**Period**: year

Nebraska Child Care Subsidy eligible program parent must either be working, involved with Employment First as part of the ADC program, going to school or trainings, going to medical or therapy visits for self or child(ren), or ill or hurt (must be confirmed by a doctor)

**References**:
- https://dhhs.ne.gov/Pages/Child-Care-Subsidy-Information-for-Parents.aspx

### ne_child_care_subsidy_income_eligible

**Label**: Nebraska Child Care Subsidy program income eligible
**Entity**: spm_unit
**Period**: year

**References**:
- https://nebraskalegislature.gov/laws/statutes.php?statute=68-1206
- https://dhhs.ne.gov/Pages/Child-Care-Parents.aspx

### ne_dhhs_has_special_needs

**Label**: Has special needs under Nebraska Department of Health and Human Services
**Entity**: person
**Period**: year

A child has a requirement for extra care because of an acute or chronic physical or mental condition

**References**:
- https://dhhs.ne.gov/Documents/CC-Subsidy-Provider-Booklet.pdf#page=31
- https://dhhs.ne.gov/licensure/Documents/CCC391-3.pdf#page=11

### ne_eitc

**Label**: NE EITC amount
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://revenue.nebraska.gov/files/doc/tax-forms/2021/f_1040n_booklet.pdfhttps://revenue.nebraska.gov/files/doc/2022_Ne_Individual_Income_Tax_Booklet_8-307-2022_final_5.pdf

### ne_elderly_disabled_credit

**Label**: NE elderly/disabled tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://revenue.nebraska.gov/files/doc/tax-forms/2021/f_1040n_booklet.pdfhttps://revenue.nebraska.gov/files/doc/2022_Ne_Individual_Income_Tax_Booklet_8-307-2022_final_5.pdf

### ne_exemptions

**Label**: Nebraska exemptions amount
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://revenue.nebraska.gov/files/doc/tax-forms/2021/f_1040n_booklet.pdfhttps://revenue.nebraska.gov/files/doc/2022_Ne_Individual_Income_Tax_Booklet_8-307-2022_final_5.pdf

### ne_income_tax

**Label**: NE income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdfhttps://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf

### ne_income_tax_before_credits

**Label**: NE income tax before credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://revenue.nebraska.gov/files/doc/tax-forms/2021/f_1040n_booklet.pdfhttps://revenue.nebraska.gov/files/doc/2022_Ne_Individual_Income_Tax_Booklet_8-307-2022_final_5.pdf

### ne_income_tax_before_refundable_credits

**Label**: NE income tax before refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdfhttps://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf

### ne_itemized_deductions

**Label**: NE itemized deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://revenue.nebraska.gov/files/doc/tax-forms/2021/f_1040n_booklet.pdfhttps://revenue.nebraska.gov/files/doc/2022_Ne_Individual_Income_Tax_Booklet_8-307-2022_final_5.pdf

### ne_military_retirement_subtraction

**Label**: Nebraska military retirement subtraction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ne_nonrefundable_credits

**Label**: NE nonrefundable income tax credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://revenue.nebraska.gov/files/doc/tax-forms/2021/f_1040n_booklet.pdfhttps://revenue.nebraska.gov/files/doc/2022_Ne_Individual_Income_Tax_Booklet_8-307-2022_final_5.pdf

### ne_refundable_credits

**Label**: NE refundable income tax credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://revenue.nebraska.gov/files/doc/tax-forms/2021/f_1040n_booklet.pdfhttps://revenue.nebraska.gov/files/doc/2022_Ne_Individual_Income_Tax_Booklet_8-307-2022_final_5.pdf

### ne_refundable_ctc

**Label**: Nebraska refundable Child Tax Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://nebraskalegislature.gov/laws/statutes.php?statute=77-7203
- https://revenue.nebraska.gov/businesses/child-care-tax-credit-act

### ne_refundable_ctc_eligible_child

**Label**: Nebraska refundable Child Tax Credit eligible child
**Entity**: person
**Period**: year

**References**:
- https://nebraskalegislature.gov/laws/statutes.php?statute=77-7202https://revenue.nebraska.gov/businesses/child-care-tax-credit-act

### ne_refundable_ctc_income_eligible

**Label**: Nebraska refundable Child Tax Credit total household income eligible child
**Entity**: tax_unit
**Period**: year

**References**:
- https://nebraskalegislature.gov/laws/statutes.php?statute=77-7203
- https://revenue.nebraska.gov/businesses/child-care-tax-credit-act

### ne_refundable_ctc_total_household_income

**Label**: Nebraska refundable Child Tax Credit total household income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://nebraskalegislature.gov/laws/statutes.php?statute=77-7203
- https://revenue.nebraska.gov/businesses/child-care-tax-credit-act

### ne_school_readiness_credit

**Label**: Nebraska school readiness tax credit
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://revenue.nebraska.gov/sites/default/files/doc/tax-forms/2024/f_Individual_Income_Tax_Booklet.pdf#page=2

### ne_school_readiness_credit_child_care_worker_rating

**Label**: Level of child care worker for the Nebraska school readiness refundable tax credit
**Entity**: person
**Period**: year

**References**:
- https://revenue.nebraska.gov/sites/default/files/doc/tax-forms/2024/f_Individual_Income_Tax_Booklet.pdf#page=2

### ne_school_readiness_credit_eligible_worker

**Label**: Eligible worker for the Nebraska school readiness refundable tax credit
**Entity**: person
**Period**: year

**References**:
- https://revenue.nebraska.gov/sites/default/files/doc/tax-forms/2024/f_Individual_Income_Tax_Booklet.pdf#page=2

### ne_social_security_subtraction

**Label**: Nebraska social security subtraction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ne_standard_deduction

**Label**: NE standard deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://revenue.nebraska.gov/files/doc/tax-forms/2021/f_1040n_booklet.pdfhttps://revenue.nebraska.gov/files/doc/2022_Ne_Individual_Income_Tax_Booklet_8-307-2022_final_5.pdf

### ne_taxable_income

**Label**: NE taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://revenue.nebraska.gov/files/doc/tax-forms/2021/f_1040n_booklet.pdfhttps://revenue.nebraska.gov/files/doc/2022_Ne_Individual_Income_Tax_Booklet_8-307-2022_final_5.pdf

### ne_withheld_income_tax

**Label**: Nebraska withheld income tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

### net_capital_gain

**Label**: Net capital gain
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

The excess of net long-term capital gain over net short-term capitalloss, plus qualified dividends (the definition of "net capital gain"which applies to 26 U.S.C. § 1(h) from § 1(h)(11)).

**References**:
- {'title': '26 U.S. Code § 1222(11)', 'href': 'https://www.law.cornell.edu/uscode/text/26/1222#11'}

### net_capital_gains

**Label**: Net capital gains before loss limitation
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### net_investment_income

**Label**: net investment income (NII) that is base of the NII Tax (NIIT)
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/1411

### net_investment_income_tax

**Label**: Net Investment Income Tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/1411

### net_worth

**Label**: net worth
**Entity**: household
**Period**: year
**Unit**: currency-USD

### never_eligible_for_social_security_benefits

**Label**: Never eligible for Social Security
**Entity**: person
**Period**: year
**Unit**: currency-USD

### new_clean_vehicle_battery_capacity

**Label**: Battery capacity of a purchased new clean vehicle
**Entity**: tax_unit
**Period**: year
**Unit**: kWh

In kilowatt-hours (kWh)

### new_clean_vehicle_battery_components_made_in_north_america

**Label**: Percent of new clean vehicle's battery components made in North America
**Entity**: tax_unit
**Period**: year
**Unit**: /1

Percent of newly purchased new clean vehicle's battery components (by value) manufactured or assembled in North America

### new_clean_vehicle_battery_critical_minerals_extracted_in_trading_partner_country

**Label**: Percent of new clean vehicle's battery critical minerals extracted in a US trading partner country
**Entity**: tax_unit
**Period**: year
**Unit**: /1

Percent of newly purchased new clean vehicle's battery critical minearls (by value) extracted or processed in any country with which the US has a free trade agreement in effect, or recycled in North America

### new_clean_vehicle_classification

**Label**: New clean vehicle classification
**Entity**: tax_unit
**Period**: year

### new_clean_vehicle_credit

**Label**: New clean vehicle credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Nonrefundable credit for the purchase of a new clean vehicle

**References**:
- https://www.law.cornell.edu/uscode/text/26/30D
- https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=373

### new_clean_vehicle_credit_credit_limit

**Label**: New clean vehicle credit credit limit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Nonrefundable credit for the purchase of a new clean vehicle

**References**:
- https://www.law.cornell.edu/uscode/text/26/30D
- https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=373

### new_clean_vehicle_credit_eligible

**Label**: Eligible for new clean vehicle credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Eligible for nonrefundable credit for the purchase of a new clean vehicle

**References**:
- https://www.law.cornell.edu/uscode/text/26/30D

### new_clean_vehicle_credit_potential

**Label**: Potential value of the New clean vehicle credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Nonrefundable credit for the purchase of a new clean vehicle

**References**:
- https://www.law.cornell.edu/uscode/text/26/30D
- https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=373

### new_clean_vehicle_msrp

**Label**: New clean vehicle MSRP
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Manufacturer's suggested retail price of a newly purchased new clean vehicle

### nh_base_exemption

**Label**: New Hampshire base exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nh_blind_exemption

**Label**: New Hampshire blind exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nh_disabled_exemption

**Label**: New Hampshire disabled exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nh_education_tax_credit

**Label**: New Hampshire Education Tax Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.gencourt.state.nh.us/rsa/html/NHTOC/NHTOC-V-77-G.htm

### nh_income_tax

**Label**: New Hampshire income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nh_income_tax_before_refundable_credits

**Label**: New Hampshire income tax before refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nh_old_age_exemption

**Label**: New Hampshire old age exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nh_refundable_credits

**Label**: New Hampshire refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nh_taxable_income

**Label**: New Hampshire taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.gencourt.state.nh.us/rsa/html/V/77/77-4.htm
- https://www.revenue.nh.gov/forms/2023/documents/dp-10-2022-print.pdf

### nh_total_exemptions

**Label**: New Hampshire total exemption allowance
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nj_additions

**Label**: New Jersey additions to federal AGI by person
**Entity**: person
**Period**: year
**Unit**: currency-USD

Additions to federal AGI to get NJ total income.

**References**:
- https://law.justia.com/codes/new-jersey/2022/title-54/section-54-8a-36/

### nj_agi

**Label**: New Jersey adjusted gross income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/new-jersey/2022/title-54/section-54-8a-36/

### nj_agi_subtractions

**Label**: New Jersey subtractions from federal AGI by person
**Entity**: person
**Period**: year
**Unit**: currency-USD

Subtractions from federal AGI to get NJ total income.

**References**:
- https://law.justia.com/codes/new-jersey/2022/title-54/section-54-8a-36/

### nj_blind_or_disabled_exemption

**Label**: New Jersey blind or disabled exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nj_cdcc

**Label**: New Jersey CDCC
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

New Jersey Child and Dependent Care Credit

**References**:
- https://www.state.nj.us/treasury/taxation/pdf/current/1040i.pdf#page=44

### nj_childless_eitc_age_eligible

**Label**: New Jersey Eligible for EITC
**Entity**: tax_unit
**Period**: year

**References**:
- https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-4-7/

### nj_ctc

**Label**: New Jersey Child Tax Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-4-17-1/https://www.nj.gov/treasury/taxation/pdf/other_forms/tgi-ee/2021/1040i.pdf#page=44https://www.nj.gov/treasury/taxation/pdf/other_forms/tgi-ee/2022/1040i.pdf#page=44https://www.state.nj.us/treasury/taxation/pdf/current/1040i.pdf#page=46

### nj_ctc_eligible

**Label**: Eligible for the New Jersey child tax credit
**Entity**: tax_unit
**Period**: year

**References**:
- https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-4-17-1/https://www.nj.gov/treasury/taxation/pdf/other_forms/tgi-ee/2021/1040i.pdf#page=44https://www.nj.gov/treasury/taxation/pdf/other_forms/tgi-ee/2022/1040i.pdf#page=44https://www.state.nj.us/treasury/taxation/pdf/current/1040i.pdf#page=46

### nj_dependents_attending_college_exemption

**Label**: New Jersey dependents attending college exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nj_dependents_exemption

**Label**: New Jersey qualified and other dependent children exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://casetext.com/statute/new-jersey-statutes/title-54a-new-jersey-gross-income-tax-act/chapter-54a3-personal-exemptions-and-deductions/section-54a3-1-personal-exemptions-and-deductions

### nj_eitc

**Label**: New Jersey EITC
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-4-7/

### nj_eitc_income_eligible

**Label**: New Jersey Eligible for EITC
**Entity**: tax_unit
**Period**: year

**References**:
- https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-4-7/

### nj_eligible_pension_income

**Label**: New Jersey pension income eligible for pension exclusion
**Entity**: person
**Period**: year
**Unit**: currency-USD

New Jersey pension income eligible for pension exclusion

**References**:
- https://www.state.nj.us/treasury/taxation/pdf/current/1040i.pdf#page=21
- https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-6-10/

### nj_income_tax

**Label**: New Jersey income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nj_income_tax_before_refundable_credits

**Label**: New Jersey income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nj_main_income_tax

**Label**: New Jersey income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-2-1/

### nj_medical_expense_deduction

**Label**: New Jersey medical expense deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nj_non_refundable_credits

**Label**: New Jersey non-refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nj_other_retirement_income_exclusion

**Label**: New Jersey Other Retirement Income Exclusion
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

New Jersey other retirement income exclusion

**References**:
- https://www.state.nj.us/treasury/taxation/pdf/current/1040i.pdf#page=21
- https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-6-15/

### nj_other_retirement_special_exclusion

**Label**: New Jersey Other Retirement Special Exclusion
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

New Jersey other retirement special exclusion

**References**:
- https://www.state.nj.us/treasury/taxation/pdf/current/1040i.pdf#page=21
- https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-6-15/

### nj_pension_retirement_exclusion

**Label**: New Jersey Pension/Retirement Exclusion
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

New Jersey pension and retirement excludable amount if eligible (Line 28a)

**References**:
- https://www.state.nj.us/treasury/taxation/pdf/current/1040i.pdf#page=21
- https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-6-10/

### nj_potential_property_tax_deduction

**Label**: New Jersey potential property tax deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-3a-17/https://www.state.nj.us/treasury/taxation/pdf/other_forms/tgi-ee/2021/1040i.pdf#page=25

### nj_property_tax_credit

**Label**: New Jersey property tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.nj.gov/treasury/taxation/pdf/other_forms/tgi-ee/2021/1040i.pdf#page=49https://www.nj.gov/treasury/taxation/pdf/other_forms/tgi-ee/2022/1040i.pdf#page=50https://www.state.nj.us/treasury/taxation/pdf/current/1040i.pdf#page=52

### nj_property_tax_credit_eligible

**Label**: New Jersey property tax credit eligibility
**Entity**: tax_unit
**Period**: year

**References**:
- https://www.nj.gov/treasury/taxation/pdf/other_forms/tgi-ee/2021/1040i.pdf#page=26https://www.nj.gov/treasury/taxation/pdf/other_forms/tgi-ee/2022/1040i.pdf#page=26https://www.state.nj.us/treasury/taxation/pdf/current/1040i.pdf#page=27

### nj_property_tax_deduction

**Label**: New Jersey property tax deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-3a-17/

### nj_property_tax_deduction_eligible

**Label**: New Jersey property tax deduction eligibility
**Entity**: tax_unit
**Period**: year

### nj_refundable_credits

**Label**: New Jersey refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nj_regular_exemption

**Label**: New Jersey regular exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nj_retirement_exclusion_fraction

**Label**: New Jersey retirement exclusion fraction based on total income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.state.nj.us/treasury/taxation/pdf/current/1040i.pdf#page=21
- https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-6-10/

### nj_senior_exemption

**Label**: New Jersey senior exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nj_taking_property_tax_deduction

**Label**: Household taking New Jersey property tax deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-3a-17/

### nj_tanf_countable_gross_unearned_income

**Label**: New Jersey TANF countable gross unearned income
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### nj_tanf_countable_resources

**Label**: Countable resources for New Jersey TANF
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### nj_tanf_gross_earned_income

**Label**: New Jersey TANF gross earned income
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### nj_tanf_maximum_allowable_income

**Label**: New Jersey TANF maximum allowable income
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### nj_tanf_maximum_benefit

**Label**: New Jersey TANF maximum benefit
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### nj_tanf_resources_eligible

**Label**: New Jersey TANF resources eligible
**Entity**: spm_unit
**Period**: year

### nj_taxable_income

**Label**: New Jersey taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

NJ AGI less taxable income deductions (Line 42)

**References**:
- https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-3-1/

### nj_taxable_income_before_property_tax_deduction

**Label**: New Jersey taxable income before property tax deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

NJ AGI less taxable income deductions, before property tax deduction (Line 39)

**References**:
- https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-3-1/

### nj_total_deductions

**Label**: New Jersey total deductions to income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nj_total_exemptions

**Label**: New Jersey total exemption allowance
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nj_total_income

**Label**: New Jersey total income by person
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/new-jersey/2022/title-54/section-54-8a-36/

### nj_withheld_income_tax

**Label**: New Jersey withheld income tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

### nm_2021_income_rebate

**Label**: New Mexico 2021 income tax rebate
**Entity**: tax_unit
**Period**: year

**References**:
- https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503708/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgDsPABwBKADTJspQhACKiQrgCe0AOSapEQmFwJlqjdt37DIAMp5SAIQ0AlAKIAZZwDUAggDkAws5SpGAARtCk7BISQA

### nm_additional_2021_income_rebate

**Label**: New Mexico additional 2021 income tax rebate
**Entity**: tax_unit
**Period**: year

**References**:
- https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503710/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgDsHHgEoANMmylCEAIqJCuAJ7QA5BskRCYXAiUr1WnXoMgAynlIAhdQCUAogBknANQCCAOQDCTyVIwACNoUnZxcSA

### nm_additions

**Label**: New Mexico additions to federal AGI
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/2f1a6781-9534-4436-b427-1557f9592099/2022pit-adj-ins.pdf

### nm_aged_blind_exemption

**Label**: New Mexico aged and blind exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/856ebf4b-3814-49dd-8631-ebe579d6a42b/Personal%20Income%20Tax.pdf#page=34
- https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/1afc56af-ea90-4d48-82e5-1f9aeb43255a/PITbook2022.pdf#page=50
- https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503666/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgBsogJQAaZNlKEIARUSFcAT2gBydRIiEwuBIuVrN23fpABlPKQBCagEoBRADKOAagEEAcgGFHE0jAAI2hSdjExIA

### nm_armed_forces_retirement_pay_exemption_person

**Label**: New Mexico armed forces retirement pay exemption per person 
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://casetext.com/statute/new-mexico-statutes-1978/chapter-7-taxation/article-2-income-tax-general-provisions/section-7-2-513-effective-until-112025-exemption-armed-forces-retirement-pay

### nm_cdcc

**Label**: New Mexico dependent child day care credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503752/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgDsfAEwBKADTJspQhACKiQrgCe0AOSapEQmFwJlqjdt37DIAMp5SAIQ0AlAKIAZZwDUAggDkAws5SpGAARtCk7BISQA

### nm_cdcc_eligible

**Label**: Eligible household for the New Mexico dependent child day care credit
**Entity**: tax_unit
**Period**: year

**References**:
- https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503752/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgDsfAEwBKADTJspQhACKiQrgCe0AOSapEQmFwJlqjdt37DIAMp5SAIQ0AlAKIAZZwDUAggDkAws5SpGAARtCk7BISQA

### nm_cdcc_eligible_child

**Label**: Eligible child for the New Mexico dependent child day care credit
**Entity**: person
**Period**: year

**References**:
- https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503752/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgDsfAEwBKADTJspQhACKiQrgCe0AOSapEQmFwJlqjdt37DIAMp5SAIQ0AlAKIAZZwDUAggDkAws5SpGAARtCk7BISQA

### nm_cdcc_max_amount

**Label**: New Mexico maximum credit for dependent child day care credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503752/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgDsfAEwBKADTJspQhACKiQrgCe0AOSapEQmFwJlqjdt37DIAMp5SAIQ0AlAKIAZZwDUAggDkAws5SpGAARtCk7BISQA

### nm_ctc

**Label**: New Mexico child income tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503818/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgAcHYQEoANMmylCEAIqJCuAJ7QA5BskRCYXAiUr1WnXoMgAynlIAhdQCUAogBknANQCCAOQDCTyVIwACNoUnZxcSA

### nm_deduction_for_certain_dependents

**Label**: New Mexico deduction for certain dependents
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503892/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgAcATgBMASgA0ybKUIQAiokK4AntADkW6REJhcCFWs069BoyADKeUgCFNAJQCiAGRcA1AIIA5AMIu0qRgAEbQpOySkkA

### nm_deduction_for_certain_dependents_eligible

**Label**: Eligibility for New Mexico deduction for certain dependents
**Entity**: tax_unit
**Period**: year

**References**:
- https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503892/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgAcATgBMASgA0ybKUIQAiokK4AntADkW6REJhcCFWs069BoyADKeUgCFNAJQCiAGRcA1AIIA5AMIu0qRgAEbQpOySkkA

### nm_deductions

**Label**: New Mexico income deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nm_eitc

**Label**: New Mexico EITC
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/856ebf4b-3814-49dd-8631-ebe579d6a42b/Personal%20Income%20Tax.pdf

### nm_eitc_demographic_eligible

**Label**: Meets demographic eligibility for New Mexico EITC
**Entity**: tax_unit
**Period**: year

### nm_eitc_eligible

**Label**: Eligible for New Mexico EITC
**Entity**: tax_unit
**Period**: year

**References**:
- https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/856ebf4b-3814-49dd-8631-ebe579d6a42b/Personal%20Income%20Tax.pdf

### nm_exemptions

**Label**: New Mexico income exemptions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nm_hundred_year_exemption

**Label**: New Mexico hundred year exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503677/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgBsAdlEBKADTJspQhACKiQrgCe0AOSapEQmFwJlqjdt37DIAMp5SAIQ0AlAKIAZZwDUAggDkAws5SpGAARtCk7BISQA

### nm_income_tax

**Label**: New Mexico income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nm_income_tax_before_non_refundable_credits

**Label**: New Mexico income tax before non-refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nm_income_tax_before_refundable_credits

**Label**: New Mexico income tax before refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nm_low_and_middle_income_exemption

**Label**: New Mexico low- and middle-income exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nm_low_income_comprehensive_tax_rebate

**Label**: New Mexico low income comprehensive tax rebate
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/1afc56af-ea90-4d48-82e5-1f9aeb43255a/PITbook2022.pdf#page=58
- https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/1afc56af-ea90-4d48-82e5-1f9aeb43255a/PITbook2022.pdf#page=70
- https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/856ebf4b-3814-49dd-8631-ebe579d6a42b/Personal%20Income%20Tax.pdf#page=67
- https://casetext.com/statute/new-mexico-statutes-1978/chapter-7-taxation/article-2-income-tax-general-provisions/section-7-2-14-low-income-comprehensive-tax-rebate?sort=relevance&type=regulation&tab=keyword&jxs=&resultsNav=false

### nm_low_income_comprehensive_tax_rebate_exemptions

**Label**: New Mexico low income comprehensive tax rebate exemptions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://casetext.com/statute/new-mexico-statutes-1978/chapter-7-taxation/article-2-income-tax-general-provisions/section-7-2-14-low-income-comprehensive-tax-rebate?sort=relevance&type=regulation&tab=keyword&jxs=&resultsNav=false

### nm_medical_care_expense_deduction

**Label**: New Mexico medical care expense deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/856ebf4b-3814-49dd-8631-ebe579d6a42b/Personal%20Income%20Tax.pdf#page=249
- https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/1afc56af-ea90-4d48-82e5-1f9aeb43255a/PITbook2022.pdf#page=31
- https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503888/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgAcogJQAaZNlKEIARUSFcAT2gBydRIiEwuBIuVrN23fpABlPKQBCagEoBRADKOAagEEAcgGFHE0jAAI2hSdjExIA

### nm_medical_expense_credit

**Label**: New Mexico unreimbursed medical expense care credit
**Entity**: tax_unit
**Period**: year

**References**:
- https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503776/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgDswgGwBKADTJspQhACKiQrgCe0AOSapEQmFwJlqjdt37DIAMp5SAIQ0AlAKIAZZwDUAggDkAws5SpGAARtCk7BISQA

### nm_medical_expense_exemption

**Label**: New Mexico unreimbursed medical expense care exemption
**Entity**: tax_unit
**Period**: year

**References**:
- https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503680/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgBsADh4BKADTJspQhACKiQrgCe0AOSapEQmFwJlqjdt37DIAMp5SAIQ0AlAKIAZZwDUAggDkAws5SpGAARtCk7BISQA

### nm_modified_gross_income

**Label**: New Mexico modified gross income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503656/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgBsfYQEoANMmylCEAIqJCuAJ7QA5BskRCYXAiUr1WnXoMgAynlIAhdQCUAogBknANQCCAOQDCTyVIwACNoUnZxcSA

### nm_net_capital_gains_deduction

**Label**: New Mexico net capital gain deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503882/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgAcwgEwBKADTJspQhACKiQrgCe0AOSapEQmFwJlqjdt37DIAMp5SAIQ0AlAKIAZZwDUAggDkAws5SpGAARtCk7BISQA

### nm_non_refundable_credits

**Label**: New Mexico non-refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nm_other_deductions_and_exemptions

**Label**: New Mexico other income deductions and exemptions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nm_property_tax_rebate

**Label**: New Mexico property tax rebate
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503750/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgDsAgJQAaZNlKEIARUSFcAT2gBydRIiEwuBIuVrN23fpABlPKQBCagEoBRADKOAagEEAcgGFHE0jAAI2hSdjExIA

### nm_property_tax_rebate_eligible

**Label**: Eligible for the New Mexico property tax rebate
**Entity**: tax_unit
**Period**: year

**References**:
- https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/1afc56af-ea90-4d48-82e5-1f9aeb43255a/PITbook2022.pdf

### nm_refundable_credits

**Label**: New Mexico refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nm_salt_add_back

**Label**: New Mexico salt addback
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/1afc56af-ea90-4d48-82e5-1f9aeb43255a/PITbook2022.pdf#page=28
- https://law.justia.com/codes/new-mexico/chapter-7/article-2/section-7-2-2/
- https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/1afc56af-ea90-4d48-82e5-1f9aeb43255a/PITbook2022.pdf#page=28

### nm_social_security_income_exemption

**Label**: New Mexico social security income exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nm_supplemental_2021_income_rebate

**Label**: New Mexico supplemental 2021 income tax rebate
**Entity**: tax_unit
**Period**: year

**References**:
- https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503706/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgDsPAGwBKADTJspQhACKiQrgCe0AOSapEQmFwJlqjdt37DIAMp5SAIQ0AlAKIAZZwDUAggDkAws5SpGAARtCk7BISQA

### nm_taxable_income

**Label**: New Mexico taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nm_withheld_income_tax

**Label**: New Mexico withheld income tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

### non_deductible_mortgage_interest

**Label**: Non-deductible mortgage interest
**Entity**: person
**Period**: year
**Unit**: currency-USD

### non_mortgage_interest

**Label**: Non-mortgage interest
**Entity**: person
**Period**: year
**Unit**: currency-USD

### non_public_school_tuition

**Label**: Nonchartered, Nonpublic School Tuition
**Entity**: person
**Period**: year

### non_qualified_dividend_income

**Label**: non-qualified dividend income
**Entity**: person
**Period**: year
**Unit**: currency-USD

### non_refundable_american_opportunity_credit

**Label**: Non-refundable American Opportunity Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Value of the non-refundable portion of the American Opportunity Credit

**References**:
- https://www.law.cornell.edu/uscode/text/26/25A#i

### non_refundable_american_opportunity_credit_credit_limit

**Label**: Non-refundable American Opportunity Credit credit limit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Value of the non-refundable portion of the American Opportunity Credit

**References**:
- https://www.law.cornell.edu/uscode/text/26/25A#i

### non_refundable_american_opportunity_credit_potential

**Label**: Potential value of the Non-refundable American Opportunity Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Value of the non-refundable portion of the American Opportunity Credit

**References**:
- https://www.law.cornell.edu/uscode/text/26/25A#i

### non_refundable_ctc

**Label**: non-refundable CTC
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

The portion of the Child Tax Credit that is not refundable.

### non_sch_d_capital_gains

**Label**: Capital gains not reported on Schedule D
**Entity**: person
**Period**: year
**Unit**: currency-USD

### ny_additional_ctc

**Label**: New York additional Empire State Child Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.nysenate.gov/legislation/laws/TAX/606

### ny_additions

**Label**: New York AGI additions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Additions to NY AGI over federal AGI.

### ny_agi

**Label**: NY adjusted gross income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://casetext.com/regulation/new-york-codes-rules-and-regulations/title-20-department-of-taxation-and-finance/chapter-ii-income-taxes-and-estate-taxes/subchapter-a-new-york-state-personal-income-tax-under-article-22-of-the-tax-law/article-3-nonresidents/part-132-new-york-adjusted-gross-income-of-a-nonresident-individual/new-york-adjusted-gross-income-defined/section-1321-new-york-adjusted-gross-income-of-a-nonresident-individual

### ny_agi_subtractions

**Label**: New York AGI subtractions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Subtractions from NY AGI over federal AGI.

### ny_allowable_college_tuition_expenses

**Label**: New York allowable college tuition expenses for the credit and deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.nysenate.gov/legislation/laws/TAX/606

### ny_cdcc

**Label**: NY CDCC
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.nysenate.gov/legislation/laws/TAX/606

### ny_cdcc_max

**Label**: Maximum NY CDCC
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.nysenate.gov/legislation/laws/TAX/606

### ny_cdcc_rate

**Label**: NY CDCC rate
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.nysenate.gov/legislation/laws/TAX/606

### ny_college_tuition_credit

**Label**: NY college tuition credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.nysenate.gov/legislation/laws/TAX/606

### ny_college_tuition_credit_eligible

**Label**: New York college tuition credit eligible
**Entity**: tax_unit
**Period**: year

**References**:
- https://www.nysenate.gov/legislation/laws/TAX/606

### ny_college_tuition_deduction

**Label**: New York itemized deduction for college tuition expenses
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.nysenate.gov/legislation/laws/TAX/615
- https://www.nysenate.gov/legislation/laws/TAX/606

### ny_ctc

**Label**: NY CTC
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

New York's Empire State Child Credit

**References**:
- https://www.nysenate.gov/legislation/laws/TAX/606

### ny_ctc_post_2024

**Label**: New York CTC post-2024
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

New York's Empire State Child Credit under post-2024 rules (2025-2027)

**References**:
- https://www.nysenate.gov/legislation/laws/TAX/606

### ny_ctc_post_2024_base

**Label**: New York CTC post-2024 base amount
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Base New York CTC amount before phase-out under post-2024 rules

**References**:
- https://www.nysenate.gov/legislation/laws/TAX/606

### ny_ctc_post_2024_eligible

**Label**: New York CTC post-2024 eligibility
**Entity**: tax_unit
**Period**: year

Whether the tax unit is eligible for New York CTC under post-2024 rules

**References**:
- https://www.nysenate.gov/legislation/laws/TAX/606

### ny_ctc_post_2024_phase_out

**Label**: New York CTC post-2024 phase-out amount
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Amount by which New York CTC is reduced due to income phase-out under post-2024 rules

**References**:
- https://www.nysenate.gov/legislation/laws/TAX/606

### ny_ctc_pre_2024

**Label**: NY CTC pre-2024 rules
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

New York's Empire State Child Credit under pre-2024 rules (original system)

**References**:
- https://www.nysenate.gov/legislation/laws/TAX/606

### ny_ctc_pre_2024_eligible

**Label**: NY CTC pre-2024 eligibility
**Entity**: tax_unit
**Period**: year

Whether the tax unit is eligible for NY CTC under pre-2024 rules

**References**:
- https://www.nysenate.gov/legislation/laws/TAX/606

### ny_deductions

**Label**: NY income deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.nysenate.gov/legislation/laws/TAX/613

### ny_drive_clean_purchased_qualifying_vehicle

**Label**: Purchased a qualifying new vehicle at an authorized dealership for the New York Drive Clean rebate program
**Entity**: household
**Period**: year

**References**:
- https://www.nyserda.ny.gov/-/media/Project/Nyserda/Files/Programs/Drive-Clean-NY/implementation-manual.pdf#pages=6,7

### ny_drive_clean_rebate

**Label**: New York Drive Clean Rebate
**Entity**: household
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.nyserda.ny.gov/-/media/Project/Nyserda/Files/Programs/Drive-Clean-NY/implementation-manual.pdf#page=8

### ny_drive_clean_vehicle_cost

**Label**: Price of a qualifying vehicle purchased at an authorized New York dealership considered under the New York Drive Clean rebate program
**Entity**: household
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.nyserda.ny.gov/-/media/Project/Nyserda/Files/Programs/Drive-Clean-NY/implementation-manual.pdf#page=8

### ny_drive_clean_vehicle_electric_range

**Label**: New York Drive Clean rebate program all-electric vehicle range
**Entity**: household
**Period**: year
**Unit**: miles

**References**:
- https://www.nyserda.ny.gov/-/media/Project/Nyserda/Files/Programs/Drive-Clean-NY/implementation-manual.pdf#page=8

### ny_eitc

**Label**: New York EITC
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.nysenate.gov/legislation/laws/TAX/606

### ny_exemptions

**Label**: NY exemptions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.nysenate.gov/legislation/laws/TAX/616

### ny_geothermal_energy_system_credit

**Label**: New York geothermal energy system equipment credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

The tax credit for a qualified purchase or lease of geothermal energy system equipment, with a 5-year carryover.

**References**:
- https://www.nysenate.gov/legislation/laws/TAX/606

### ny_household_credit

**Label**: NY household credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.nysenate.gov/legislation/laws/TAX/606

### ny_income_tax

**Label**: NY income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ny_income_tax_before_credits

**Label**: NY income tax before credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ny_income_tax_before_refundable_credits

**Label**: NY income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ny_inflation_refund_credit

**Label**: New York 2025 inflation refund credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.nysenate.gov/legislation/laws/TAX/606#QQQ

### ny_itemized_deductions

**Label**: New York itemized deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.nysenate.gov/legislation/laws/TAX/615

### ny_itemized_deductions_higher_incremental_reduction

**Label**: New York itemized deductions higher incremental reduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.nysenate.gov/legislation/laws/TAX/615

### ny_itemized_deductions_incremental_reduction

**Label**: New York itemized deductions incremental reduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.nysenate.gov/legislation/laws/TAX/615

### ny_itemized_deductions_lower_incremental_reduction

**Label**: New York itemized deductions lower incremental reduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.nysenate.gov/legislation/laws/TAX/615

### ny_itemized_deductions_max

**Label**: NY uncapped itemized deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.nysenate.gov/legislation/laws/TAX/615

### ny_itemized_deductions_reduction

**Label**: NY itemized deductions reduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.nysenate.gov/legislation/laws/TAX/615

### ny_itemized_deductions_reduction_applies

**Label**: Whether the reduction to the New York itemized deductions applies
**Entity**: tax_unit
**Period**: year

**References**:
- https://www.nysenate.gov/legislation/laws/TAX/615

### ny_itemized_deductions_reduction_based_on_charitable_deduction

**Label**: New York itemized deductions reduction based on charitable deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.tax.ny.gov/pdf/2024/inc/it196i_2024.pdf#page=20

### ny_itemized_deductions_reduction_based_on_charitable_deduction_applies

**Label**: New York itemized deductions reduction based on charitable deduction
**Entity**: tax_unit
**Period**: year

**References**:
- https://www.nysenate.gov/legislation/laws/TAX/615

### ny_itemizes

**Label**: Itemizes New York deductions
**Entity**: tax_unit
**Period**: year

Tax units who itemize their federal deductions can opt to itemize their New York deductions. However, if a standard deduction causes a lower tax liability, they must choose that.

**References**:
- https://www.nysenate.gov/legislation/laws/TAX/613

### ny_main_income_tax

**Label**: NY main income tax (before credits and supplemental tax)
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ny_non_refundable_credits

**Label**: NY capped non-refundable tax credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ny_pension_exclusion

**Label**: New York pension exclusion
**Entity**: person
**Period**: year
**Unit**: currency-USD

Exclusion for pension income for eligible individuals.

### ny_qualified_geothermal_energy_system_expenditures

**Label**: Qualified geothermal energy system equipment expenditures
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Money spent in the current year for the purchase or lease of geothermal energy system equipment.

**References**:
- https://www.nysenate.gov/legislation/laws/TAX/606

### ny_qualified_solar_energy_systems_equipment_expenditures

**Label**: Qualified solar energy systems equipment expenditures in New York
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.nysenate.gov/legislation/laws/TAX/606

### ny_real_property_tax_credit

**Label**: NY real property tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.nysenate.gov/legislation/laws/TAX/606

### ny_refundable_credits

**Label**: NY refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ny_solar_energy_systems_equipment_credit

**Label**: New York solar energy systems equipment credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.nysenate.gov/legislation/laws/TAX/606

### ny_standard_deduction

**Label**: NY standard deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.nysenate.gov/legislation/laws/TAX/613

### ny_supplemental_eitc

**Label**: NY Supplemental EITC
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.nysenate.gov/legislation/laws/TAX/606

### ny_supplemental_tax

**Label**: NY supplemental income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ny_tanf

**Label**: New York TANF
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### ny_tanf_countable_earned_income

**Label**: New York TANF countable earned income
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### ny_tanf_countable_gross_unearned_income

**Label**: New York TANF countable gross unearned income
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### ny_tanf_countable_resources

**Label**: Countable resources for New York TANF
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### ny_tanf_eligible

**Label**: New York TANF eligible
**Entity**: spm_unit
**Period**: year

### ny_tanf_grant_standard

**Label**: New York TANF grant standard
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### ny_tanf_gross_earned_income

**Label**: New York TANF gross earned income
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### ny_tanf_income_eligible

**Label**: New York TANF income eligible
**Entity**: spm_unit
**Period**: year

### ny_tanf_need_standard

**Label**: New York TANF need standard
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### ny_tanf_resources_eligible

**Label**: New York TANF resources eligible
**Entity**: spm_unit
**Period**: year

### ny_taxable_income

**Label**: NY taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

NY AGI less taxable income deductions

**References**:
- https://www.nysenate.gov/legislation/laws/TAX/611

### ny_withheld_income_tax

**Label**: New York withheld income tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

### nyc_cdcc

**Label**: NYC Child and Dependent Care Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.tax.ny.gov/pdf/current_forms/it/it216i.pdf

### nyc_cdcc_age_restricted_expenses

**Label**: Childcare expenses for children under NYC CDCC age limit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nyc_cdcc_applicable_percentage

**Label**: NYC CDCC rate
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nyc_cdcc_eligible

**Label**: Eligible for NYC CDCC
**Entity**: tax_unit
**Period**: year

### nyc_cdcc_share_qualifying_childcare_expenses

**Label**: Share of Childcare expenses that qualify towards NYC CDCC
**Entity**: tax_unit
**Period**: year
**Unit**: /1

### nyc_eitc

**Label**: NYC EITC
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nyc_household_credit

**Label**: NYC Household Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nyc_income_tax

**Label**: NYC income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nyc_income_tax_before_credits

**Label**: NYC income tax before credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nyc_income_tax_before_refundable_credits

**Label**: NYC income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nyc_non_refundable_credits

**Label**: NYC non-refundable tax credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.tax.ny.gov/pit/credits/new_york_city_credits.htm#:~:text=New%20for%202022,adjusted%20gross%20income%20(NYAGI).

### nyc_refundable_credits

**Label**: NYC refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.tax.ny.gov/pit/credits/new_york_city_credits.htm#:~:text=New%20for%202022,adjusted%20gross%20income%20(NYAGI).

### nyc_school_credit_income

**Label**: NYC income used for school tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nyc_school_tax_credit

**Label**: NYC School Tax Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nyc_school_tax_credit_fixed_amount

**Label**: NYC School Tax Credit Fixed Amount
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nyc_school_tax_credit_fixed_amount_eligible

**Label**: Eligible for NYC School Tax Credit Fixed Amount
**Entity**: tax_unit
**Period**: year

### nyc_school_tax_credit_rate_reduction_amount

**Label**: NYC School Tax Credit Rate Reduction Amount
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### nyc_school_tax_credit_rate_reduction_amount_eligible

**Label**: Eligible for NYC School Tax Credit Rate Reduction Amount
**Entity**: tax_unit
**Period**: year

### nyc_taxable_income

**Label**: NYC taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.tax.ny.gov/pdf/2022/printable-pdfs/inc/it201i-2022.pdf#page=16

### nyc_unincorporated_business_credit

**Label**: NYC Unincorporated Business Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### offered_aca_disqualifying_esi

**Label**: Person is offered ACA disqualifying esi
**Entity**: person
**Period**: year

### oh_529_plan_deduction

**Label**: Ohio deduction for contributions to 529 plans
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=18

### oh_529_plan_deduction_person

**Label**: Ohio deduction for contributions to 529 plans
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=18

### oh_additions

**Label**: Ohio additions
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.ohio.gov/static/communications/publications/individual_income_tax_ohio.pdf#page=2https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-bundle.pdf#page=3https://cms7files1.revize.com/starkcountyoh/Document_center/Offices/Auditor/Services/Homestead%20Exemption/Ohio_Adj_Gross_Income.pdf#page=1

### oh_adoption_credit

**Label**: Ohio adoption credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-sd100-instruction-booklet.pdf#page=21
- https://tax.ohio.gov/wps/portal/gov/tax/help-center/faqs/income+-+individual+credits/income-individual-credits
- https://casetext.com/statute/ohio-revised-code/title-57-taxation/chapter-5747-income-tax/section-574737-repealed
- https://law.justia.com/codes/ohio/2022/title-57/chapter-5747/section-5747-37/

### oh_adoption_credit_person

**Label**: Ohio adoption credit for each person
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-sd100-instruction-booklet.pdf#page=21
- https://tax.ohio.gov/wps/portal/gov/tax/help-center/faqs/income+-+individual+credits/income-individual-credits
- https://casetext.com/statute/ohio-revised-code/title-57-taxation/chapter-5747-income-tax/section-574737-repealed
- https://law.justia.com/codes/ohio/2022/title-57/chapter-5747/section-5747-37/

### oh_agi

**Label**: Ohio adjusted gross income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://codes.ohio.gov/ohio-revised-code/section-5747.055
- https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=20

### oh_agi_person

**Label**: Ohio adjusted gross income
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://codes.ohio.gov/ohio-revised-code/section-5747.055
- https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=20

### oh_bonus_depreciation_add_back

**Label**: Ohio bonus depreciation add back
**Entity**: person
**Period**: year

### oh_cdcc

**Label**: Ohio child and dependent care credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=20

### oh_deductions

**Label**: Ohio deductions
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.ohio.gov/static/communications/publications/individual_income_tax_ohio.pdf#page=2https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-bundle.pdf#page=3https://cms7files1.revize.com/starkcountyoh/Document_center/Offices/Auditor/Services/Homestead%20Exemption/Ohio_Adj_Gross_Income.pdf

### oh_eitc

**Label**: Ohio Earned Income Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://codes.ohio.gov/ohio-revised-code/section-5747.71
- https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-sd100-instruction-booklet.pdf#page=21

### oh_exemption_credit

**Label**: Ohio Exemption Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/ohio/2022/title-57/chapter-5747/section-5747-022/

### oh_federal_conformity_deductions

**Label**: Ohio federal conformity deductions
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-bundle.pdf#page=4

### oh_has_taken_oh_lump_sum_credits

**Label**: Whether a person has taken Ohio lump sum credits
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=20
- https://codes.ohio.gov/ohio-revised-code/section-5747.055

### oh_income_tax

**Label**: Ohio income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### oh_income_tax_before_non_refundable_credits

**Label**: Ohio income tax before credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf

### oh_income_tax_before_refundable_credits

**Label**: Ohio income tax before refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### oh_income_tax_exempt

**Label**: Ohio income tax exempt
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf

### oh_insured_unreimbursed_medical_care_expense_amount

**Label**: Ohio insured unreimbursed medical and health care expense amount
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-sd100-instruction-booklet.pdf#page=18
- https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-sd100-instruction-booklet.pdf#page=27
- https://codes.ohio.gov/ohio-revised-code/section-5747.01

### oh_insured_unreimbursed_medical_care_expenses

**Label**: Ohio insured unreimbursed medical and health care expense deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-sd100-instruction-booklet.pdf#page=18
- https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-sd100-instruction-booklet.pdf#page=27
- https://codes.ohio.gov/ohio-revised-code/section-5747.01

### oh_insured_unreimbursed_medical_care_expenses_person

**Label**: Ohio insured unreimbursed medical and health care expense deduction for each person
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-sd100-instruction-booklet.pdf#page=18
- https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-sd100-instruction-booklet.pdf#page=27
- https://codes.ohio.gov/ohio-revised-code/section-5747.01

### oh_joint_filing_credit

**Label**: Ohio joint filing credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://codes.ohio.gov/ohio-revised-code/section-5747.05

### oh_joint_filing_credit_agi_subtractions

**Label**: Ohio qualifying income for the joint filing credit
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://codes.ohio.gov/ohio-revised-code/section-5747.055
- https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=20

### oh_joint_filing_credit_eligible

**Label**: Eligible for the Ohio joint filing credit
**Entity**: tax_unit
**Period**: year

**References**:
- https://codes.ohio.gov/ohio-revised-code/section-5747.05

### oh_joint_filing_credit_qualifying_income

**Label**: Ohio qualifying income for the joint filing credit
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://codes.ohio.gov/ohio-revised-code/section-5747.055
- https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=20

### oh_lump_sum_distribution_credit

**Label**: Ohio lump sum distribution credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=29

### oh_lump_sum_distribution_credit_eligible

**Label**: Eligible for the Ohio lump sum distribution credit
**Entity**: tax_unit
**Period**: year

**References**:
- https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=29

### oh_lump_sum_distribution_credit_eligible_person

**Label**: Eligible person for the Ohio lump sum distribution credit
**Entity**: person
**Period**: year

**References**:
- https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=29

### oh_lump_sum_distribution_credit_person

**Label**: Ohio lump sum distribution credit
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=29

### oh_lump_sum_retirement_credit

**Label**: Ohio Lump Sum Retirement Income Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://codes.ohio.gov/ohio-revised-code/section-5747.055

### oh_lump_sum_retirement_credit_eligible

**Label**: Eligible for the Ohio lump sum retirement income credit
**Entity**: tax_unit
**Period**: year

**References**:
- https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=20

### oh_modified_agi

**Label**: Ohio modified adjusted gross income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-sd100-instruction-booklet.pdf#page=31

### oh_non_public_school_credits

**Label**: Ohio Nonchartered, Nonpublic, School Tuition Credit AGI Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=21

### oh_non_refundable_credits

**Label**: Ohio non-refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/sch-cre.pdf
- https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/itschedule-credits.pdf

### oh_other_add_backs

**Label**: Ohio other add backs
**Entity**: person
**Period**: year

### oh_partial_non_refundable_credits

**Label**: Ohio non-refundable credits prior to the joint filing credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/sch-cre.pdf
- https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/itschedule-credits.pdf

### oh_pension_based_retirement_income_credit

**Label**: Ohio pension based retirement income credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://codes.ohio.gov/ohio-revised-code/section-5747.055

### oh_pension_based_retirement_income_credit_eligible

**Label**: Eligible for the Ohio pension based retirement income credit
**Entity**: tax_unit
**Period**: year

**References**:
- https://codes.ohio.gov/ohio-revised-code/section-5747.055

### oh_personal_exemptions

**Label**: Ohio personal exemptions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=14

### oh_personal_exemptions_eligible_person

**Label**: Eligible person for the Ohio Exemption Credit
**Entity**: person
**Period**: year

**References**:
- https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=14

### oh_refundable_credits

**Label**: Ohio refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/sch-cre.pdf
- https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/itschedule-credits.pdf

### oh_retirement_credit

**Label**: Ohio Retirement Income Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://codes.ohio.gov/ohio-revised-code/section-5747.055

### oh_section_179_expense_add_back

**Label**: Ohio Section 179 Expense Add Back
**Entity**: person
**Period**: year

### oh_senior_citizen_credit

**Label**: Ohio senior citizen credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=20
- https://codes.ohio.gov/ohio-revised-code/section-5747.055

### oh_tax_before_joint_filing_credit

**Label**: Ohio tax liability before the joint filing credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/sch-cre.pdf
- https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/itschedule-credits.pdf

### oh_taxable_income

**Label**: Ohio taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf

### oh_uniformed_services_retirement_income_deduction

**Label**: Ohio Uniformed services retirement income
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-bundle.pdf#page=4

### oh_uninsured_unreimbursed_medical_care_expenses

**Label**: Ohio unreimbursed medical and health care expense deduction for uninsured expenses
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-sd100-instruction-booklet.pdf#page=18
- https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-sd100-instruction-booklet.pdf#page=27
- https://codes.ohio.gov/ohio-revised-code/section-5747.01

### oh_unreimbursed_medical_care_expense_deduction

**Label**: Ohio unreimbursed medical and health care expense deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-sd100-instruction-booklet.pdf#page=18
- https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-sd100-instruction-booklet.pdf#page=27
- https://codes.ohio.gov/ohio-revised-code/section-5747.01

### oh_unreimbursed_medical_care_expense_deduction_person

**Label**: Ohio unreimbursed medical and health care expense deduction
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-sd100-instruction-booklet.pdf#page=18
- https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-sd100-instruction-booklet.pdf#page=27
- https://codes.ohio.gov/ohio-revised-code/section-5747.01

### oh_withheld_income_tax

**Label**: Ohio withheld income tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

### ok_additions

**Label**: Oklahoma AGI additions to federal AGI
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdfhttps://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf

### ok_adjustments

**Label**: Oklahoma adjustments
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdfhttps://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf

### ok_agi

**Label**: Oklahoma AGI
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdfhttps://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf

### ok_agi_subtractions

**Label**: Oklahoma AGI subtractions from federal AGI
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdf#page=16https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf#page=16

### ok_child_care_child_tax_credit

**Label**: Oklahoma Child Care/Child Tax Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdfhttps://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf

### ok_count_exemptions

**Label**: Count of Oklahoma exemptions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdfhttps://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf

### ok_eitc

**Label**: Oklahoma EITC
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdfhttps://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf

### ok_exemptions

**Label**: Oklahoma exemptions amount
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdfhttps://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf

### ok_federal_eitc

**Label**: Federal earned income credit for the Oklahoma EITC computation
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/oklahoma/title-68/section-68-2357-43/

### ok_federal_eitc_demographic_eligible

**Label**: Meets demographic eligibility for EITC for the Oklahoma EITC computation
**Entity**: tax_unit
**Period**: year

**References**:
- https://law.justia.com/codes/oklahoma/title-68/section-68-2357-43/

### ok_federal_eitc_eligible

**Label**: Eligible for federal EITC for the Oklahoma EITC computation
**Entity**: tax_unit
**Period**: year

**References**:
- https://law.justia.com/codes/oklahoma/title-68/section-68-2357-43/

### ok_federal_eitc_investment_income_eligible

**Label**: Meets investment income eligibility for EITC
**Entity**: tax_unit
**Period**: year

**References**:
- https://law.justia.com/codes/oklahoma/title-68/section-68-2357-43/

### ok_federal_eitc_maximum

**Label**: Maximum federal EITC for the Oklahoma EITC computation
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/oklahoma/title-68/section-68-2357-43/

### ok_federal_eitc_phase_in_rate

**Label**: Federal EITC phase-in rate for the Oklahoma EITC computation
**Entity**: tax_unit
**Period**: year
**Unit**: /1

Rate at which the EITC phases in with income.

**References**:
- https://law.justia.com/codes/oklahoma/title-68/section-68-2357-43/

### ok_federal_eitc_phase_out_rate

**Label**: Federal EITC phase-out rate for the Oklahoma EITC computation
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/oklahoma/title-68/section-68-2357-43/

### ok_federal_eitc_phase_out_start

**Label**: Federal EITC phase-out start for the Oklahoma EITC computation
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/oklahoma/title-68/section-68-2357-43/

### ok_federal_eitc_phased_in

**Label**: Federal EITC phase-in amount for the Oklahoma EITC computation
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

EITC maximum amount, taking into account earnings.

### ok_federal_eitc_reduction

**Label**: Federal EITC reduction for the Oklahoma EITC computation
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/oklahoma/title-68/section-68-2357-43/

### ok_gross_income

**Label**: Oklahoma gross income used in OK credit calculations
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdfhttps://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf

### ok_income_tax

**Label**: Oklahoma income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdfhttps://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf

### ok_income_tax_before_credits

**Label**: Oklahoma income tax before credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdfhttps://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf

### ok_income_tax_before_refundable_credits

**Label**: Oklahoma income tax before refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdfhttps://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf

### ok_itemized_deductions

**Label**: Oklahoma itemized deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdfhttps://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf

### ok_military_retirement_exclusion

**Label**: Oklahoma military retirement exclusion
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://casetext.com/regulation/oklahoma-administrative-code/title-710-oklahoma-tax-commission/chapter-50-income/subchapter-15-oklahoma-taxable-income/part-5-other-adjustments-to-income/section-71050-15-49-deduction-for-retirement-income

### ok_nonrefundable_credits

**Label**: Oklahoma nonrefundable income tax credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdfhttps://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf

### ok_pension_subtraction

**Label**: Oklahoma pension subtraction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdfhttps://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf

### ok_ptc

**Label**: Oklahoma property tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/538-H-2021.pdfhttps://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/538-H.pdf

### ok_refundable_credits

**Label**: Oklahoma refundable income tax credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdfhttps://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf

### ok_standard_deduction

**Label**: Oklahoma standard deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdfhttps://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf

### ok_stc

**Label**: Oklahoma sales tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdfhttps://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf

### ok_tanf

**Label**: Oklahoma TANF
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### ok_taxable_income

**Label**: Oklahoma taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdfhttps://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf

### ok_use_tax

**Label**: Oklahoma use tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdfhttps://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf

### ok_withheld_income_tax

**Label**: Oklahoma withheld income tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

### older_spouse_birth_year

**Label**: Birth year of head or spouse of tax unit depending on which is greater
**Entity**: tax_unit
**Period**: year
**Unit**: year

Birth year of taxpayer (i.e. primary adult) or spouse (i.e. secondary adult if present), depending on which is greater. 

### or_additions

**Label**: Oregon income additions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### or_agi

**Label**: Oregon adjusted gross income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### or_cdcc_relevant_expenses

**Label**: Oregon working family household and dependent care expenses
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://oregon.public.law/statutes/ors_315.264

### or_ctc

**Label**: Oregon Child Tax Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://olis.oregonlegislature.gov/liz/2023R1/Downloads/MeasureDocument/HB3235/Enrolled

### or_deductions

**Label**: OR deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.oregonlegislature.gov/bills_laws/ors/ors316.html
- https://www.oregon.gov/dor/forms/FormsPubs/form-or-40_101-040_2021.pdf#page=3

### or_disabled_child_dependent_exemptions

**Label**: OR disabled child dependent exemptions
**Entity**: tax_unit
**Period**: year

**References**:
- https://www.oregon.gov/dor/forms/FormsPubs/form-or-40-inst_101-040-1_2021.pdf#page=17https://www.oregonlegislature.gov/bills_laws/ors/ors316.html

### or_eitc

**Label**: OR EITC
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.oregon.gov/dor/forms/FormsPubs/form-or-40-inst_101-040-1_2021.pdf#page=18
- https://www.oregonlegislature.gov/bills_laws/ors/ors315.html

### or_exemption_credit

**Label**: OR exemption credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.oregon.gov/dor/forms/FormsPubs/form-or-40-inst_101-040-1_2021.pdf#page=17https://www.oregonlegislature.gov/bills_laws/ors/ors316.html

### or_federal_pension_subtraction

**Label**: Oregon Federal Pension Subtraction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.oregon.gov/dor/forms/FormsPubs/publication-or-17_101-431_2022.pdf#page=84

### or_federal_tax_liability_subtraction

**Label**: OR federal tax liability subtraction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.oregon.gov/dor/forms/FormsPubs/publication-or-17_101-431_2021.pdf#page=71
- https://www.oregonlegislature.gov/bills_laws/ors/ors316.html

### or_income_subtractions

**Label**: OR income subtractions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.oregon.gov/dor/forms/FormsPubs/form-or-40-inst_101-040-1_2021.pdf#page=13
- https://www.oregonlegislature.gov/bills_laws/ors/ors316.html

### or_income_tax

**Label**: OR income tax after refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### or_income_tax_before_credits

**Label**: OR income tax before credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.oregon.gov/dor/forms/FormsPubs/form-or-40-inst_101-040-1_2021.pdf#page=18
- https://www.oregonlegislature.gov/bills_laws/ors/ors316.html

### or_income_tax_before_refundable_credits

**Label**: OR income tax before refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### or_itemized_deductions

**Label**: OR itemized deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.oregonlegislature.gov/bills_laws/ors/ors316.html

### or_kicker

**Label**: OR Kicker
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.oregon.gov/dor/forms/FormsPubs/form-or-40-inst_101-040-1_2021.pdf#page=19
- https://www.oregonlegislature.gov/bills_laws/Pages/OrConst.aspx

### or_non_refundable_credits

**Label**: OR uncapped non-refundable tax credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### or_refundable_credits

**Label**: Oregon refundable tax credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### or_regular_exemptions

**Label**: OR regular exemptions
**Entity**: tax_unit
**Period**: year

**References**:
- https://www.oregon.gov/dor/forms/FormsPubs/form-or-40-inst_101-040-1_2021.pdf#page=17https://www.oregonlegislature.gov/bills_laws/ors/ors316.html

### or_retirement_credit

**Label**: Oregon Retirement Income Tax Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.oregon.gov/dor/forms/FormsPubs/publication-or-17_101-431_2021.pdf#page=108

### or_retirement_credit_eligible_person

**Label**: Eligible person for the Oregon Retirement Income Tax Credit
**Entity**: person
**Period**: year

**References**:
- https://secure.sos.state.or.us/oard/viewSingleRule.action?ruleVrsnRsn=238290#:~:text=Eligible%20individuals%20receiving%20retirement%20pay,by%20the%20household%20income%20limitation.

### or_retirement_credit_household_income

**Label**: Household income for the Oregon Retirement Income Tax Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://casetext.com/statute/oregon-revised-statutes/title-29-revenue-and-taxation/chapter-316-personal-income-tax/additional-credits/retirement-income/section-316157-credit-for-retirement-income

### or_severely_disabled_exemptions

**Label**: OR severely disabled exemptions for tax head or spouse
**Entity**: tax_unit
**Period**: year

**References**:
- https://www.oregon.gov/dor/forms/FormsPubs/form-or-40-inst_101-040-1_2021.pdf#page=17https://www.oregonlegislature.gov/bills_laws/ors/ors316.html

### or_standard_deduction

**Label**: OR standard deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Oregon standard deduction, including bonus for aged or blind and special rules for filers who are claimable as dependents.

**References**:
- https://www.oregon.gov/dor/forms/FormsPubs/form-or-40-inst_101-040-1_2021.pdf#page=18
- https://www.oregonlegislature.gov/bills_laws/ors/ors316.html

### or_tax_before_credits_in_prior_year

**Label**: OR tax before credits in prior year
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### or_taxable_income

**Label**: OR taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### or_wfhdc_eligibility_category

**Label**: Oregon working family household and dependent care credit percentage table column
**Entity**: tax_unit
**Period**: year

**References**:
- https://www.oregon.gov/dor/forms/FormsPubs/publication-or-wfhdc-tb_101-458_2021.pdf#page=1

### or_wfhdc_eligible

**Label**: Eligible for the Oregon working family household and dependent care credit
**Entity**: tax_unit
**Period**: year

Oregon Working Family Household and Dependent Care Credit household eligibility

**References**:
- https://www.oregon.gov/dor/forms/FormsPubs/schedule-or-wfhdc-inst_101-195-1_2022.pdf#pahe=1
- https://law.justia.com/codes/oregon/2021/volume-08/chapter-315/section-315-264/

### or_wfhdc_employment_eligible

**Label**: Employment eligible for the Oregon working family household and dependent care credit
**Entity**: tax_unit
**Period**: year

Oregon Working Family Household and Dependent Care Credit household eligibility

**References**:
- https://www.oregon.gov/dor/forms/FormsPubs/schedule-or-wfhdc-inst_101-195-1_2022.pdf#pahe=1
- https://law.justia.com/codes/oregon/2021/volume-08/chapter-315/section-315-264/

### or_wfhdc_has_qualified_individual_eligible

**Label**: Check if household has eligible individuals for Oregon Working Family Household and Dependent Care Credit
**Entity**: tax_unit
**Period**: year

Oregon Working Family Household and Dependent Care Credit household eligibility

**References**:
- https://www.oregon.gov/dor/forms/FormsPubs/schedule-or-wfhdc-inst_101-195-1_2022.pdf#pahe=1
- https://law.justia.com/codes/oregon/2021/volume-08/chapter-315/section-315-264/

### or_wfhdc_household_income

**Label**: Household income for the Oregon working family household and dependent care credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Larger of federal and state AGI

**References**:
- https://www.oregon.gov/dor/forms/FormsPubs/schedule-or-wfhdc-inst_101-195-1_2022.pdf#pahe=1
- https://law.justia.com/codes/oregon/2021/volume-08/chapter-315/section-315-264/

### or_wfhdc_household_size_eligible

**Label**: Household size eligible for the Oregon working family household and dependent care credit
**Entity**: tax_unit
**Period**: year

Oregon Working Family Household and Dependent Care Credit household eligibility

**References**:
- https://www.oregon.gov/dor/forms/FormsPubs/schedule-or-wfhdc-inst_101-195-1_2022.pdf#pahe=1
- https://law.justia.com/codes/oregon/2021/volume-08/chapter-315/section-315-264/

### or_wfhdc_income_category

**Label**: Oregon working family household and dependent care credit percentage table row letter
**Entity**: tax_unit
**Period**: year
**Unit**: /1

**References**:
- https://www.oregon.gov/dor/forms/FormsPubs/publication-or-wfhdc-tb_101-458_2021.pdf#page=1

### or_wfhdc_income_eligible

**Label**: Income eligible for the Oregon working family household and dependent care credit
**Entity**: tax_unit
**Period**: year

Oregon Working Family Household and Dependent Care Credit household eligibility

**References**:
- https://www.oregon.gov/dor/forms/FormsPubs/schedule-or-wfhdc-inst_101-195-1_2022.pdf#pahe=1
- https://law.justia.com/codes/oregon/2021/volume-08/chapter-315/section-315-264/

### or_withheld_income_tax

**Label**: Oregon withheld income tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

### or_working_family_household_and_dependent_care_credit

**Label**: Oregon working family household and dependent care credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.oregon.gov/dor/forms/FormsPubs/publication-or-wfhdc-tb_101-458_2022.pdf

### other_credits

**Label**: other credits
**Entity**: person
**Period**: year
**Unit**: currency-USD

### other_medical_expenses

**Label**: Other medical expenses
**Entity**: person
**Period**: year
**Unit**: currency-USD

### other_net_gain

**Label**: Other net gains
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Other net gain/loss from Form 4797

### outpatient_expense

**Label**: Outpatient expenses
**Entity**: person
**Period**: year
**Unit**: currency-USD

### over_the_counter_health_expenses

**Label**: Over the counter health expenses
**Entity**: person
**Period**: year
**Unit**: currency-USD

### overtime_income_deduction

**Label**: Overtime income deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### overtime_income_deduction_ssn_requirement_met

**Label**: SSN requirement met for the overtime income deduction
**Entity**: tax_unit
**Period**: year

### own_children_in_household

**Label**: Count of one's own children in the household
**Entity**: person
**Period**: year

### p08000

**Label**: p08000
**Entity**: person
**Period**: year

### pa_adjusted_taxable_income

**Label**: PA income tax after deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.pa.gov/FormsandPublications/FormsforIndividuals/PIT/Documents/2021/2021_pa-40in.pdf#page=21

### pa_cdcc

**Label**: Pennsylvania Child and Dependent Care Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.pa.gov/FormsandPublications/FormsforIndividuals/PIT/Documents/2022/2022_pa-40dc.pdf

### pa_eligibility_income

**Label**: PA eligibility income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.pa.gov/FormsandPublications/FormsforIndividuals/PIT/Documents/2021/2021_pa-40sp.pdf

### pa_income_tax

**Label**: Pennsylvania income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.pa.gov/FormsandPublications/FormsforIndividuals/PIT/Documents/2021/2021_pa-40in.pdf#page=21

### pa_income_tax_after_forgiveness

**Label**: PA income tax after forgiveness
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.pa.gov/FormsandPublications/FormsforIndividuals/PIT/Documents/2021/2021_pa-40in.pdf#page=21

### pa_income_tax_before_forgiveness

**Label**: PA income tax before forgiveness
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.pa.gov/FormsandPublications/FormsforIndividuals/PIT/Documents/2021/2021_pa-40in.pdf#page=21

### pa_nontaxable_pension_income

**Label**: Pension income taxable by US but not by PA
**Entity**: person
**Period**: year
**Unit**: currency-USD

US taxable pension income excluded from PA AGI.

**References**:
- https://www.revenue.pa.gov/FormsandPublications/FormsforIndividuals/PIT/Documents/2021/2021_pa-40in.pdf#page=8

### pa_refundable_tax_credits

**Label**: Pennsylvania refundable tax credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### pa_tanf_age_eligible

**Label**: Pennsylvania TANF age eligibility
**Entity**: spm_unit
**Period**: year

### pa_tanf_age_eligible_on_pregnant_women_limitation

**Label**: Pennsylvania TANF age eligibility on pregnant women requirement
**Entity**: spm_unit
**Period**: year

### pa_tanf_countable_resources

**Label**: Pennsylvania TANF countable resources
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### pa_tanf_resources_eligible

**Label**: Meets Pennsylvania TANF resource limit
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### pa_tax_deductions

**Label**: PA deductions against taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.pa.gov/FormsandPublications/FormsforIndividuals/PIT/Documents/2021/2021_pa-40in.pdf#page=20

### pa_tax_forgiveness_amount

**Label**: PA forgiveness amount
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.pa.gov/FormsandPublications/FormsforIndividuals/PIT/Documents/2021/2021_pa-40in.pdf#page=21

### pa_tax_forgiveness_rate

**Label**: PA tax forgiveness on eligibility income
**Entity**: tax_unit
**Period**: year
**Unit**: /1

**References**:
- https://www.revenue.pa.gov/FormsandPublications/FormsforIndividuals/PIT/Documents/2021/2021_pa-40in.pdf#page=39

### pa_total_taxable_income

**Label**: PA total taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.pa.gov/FormsandPublications/FormsforIndividuals/PIT/Documents/2021/2021_pa-40in.pdf#page=8

### pa_use_tax

**Label**: PA Use Tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.pa.gov/FormsandPublications/FormsforIndividuals/PIT/Documents/2021/2021_pa-40in.pdf#page=22

### pa_withheld_income_tax

**Label**: Pennsylvania withheld income tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

### partnership_s_corp_income

**Label**: partnership/S-corp income
**Entity**: person
**Period**: year
**Unit**: currency-USD

### partnership_s_corp_income_would_be_qualified

**Label**: Partnership and S-corp income would be qualified
**Entity**: person
**Period**: year

Whether income from partnerships and S corporations would be considered qualified business income.

**References**:
- https://www.law.cornell.edu/uscode/text/26/199A#c_3_A

### payroll_tax_gross_wages

**Label**: Gross wages and salaries for payroll taxes
**Entity**: person
**Period**: year
**Unit**: currency-USD

### pell_grant

**Label**: Pell Grant
**Entity**: person
**Period**: year
**Unit**: currency-USD

### pell_grant_calculation_method

**Label**: Pell Grant calculation method
**Entity**: tax_unit
**Period**: year

### pell_grant_contribution_from_assets

**Label**: Pell Grant head contribution from assets
**Entity**: person
**Period**: year
**Unit**: currency-USD

### pell_grant_countable_assets

**Label**: Pell Grant countable assets
**Entity**: person
**Period**: year
**Unit**: currency-USD

### pell_grant_dependent_allowances

**Label**: Pell Grant dependent allowances
**Entity**: person
**Period**: year
**Unit**: currency-USD

### pell_grant_dependent_available_income

**Label**: Pell Grant dependent available income
**Entity**: person
**Period**: year
**Unit**: currency-USD

### pell_grant_dependent_contribution

**Label**: Pell Grant dependent contribution
**Entity**: person
**Period**: year
**Unit**: currency-USD

### pell_grant_dependent_other_allowances

**Label**: Pell Grant dependent other allowances
**Entity**: person
**Period**: year
**Unit**: currency-USD

### pell_grant_dependents_in_college

**Label**: Pell Grant dependents in college
**Entity**: tax_unit
**Period**: year

### pell_grant_efc

**Label**: Pell Grant expected family contribution
**Entity**: person
**Period**: year
**Unit**: currency-USD

### pell_grant_eligibility_type

**Label**: Maximum, minimum, or ineligible for Pell Grant
**Entity**: person
**Period**: year

### pell_grant_formula

**Label**: Pell Grant formula
**Entity**: person
**Period**: year

### pell_grant_head_allowances

**Label**: Pell Grant head allowances
**Entity**: person
**Period**: year
**Unit**: currency-USD

### pell_grant_head_assets

**Label**: Pell Grant head assets
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### pell_grant_head_available_income

**Label**: Pell Grant head available income
**Entity**: person
**Period**: year
**Unit**: currency-USD

### pell_grant_head_contribution

**Label**: Pell Grant head contribution
**Entity**: person
**Period**: year
**Unit**: currency-USD

### pell_grant_household_type

**Label**: Pell Grant household type
**Entity**: person
**Period**: year

### pell_grant_max_fpg_percent_limit

**Label**: The maximum FPG percent to qualify for the maximum Pell Grant
**Entity**: person
**Period**: year
**Unit**: /1

### pell_grant_min_fpg_percent_limit

**Label**: The maximum FPG percent to qualify for the minimum Pell Grant
**Entity**: person
**Period**: year
**Unit**: /1

### pell_grant_months_in_school

**Label**: Pell Grant months of year student is in school
**Entity**: person
**Period**: year

### pell_grant_primary_income

**Label**: Pell Grant head income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### pell_grant_sai

**Label**: Pell Grant student aid index
**Entity**: person
**Period**: year
**Unit**: currency-USD

### pell_grant_simplified_formula_applies

**Label**: Use Pell Grant simplified formula
**Entity**: person
**Period**: year

### pell_grant_uses_efc

**Label**: Pell Grant uses the expected family contribution
**Entity**: person
**Period**: year

### pell_grant_uses_sai

**Label**: Pell Grant uses the student aid index
**Entity**: person
**Period**: year

### pension_income

**Label**: pension income
**Entity**: person
**Period**: year
**Unit**: currency-USD

Income from pensions, annuitities, life insurance or endowment contracts.

### pension_survivors

**Label**: Pension and annuity income from survivors benefits
**Entity**: person
**Period**: year
**Unit**: currency-USD

### per_capita_chip

**Label**: Average CHIP payment
**Entity**: person
**Period**: year
**Unit**: currency-USD

Per-capita CHIP payment for this person's State.

**References**:
- https://www.macpac.gov/publication/chip-spending-by-state/

### person_count

**Label**: People represented
**Entity**: person
**Period**: year

### person_family_id

**Label**: Unique reference for the family of this person
**Entity**: person
**Period**: year

### person_household_id

**Label**: Unique reference for the household of this person
**Entity**: person
**Period**: year

### person_id

**Label**: Unique reference for this person
**Entity**: person
**Period**: year

### person_in_poverty

**Label**: person in poverty
**Entity**: person
**Period**: year

Whether person is in poverty

### person_marital_unit_id

**Label**: Marital unit ID
**Entity**: person
**Period**: year

### person_spm_unit_id

**Label**: SPM unit ID
**Entity**: person
**Period**: year

### person_tax_unit_id

**Label**: Unique reference for the tax unit of this person
**Entity**: person
**Period**: year

### person_weight

**Label**: Person weight
**Entity**: person
**Period**: year

### personal_property

**Label**: Personal property value
**Entity**: person
**Period**: year
**Unit**: currency-USD

### pha_payment_standard

**Label**: HUD payment standard
**Entity**: household
**Period**: year
**Unit**: currency-USD

Payment standard for HUD programs

**References**:
- https://www.law.cornell.edu/cfr/text/24/982.503

### phone_cost

**Label**: Phone cost
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### phone_expense

**Label**: Phone expense
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### physician_services_expense

**Label**: Physician services expenses
**Entity**: person
**Period**: year
**Unit**: currency-USD

### positive_agi

**Label**: Positive AGI
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Negative AGI values capped at zero

### positive_gross_income

**Label**: Positive Gross Income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Negative gross income values capped at zero

### poverty_gap

**Label**: poverty gap
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

Difference between household income and poverty line.

### poverty_line

**Label**: poverty line
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

Income threshold below which a household is considered to be in poverty.

### pr_agi

**Label**: Puerto Rico adjusted gross income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/puerto-rico/title-thirteen/subtitle-17/part-ii/chapter-1005/subchapter-a/30103/

### pr_agi_person

**Label**: Puerto Rico adjusted gross income person level
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/puerto-rico/title-thirteen/subtitle-17/part-ii/chapter-1005/subchapter-a/30103/

### pr_casualty_loss_deduction

**Label**: Puerto Rico casualty loss deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/puerto-rico/title-thirteen/subtitle-17/part-ii/chapter-1005/subchapter-c/30135/

### pr_charitable_deduction

**Label**: Puerto Rico charitable deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/puerto-rico/title-thirteen/subtitle-17/part-ii/chapter-1005/subchapter-c/30135/

### pr_compensatory_low_income_credit

**Label**: Additional compensatory low income credit
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://casetext.com/statute/laws-of-puerto-rico/title-thirteen-taxation-and-finance/subtitle-17-internal-revenue-code-of-2011/part-ii-income-taxes/chapter-1007-credits-against-tax/subchapter-b-refundable-credits/30212-credit-for-low-income-individuals-older-than-sixty-five-65-years-of-age

### pr_earned_income_credit

**Label**: Puerto Rico earned income credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://hacienda.pr.gov/sites/default/files/schedule_ct_rev._jul_5_23_informative_-_instructions.pdf#page=2

### pr_earned_income_credit_eligible

**Label**: Puerto Rico earned income credit eligible unit
**Entity**: tax_unit
**Period**: year

**References**:
- https://hacienda.pr.gov/sites/default/files/schedule_ct_rev._jul_5_23_informative_-_instructions.pdf#page=1

### pr_earned_income_credit_eligible_person

**Label**: Puerto Rico earned income credit eligible person
**Entity**: person
**Period**: year

**References**:
- https://hacienda.pr.gov/sites/default/files/schedule_ct_rev._jul_5_23_informative_-_instructions.pdf#page=1

### pr_earned_income_credit_unearned_income

**Label**: Puerto Rico earned income credit unearned income
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://casetext.com/statute/laws-of-puerto-rico/title-thirteen-taxation-and-finance/subtitle-17-internal-revenue-code-of-2011/part-ii-income-taxes/chapter-1007-credits-against-tax/subchapter-b-refundable-credits/30211-earned-income-credit

### pr_education_deduction

**Label**: Puerto Rico education contribution deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/puerto-rico/title-thirteen/subtitle-17/part-ii/chapter-1005/subchapter-c/30135/

### pr_education_deduction_beneficiary_count

**Label**: Puerto Rico education contribution deduction beneficiary count
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/puerto-rico/title-thirteen/subtitle-17/part-ii/chapter-1005/subchapter-c/30135/

### pr_gross_income

**Label**: Puerto Rico gross income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/puerto-rico/title-thirteen/subtitle-17/part-ii/chapter-1005/subchapter-a/30101/

### pr_gross_income_person

**Label**: Puerto Rico gross income person
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/puerto-rico/title-thirteen/subtitle-17/part-ii/chapter-1005/subchapter-a/30101/

### pr_low_income_credit

**Label**: Puerto Rico low income credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://casetext.com/statute/laws-of-puerto-rico/title-thirteen-taxation-and-finance/subtitle-17-internal-revenue-code-of-2011/part-ii-income-taxes/chapter-1007-credits-against-tax/subchapter-b-refundable-credits/30212-credit-for-low-income-individuals-older-than-sixty-five-65-years-of-age

### pr_low_income_credit_eligible

**Label**: Eligible unit for the Puerto Rico low income credit
**Entity**: tax_unit
**Period**: year

**References**:
- https://casetext.com/statute/laws-of-puerto-rico/title-thirteen-taxation-and-finance/subtitle-17-internal-revenue-code-of-2011/part-ii-income-taxes/chapter-1007-credits-against-tax/subchapter-b-refundable-credits/30212-credit-for-low-income-individuals-older-than-sixty-five-65-years-of-age

### pr_low_income_credit_eligible_people

**Label**: Eligible people for the Puerto Rico low income credit
**Entity**: tax_unit
**Period**: year

**References**:
- https://casetext.com/statute/laws-of-puerto-rico/title-thirteen-taxation-and-finance/subtitle-17-internal-revenue-code-of-2011/part-ii-income-taxes/chapter-1007-credits-against-tax/subchapter-b-refundable-credits/30212-credit-for-low-income-individuals-older-than-sixty-five-65-years-of-age

### pr_low_income_credit_eligible_person

**Label**: Eligible person for the Puerto Rico low income credit
**Entity**: person
**Period**: year

**References**:
- https://casetext.com/statute/laws-of-puerto-rico/title-thirteen-taxation-and-finance/subtitle-17-internal-revenue-code-of-2011/part-ii-income-taxes/chapter-1007-credits-against-tax/subchapter-b-refundable-credits/30212-credit-for-low-income-individuals-older-than-sixty-five-65-years-of-age

### pr_medical_expense_deduction

**Label**: Puerto Rico medical expense deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/puerto-rico/title-thirteen/subtitle-17/part-ii/chapter-1005/subchapter-c/30135/

### pr_mortgage_deduction

**Label**: Puerto Rico home mortgage deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/puerto-rico/title-thirteen/subtitle-17/part-ii/chapter-1005/subchapter-c/30135/

### pr_refundable_credits

**Label**: Puerto Rico refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### pr_retirement_deduction

**Label**: Puerto Rico retirement contribution deduction
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/puerto-rico/title-thirteen/subtitle-17/part-ii/chapter-1005/subchapter-c/30135/

### pr_retirement_deduction_eligibility

**Label**: Puerto Rico retirement contribution deduction eligibility
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/puerto-rico/title-thirteen/subtitle-17/part-ii/chapter-1005/subchapter-c/30135/

### pre_subsidy_care_expenses

**Label**: Pre subsidy care expenses
**Entity**: person
**Period**: month
**Unit**: currency-USD

### pre_subsidy_childcare_expenses

**Label**: Pre subsidy child care expenses
**Entity**: person
**Period**: year
**Unit**: currency-USD

### pre_subsidy_electricity_expense

**Label**: Pre subsidy electricity expense
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### pre_subsidy_rent

**Label**: Pre subsidy rent
**Entity**: person
**Period**: year
**Unit**: currency-USD

### pre_tax_contributions

**Label**: Pre-tax contributions
**Entity**: person
**Period**: year
**Unit**: currency-USD

Payroll deductions.

### premium_tax_credit

**Label**: Affordable Care Act Premium Tax Credit
**Entity**: tax_unit
**Period**: month
**Unit**: currency-USD

### prescription_expense

**Label**: Prescription expenses
**Entity**: person
**Period**: year
**Unit**: currency-USD

### previous_year_income_available

**Label**: Prior-year income available
**Entity**: person
**Period**: year

Whether prior-year income was available in the survey.

### prior_energy_efficient_home_improvement_credits

**Label**: Prior year energy efficient home improvement credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Energy efficient home improvement credits claimed in prior years

**References**:
- https://www.law.cornell.edu/uscode/text/26/25C#b_1

### prior_energy_efficient_window_credits

**Label**: Prior years energy efficient window credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Energy efficient window credits claimed in prior years

**References**:
- https://www.law.cornell.edu/uscode/text/26/25C#b_2

### prior_year_minimum_tax_credit

**Label**: Prior year minimum tax credit
**Entity**: person
**Period**: year
**Unit**: currency-USD

Prior year minimum tax credit from Form 8801

**References**:
- https://www.law.cornell.edu/uscode/text/26/53

### private_pension_income

**Label**: private pension income
**Entity**: person
**Period**: year
**Unit**: currency-USD

Income from non-government employee pensions.

### property_sales_net_capital_gain

**Label**: Net capital gains from sale or exchange of property
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### public_pension_income

**Label**: public pension income
**Entity**: person
**Period**: year
**Unit**: currency-USD

Income from government employee pensions.

### puerto_rico_income

**Label**: Income from Puerto Rico
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Income generated in Puerto Rico by any individual who is a bona fide resident.

**References**:
- https://www.law.cornell.edu/uscode/text/26/933

### purchased_qualifying_new_clean_vehicle

**Label**: Purchased a qualifying new clean vehicle
**Entity**: tax_unit
**Period**: year

### purchased_qualifying_used_clean_vehicle

**Label**: Purchased a qualifying used clean vehicle
**Entity**: tax_unit
**Period**: year

### qbid_amount

**Label**: Per-cap qualified business income deduction amount for each person
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/199A#b_1https://www.irs.gov/pub/irs-prior/p535--2018.pdf

### qualified_adoption_assistance_expense

**Label**: Qualified adoption expense
**Entity**: person
**Period**: year
**Unit**: currency-USD

Qualified adoption expense (as defined in 26 U.S. Code § 23(d)) made pursuant to an adoption assistance program.

**References**:
- https://www.law.cornell.edu/uscode/text/26/23#d

### qualified_battery_storage_technology_expenditures

**Label**: Qualified battery storage technology expenditures
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Expenditures for qualified battery storage technology installed in connection with a dwelling unit located in the United States and used as a residence by the taxpayer and has the capacity not less than 3kwh.

**References**:
- https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=352

### qualified_bdc_income

**Label**: Business Development Company dividend income
**Entity**: person
**Period**: year
**Unit**: currency-USD

Business Development Company Dividend Income. Part of the QBID calculation.

**References**:
- https://www.law.cornell.edu/uscode/text/26/1#h_11

### qualified_business_income

**Label**: Qualified business income
**Entity**: person
**Period**: year
**Unit**: currency-USD

Business income that qualifies for the qualified business income deduction.

**References**:
- https://www.law.cornell.edu/uscode/text/26/199A#c

### qualified_business_income_deduction

**Label**: Qualified business income deduction for tax unit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/199A#b_1https://www.irs.gov/pub/irs-prior/p535--2018.pdf

### qualified_business_income_deduction_person

**Label**: Qualified business income deduction for each person
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/199A#b_1https://www.irs.gov/pub/irs-prior/p535--2018.pdf

### qualified_dividend_income

**Label**: qualified dividend income
**Entity**: person
**Period**: year
**Unit**: currency-USD

### qualified_furnace_or_hot_water_boiler_expenditures

**Label**: Expenditures on qualified natural gas, propane, or oil furnaces or hot water boilers
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Must achieve an annual fuel utilization efficiency rate of not less than 95.

**References**:
- https://www.law.cornell.edu/uscode/text/26/25C#d_4

### qualified_reit_and_ptp_income

**Label**: REIT and PTP Income
**Entity**: person
**Period**: year
**Unit**: currency-USD

REIT and Publically Traded Partnership Income. Part of the QBID calclulation.

**References**:
- https://www.law.cornell.edu/uscode/text/26/1#h_11

### qualified_retirement_penalty

**Label**: Penalty tax on qualified retirement plans
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### qualified_tuition_expenses

**Label**: Qualified tuition expenses
**Entity**: person
**Period**: year
**Unit**: currency-USD

### qualifies_for_elderly_or_disabled_credit

**Label**: Qualifies for elderly or disabled credit
**Entity**: person
**Period**: year

Whether this tax unit qualifies for the elderly or disabled credit

### race

**Label**: race
**Entity**: person
**Period**: year

The broadest racial category (White only, Black only, Hispanic, Other)

### railroad_benefits

**Label**: Recieves any railroad benefits
**Entity**: person
**Period**: year

### real_estate_taxes

**Label**: Real estate taxes
**Entity**: person
**Period**: year
**Unit**: currency-USD

### recapture_of_investment_credit

**Label**: Recapture of Investment Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### receives_housing_assistance

**Label**: Currently receives housing assistance
**Entity**: spm_unit
**Period**: year

Currently receives housing assistance

### receives_or_needs_protective_services

**Label**: Child receiving or needs protective services
**Entity**: person
**Period**: year

### receives_wic

**Label**: Reported to receive WIC
**Entity**: person
**Period**: month

### recovery_rebate_credit

**Label**: Recovery Rebate Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/6428

### reduced_price_school_meals

**Label**: reduced price school meals
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

Value of reduced price school meals.

### refundable_american_opportunity_credit

**Label**: Refundable American Opportunity Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Value of the refundable portion of the American Opportunity Credit

**References**:
- https://www.law.cornell.edu/uscode/text/26/25A#i

### refundable_ctc

**Label**: refundable CTC
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

The portion of the Child Tax Credit that is refundable.

**References**:
- https://www.law.cornell.edu/uscode/text/26/24#d

### refundable_payroll_tax_credit

**Label**: Refundable Payroll Tax Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### regular_tax_before_credits

**Label**: Regular tax before credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Regular tax on regular taxable income before credits

### relative_capital_gains_mtr_change

**Label**: relative change in capital gains tax rate
**Entity**: person
**Period**: year
**Unit**: /1

### relative_income_change

**Label**: relative income change
**Entity**: person
**Period**: year
**Unit**: /1

### relative_wage_change

**Label**: relative wage change
**Entity**: person
**Period**: year
**Unit**: /1

### rent

**Label**: Rent
**Entity**: person
**Period**: year
**Unit**: currency-USD

### rent_is_shared_with_another_tax_unit

**Label**: Whether the household shares rent with others
**Entity**: tax_unit
**Period**: year

### rental_income

**Label**: rental income
**Entity**: person
**Period**: year
**Unit**: currency-USD

Income from rental of property

### rental_income_would_be_qualified

**Label**: Rental income would be qualified
**Entity**: person
**Period**: year

Whether rental income would be considered qualified business income.

**References**:
- https://www.law.cornell.edu/uscode/text/26/199A#c_3_A

### rents

**Label**: Tax unit pays rent
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### reported_salt

**Label**: Reported State and local sales or income tax and real estate taxes subject to the SALT deduction limited to taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### residential_clean_energy_credit

**Label**: Residential clean energy credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Residential clean energy tax credit

**References**:
- https://www.law.cornell.edu/uscode/text/26/25D

### residential_clean_energy_credit_credit_limit

**Label**: Residential clean energy credit credit limit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Residential clean energy tax credit

**References**:
- https://www.law.cornell.edu/uscode/text/26/25D

### residential_clean_energy_credit_potential

**Label**: Potential value of the Residential clean energy credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Residential clean energy tax credit

**References**:
- https://www.law.cornell.edu/uscode/text/26/25D

### residential_efficiency_electrification_rebate

**Label**: Residential efficiency and electrification rebate
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### residential_efficiency_electrification_retrofit_energy_savings

**Label**: Modeled energy system savings from a residential efficiency and electrification retrofit
**Entity**: tax_unit
**Period**: year
**Unit**: kWh/month

In kilowatt hours per month. Do not include savings from projects listed in other electrification and efficiency expenditure categories.

**References**:
- https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=587

### residential_efficiency_electrification_retrofit_expenditures

**Label**: Expenditures on efficiency and electrification retrofits 
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=587

### retired_from_federal_government

**Label**: Retired from Federal Government
**Entity**: person
**Period**: year

### retired_from_ky_government

**Label**: Retired from state or local government in Kentucky
**Entity**: person
**Period**: year

### retired_on_total_disability

**Label**: Retired on total disability
**Entity**: person
**Period**: year

Whether this individual has retired on disability, and was permanently and totally disabled when they retired

### retirement_benefits_from_ss_exempt_employment

**Label**: Retirement benefits amount from SS exempt employment
**Entity**: person
**Period**: year
**Unit**: currency-USD

Amount of a recipient receive retirement benefits from SS exempt employment

**References**:
- https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=18

### retirement_distributions

**Label**: Retirement account distributions
**Entity**: person
**Period**: year
**Unit**: currency-USD

### ri_additions

**Label**: Rhode Island AGI Additions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.ri.gov/sites/g/files/xkgbur541/files/2022-12/2022%201041%20Schedule%20M_w.pdf#page=2

### ri_agi

**Label**: Rhode Island AGI
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.ri.gov/sites/g/files/xkgbur541/files/2022-12/2022%201041%20Schedule%20M_w.pdf

### ri_cdcc

**Label**: Rhode Island child and dependent care credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ri_child_tax_rebate

**Label**: Rhode Island Child Tax Rebate
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.ri.gov/sites/g/files/xkgbur541/files/2022-08/H7123Aaa_CTR_0.pdf

### ri_child_tax_rebate_eligible

**Label**: Rhode Island Child Tax Rebate
**Entity**: tax_unit
**Period**: year

**References**:
- https://tax.ri.gov/sites/g/files/xkgbur541/files/2022-08/H7123Aaa_CTR_0.pdf

### ri_eitc

**Label**: Rhode Island earned income tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ri_exemptions

**Label**: Rhode Island exemptions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.ri.gov/sites/g/files/xkgbur541/files/2022-12/2022%20Tax%20Rate%20and%20Worksheets.pdf

### ri_income_tax

**Label**: Rhode Island income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ri_income_tax_before_non_refundable_credits

**Label**: Rhode Island income tax before refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ri_income_tax_before_refundable_credits

**Label**: Rhode Island income tax before refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ri_non_refundable_credits

**Label**: Rhode Island non-refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ri_property_tax_credit

**Label**: Rhode Island property tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- http://webserver.rilin.state.ri.us/Statutes/TITLE44/44-33/44-33-9.htm

### ri_property_tax_credit_eligible

**Label**: Rhode Island property tax credit eligibility status
**Entity**: tax_unit
**Period**: year

**References**:
- http://webserver.rilin.state.ri.us/Statutes/TITLE44/44-33/44-33-3.htm
- https://tax.ri.gov/sites/g/files/xkgbur541/files/2022-01/2021-ri-1040h_w.pdf#page=1

### ri_property_tax_household_income

**Label**: Rhode Island total household income for the property tax credit computation
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.ri.gov/sites/g/files/xkgbur541/files/2022-12/2022%20RI-1040H_v2_w.pdf#page=2

### ri_refundable_credits

**Label**: Rhode Island refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ri_retirement_income_subtraction

**Label**: Rhode Island retirement income subtraction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- http://webserver.rilin.state.ri.us/Statutes/title44/44-30/44-30-12.HTM

### ri_retirement_income_subtraction_eligible

**Label**: Eligible for the Rhode Island retirement income subtraction
**Entity**: tax_unit
**Period**: year

**References**:
- http://webserver.rilin.state.ri.us/Statutes/title44/44-30/44-30-12.HTM

### ri_social_security_modification

**Label**: Rhode Island Social Security Modification
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.ri.gov/sites/g/files/xkgbur541/files/2022-12/Social%20Security%20Worksheet_w.pdf

### ri_social_security_modification_eligible

**Label**: Eligible for the Rhode Island Social Security Modification
**Entity**: tax_unit
**Period**: year

**References**:
- https://tax.ri.gov/sites/g/files/xkgbur541/files/2022-12/Social%20Security%20Worksheet_w.pdf

### ri_standard_deduction

**Label**: Rhode Island standard deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

https://tax.ri.gov/sites/g/files/xkgbur541/files/2022-12/ADV_2022_40_Inflation_Adjustments.pdf

### ri_standard_deduction_applicable_percentage

**Label**: Rhode Island standard deduction applicable percentage
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.ri.gov/sites/g/files/xkgbur541/files/2021-11/2021-tax-rate-and-worksheets.pdfhttps://tax.ri.gov/sites/g/files/xkgbur541/files/2022-12/2022%20Tax%20Rate%20and%20Worksheets.pdf

### ri_subtractions

**Label**: Rhode Island AGI Subtractions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.ri.gov/sites/g/files/xkgbur541/files/2022-12/2022%201041%20Schedule%20M_w.pdf#page=1

### ri_taxable_income

**Label**: Rhode Island taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.ri.gov/sites/g/files/xkgbur541/files/2022-12/2022_1040WE_w_0.pdf

### ri_tuition_saving_program_contribution_subtraction

**Label**: Rhode Island tuition saving program contribution subtraction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- http://webserver.rilin.state.ri.us/Statutes/title44/44-30/44-30-12.HTM

### ri_withheld_income_tax

**Label**: Rhode Island withheld income tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

### roth_401k_contributions

**Label**: Roth 401(k) contributions
**Entity**: person
**Period**: year
**Unit**: currency-USD

Contributions to Roth 401(k) accounts.

### roth_403b_contributions

**Label**: Roth 403(b) contributions
**Entity**: person
**Period**: year
**Unit**: currency-USD

Contributions to Roth 403(b) accounts

### roth_ira_contributions

**Label**: Roth IRA contributions
**Entity**: person
**Period**: year
**Unit**: currency-USD

Contributions to Roth Individual Retirement Accounts.

### rrc_arpa

**Label**: Recovery Rebate Credit (ARPA)
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/6428B

### rrc_caa

**Label**: Recovery Rebate Credit (CAA)
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/6428A

### rrc_cares

**Label**: Recovery Rebate Credit (CARES)
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/6428

### s_corp_self_employment_income

**Label**: S-Corp self-employment income
**Entity**: person
**Period**: year
**Unit**: currency-USD

Partner self-employment earnings/loss (included in partnership_s_corp_income total)

### safmr_used_for_hcv

**Label**: Small area fair market rent used for purposes of the Housing Choice Voucher Program
**Entity**: household
**Period**: year

### salt

**Label**: State and local sales or income tax and real estate taxes subject to the SALT deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### salt_cap

**Label**: SALT cap
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/164

### salt_deduction

**Label**: SALT deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

State and local taxes plus real estate tax deduction from taxable income.

**References**:
- https://www.law.cornell.edu/uscode/text/26/164

### salt_refund_income

**Label**: State and local tax refund income
**Entity**: person
**Period**: year
**Unit**: currency-USD

### salt_refund_last_year

**Label**: SALT refund last year
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### savers_credit

**Label**: Retirement Savings Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.irs.gov/pub/irs-pdf/f8880.pdf
- https://www.law.cornell.edu/uscode/text/26/25B#c

### savers_credit_credit_limit

**Label**: Retirement Savings Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.irs.gov/pub/irs-pdf/f8880.pdf
- https://www.law.cornell.edu/uscode/text/26/25B#c

### savers_credit_eligible_person

**Label**: Eligible person for the retirement saving contributions credit
**Entity**: person
**Period**: year

**References**:
- https://www.irs.gov/pub/irs-pdf/f8880.pdf
- https://www.law.cornell.edu/uscode/text/26/25B#c

### savers_credit_person

**Label**: Retirement Savings Credit for eahc individual person
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.irs.gov/pub/irs-pdf/f8880.pdf
- https://www.law.cornell.edu/uscode/text/26/25B#c
- https://www.law.cornell.edu/uscode/text/26/25B#d_2

### savers_credit_potential

**Label**: Potential value of the Retirement Savings Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.irs.gov/pub/irs-pdf/f8880.pdf
- https://www.law.cornell.edu/uscode/text/26/25B#c

### savers_credit_qualified_contributions

**Label**: Retirement Savings Credit qualified contributions
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/25B#d_2

### sc_additions

**Label**: South Carolina additions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### sc_cdcc

**Label**: South Carolina CDCC
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

South Carolina Child and Dependent Care Credit

**References**:
- https://dor.sc.gov/forms-site/Forms/IITPacket_2022.pdf#page=22

### sc_dependent_exemption

**Label**: South Carolina dependent exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://dor.sc.gov/forms-site/Forms/SC1040_2022.pdf#page=2
- https://www.scstatehouse.gov/code/t12c006.php

### sc_eitc

**Label**: South Carolina EITC
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://dor.sc.gov/forms-site/Forms/TC60_2021.pdf

### sc_gross_earned_income

**Label**: South Carolina gross earned income
**Entity**: person
**Period**: year
**Unit**: currency-USD

### sc_income_tax

**Label**: South Carolina income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### sc_income_tax_before_non_refundable_credits

**Label**: South Carolina income tax before non-refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://dor.sc.gov/forms-site/Forms/SC1040TT_2022.pdf

### sc_income_tax_before_refundable_credits

**Label**: South Carolina income tax before refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### sc_military_deduction

**Label**: South Carolina military retirement deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.scstatehouse.gov/code/t12c006.php
- https://dor.sc.gov/forms-site/Forms/IITPacket_2021.pdf#page=17

### sc_military_deduction_indv

**Label**: South Carolina military deduction for eligible individuals
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.scstatehouse.gov/code/t12c006.php
- https://dor.sc.gov/forms-site/Forms/IITPacket_2021.pdf#page=17

### sc_military_deduction_survivors

**Label**: South Carolina military retirement deduction for survivors
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.scstatehouse.gov/code/t12c006.php
- https://dor.sc.gov/forms-site/Forms/IITPacket_2021.pdf#page=17

### sc_net_capital_gain_deduction

**Label**: South Carolina net capital gain deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://dor.sc.gov/forms-site/Forms/IITPacket_2021.pdf#page=15
- https://www.scstatehouse.gov/code/t12c006.php

### sc_non_refundable_credits

**Label**: South Carolina non-refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### sc_refundable_credits

**Label**: South Carolina refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### sc_retirement_cap

**Label**: South Carolina retirement income subtraction cap
**Entity**: person
**Period**: year
**Unit**: currency-USD

### sc_retirement_deduction

**Label**: South Carolina retirement deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### sc_retirement_deduction_indv

**Label**: South Carolina retirement deduction for eligible individuals
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.scstatehouse.gov/code/t12c006.php
- https://dor.sc.gov/forms-site/Forms/IITPacket_2021.pdf#page=17

### sc_retirement_deduction_survivors

**Label**: South Carolina retirement deduction for survivors
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.scstatehouse.gov/code/t12c006.php
- https://dor.sc.gov/forms-site/Forms/IITPacket_2021.pdf#page=17

### sc_senior_exemption

**Label**: South Carolina senior exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://dor.sc.gov/forms-site/Forms/SC1040_2022.pdf

### sc_senior_exemption_person

**Label**: South Carolina senior exemption for each person
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://dor.sc.gov/forms-site/Forms/SC1040_2022.pdf

### sc_state_tax_addback

**Label**: South Carolina State Tax addback
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://dor.sc.gov/forms-site/Forms/SC1040_2022.pdf#page=2
- https://dor.sc.gov/forms-site/Forms/SC1040inst_2022.pdf#page=2
- https://www.scstatehouse.gov/code/t12c006.php

### sc_subtractions

**Label**: South Carolina subtractions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### sc_taxable_income

**Label**: South Carolina taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://dor.sc.gov/forms-site/Forms/IITPacket_2022.pdf#page=33

### sc_tuition_credit

**Label**: South Carolina Tuition Credit
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://dor.sc.gov/forms-site/Forms/I319_2021.pdf#page=2
- https://www.scstatehouse.gov/code/t12c006.php

### sc_tuition_credit_eligible

**Label**: Eligible for the South Carolina Tuition Credit
**Entity**: person
**Period**: year

**References**:
- https://dor.sc.gov/forms-site/Forms/I319_2021.pdf#page=2
- https://www.scstatehouse.gov/code/t12c006.php

### sc_two_wage_earner_credit

**Label**: South Carolina two wage earner credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://dor.sc.gov/forms-site/Forms/SC1040TT_2021.pdf
- https://dor.sc.gov/forms-site/Forms/IITPacket_2021.pdf#page=23

### sc_withheld_income_tax

**Label**: South Carolina withheld income tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

### sc_young_child_deduction

**Label**: South Carolina young child deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://dor.sc.gov/forms-site/Forms/SC1040_2022.pdf#page=2
- https://www.scstatehouse.gov/code/t12c006.php

### school_meal_countable_income

**Label**: Countable income for school meals
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

SPM unit's countable income for school meal program

### school_meal_daily_subsidy

**Label**: School meal subsidies per child per day
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

Value of school meal subsidies per child per day

### school_meal_fpg_ratio

**Label**: School meal FPG ratio
**Entity**: spm_unit
**Period**: year
**Unit**: /1

SPM unit's federal poverty ratio for school meal program

### school_meal_net_subsidy

**Label**: Free and reduced price school meals
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

Value of free and reduced price school meal subsidies

### school_meal_paid_daily_subsidy

**Label**: School meal subsidies per full-price child per day
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

Value of school meal subsidies paid to full-price children per day in household's state

### school_meal_tier

**Label**: School meal tier
**Entity**: spm_unit
**Period**: year

SPM unit's school meal program tier

### section_22_income

**Label**: Section 22 income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Income upon which the elderly or disabled credit is applied

**References**:
- https://www.law.cornell.edu/uscode/text/26/22

### self_employed_health_insurance_ald

**Label**: Self-employed health insurance ALD
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Above-the-line deduction for self-employed health insurance contributions.

**References**:
- https://www.law.cornell.edu/uscode/text/26/162#l

### self_employed_health_insurance_ald_person

**Label**: Self-employed health insurance ALD for each person
**Entity**: person
**Period**: year
**Unit**: currency-USD

Personal above-the-line deduction for self-employed health insurance contributions.

**References**:
- https://www.law.cornell.edu/uscode/text/26/162#l

### self_employed_health_insurance_premiums

**Label**: Self-employed health insurance premiums
**Entity**: person
**Period**: year
**Unit**: currency-USD

Health insurance premiums for plans covering individuals who are not covered by any employer-sponsored health insurance.

### self_employed_pension_contribution_ald

**Label**: Self-employed pension contribution ALD
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Above-the-line deduction for self-employed pension plan contributions.

**References**:
- https://www.law.cornell.edu/uscode/text/26/162#l

### self_employed_pension_contribution_ald_person

**Label**: Self-employed pension contribution ALD for each person
**Entity**: person
**Period**: year
**Unit**: currency-USD

Personal above-the-line deduction for self-employed pension plan contributions.

**References**:
- https://www.law.cornell.edu/uscode/text/26/162#l

### self_employed_pension_contributions

**Label**: Self-employed pension contributions
**Entity**: person
**Period**: year
**Unit**: currency-USD

Pension plan contributions associated with plans for the self employed.

### self_employment_income

**Label**: self-employment income
**Entity**: person
**Period**: year
**Unit**: currency-USD

Self-employment non-farm income.

**References**:
- https://www.law.cornell.edu/uscode/text/26/1402#a

### self_employment_income_before_lsr

**Label**: self-employment income before labor supply responses
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/1402#a

### self_employment_income_behavioral_response

**Label**: self-employment income behavioral response
**Entity**: person
**Period**: year
**Unit**: currency-USD

### self_employment_income_last_year

**Label**: self-employment income last year
**Entity**: person
**Period**: year
**Unit**: currency-USD

Self-employment income in prior year.

### self_employment_income_would_be_qualified

**Label**: Self-employment income would be qualified
**Entity**: person
**Period**: year

Whether self-employment income would be considered qualified business income.

**References**:
- https://www.law.cornell.edu/uscode/text/26/199A#c_3_A

### self_employment_medicare_tax

**Label**: Self-employment Medicare tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/1401#b_1

### self_employment_social_security_tax

**Label**: Self-employment Social Security tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/1401#a

### self_employment_tax

**Label**: self-employment tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

### self_employment_tax_ald

**Label**: Self-employment tax ALD deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Above-the-line deduction for self-employment tax

**References**:
- https://www.law.cornell.edu/uscode/text/26/164#f

### self_employment_tax_ald_person

**Label**: Self-employment tax ALD deduction for each person
**Entity**: person
**Period**: year
**Unit**: currency-USD

Personal above-the-line deduction for self-employment tax

**References**:
- https://www.law.cornell.edu/uscode/text/26/164#f

### sep_distributions

**Label**: SEP distributions
**Entity**: person
**Period**: year
**Unit**: currency-USD

### separate_filer_itemizes

**Label**: Separate filer itemizes
**Entity**: tax_unit
**Period**: year

Whether the taxpayer in this tax unit has a spouse who files separately and itemizes deductions.

### sewage_expense

**Label**: Sewage expense
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### share_of_care_and_support_costs_paid_by_tax_filer

**Label**: The percentage of care and support costs of a senior paid by the tax filer
**Entity**: person
**Period**: year

### short_term_capital_gains

**Label**: short-term capital gains
**Entity**: person
**Period**: year
**Unit**: currency-USD

Net gains made from sales of assets held for one year or less(losses are expressed as negative gains).

**References**:
- {'title': '26 U.S. Code § 1222(1)', 'href': 'https://www.law.cornell.edu/uscode/text/26/1222#1'}

### slcsp

**Label**: Second-lowest ACA silver-plan cost
**Entity**: tax_unit
**Period**: month
**Unit**: currency-USD

### slcsp_age_0

**Label**: Second-lowest ACA silver-plan for a person aged 0
**Entity**: household
**Period**: month
**Unit**: currency-USD

### slcsp_age_curve_amount_person

**Label**: Second-lowest ACA silver-plan cost, for people in age curve states
**Entity**: person
**Period**: month
**Unit**: currency-USD

### slcsp_age_curve_applies

**Label**: ACA age curve applies, rather than family tier
**Entity**: tax_unit
**Period**: month

### slcsp_family_tier_amount

**Label**: ACA family tier premium amount
**Entity**: tax_unit
**Period**: month
**Unit**: currency-USD

### slcsp_family_tier_applies

**Label**: ACA family tier applies, rather than age curves
**Entity**: tax_unit
**Period**: month

### slcsp_family_tier_category

**Label**: ACA family tier category for premium calculation
**Entity**: tax_unit
**Period**: month

### slcsp_family_tier_multiplier

**Label**: ACA family tier multiplier for premium calculation
**Entity**: tax_unit
**Period**: month
**Unit**: /1

### slcsp_rating_area

**Label**: Second-lowest ACA silver-plan cost rating area
**Entity**: household
**Period**: year

### slcsp_rating_area_default

**Label**: Second-lowest ACA silver-plan cost rating area outside of LA County
**Entity**: household
**Period**: year

### slcsp_rating_area_la_county

**Label**: Second-lowest ACA silver-plan cost rating area in Los Angeles County
**Entity**: household
**Period**: year

### small_area_fair_market_rent

**Label**: Small area fair market rent
**Entity**: household
**Period**: year
**Unit**: currency-USD

### small_wind_energy_property_expenditures

**Label**: Qualified small wind energy property expenditures
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Expenditures for property which uses a wind turbine to generate electricity for use in connection with a dwelling unit located in the United States and used as a residence by the taxpayer.

**References**:
- https://www.law.cornell.edu/uscode/text/26/25D#d_4

### snap

**Label**: SNAP allotment
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

Final SNAP benefit amount, equal to net income minus food contribution

**References**:
- https://www.law.cornell.edu/uscode/text/7/2017#a

### snap_assets

**Label**: SNAP assets
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

Countable assets for SNAP limits

### snap_child_support_deduction

**Label**: SNAP child support payment deduction
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

Deduction from SNAP gross income for child support payments

**References**:
- https://www.law.cornell.edu/uscode/text/7/2014#e_4

### snap_child_support_gross_income_deduction

**Label**: SNAP child support payment deduction from gross income
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

Deduction for child support payments when computing SNAP gross income

**References**:
- https://www.law.cornell.edu/uscode/text/7/2014#e_4

### snap_deductions

**Label**: SNAP income deductions
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

Deductions made from gross income for SNAP benefits

**References**:
- https://www.law.cornell.edu/uscode/text/7/2014#e

### snap_dependent_care_deduction

**Label**: SNAP dependent care deduction
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

Deduction from SNAP gross income for dependent care

**References**:
- https://www.law.cornell.edu/uscode/text/7/2014#e_3

### snap_earned_income

**Label**: SNAP earned income
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

Earned income for calculating the SNAP earned income deduction

**References**:
- https://www.law.cornell.edu/cfr/text/7/273.9#b_1

### snap_earned_income_deduction

**Label**: SNAP earned income deduction
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

Earned income deduction for calculating SNAP benefit amount

**References**:
- https://www.law.cornell.edu/uscode/text/7/2014#e_2

### snap_emergency_allotment

**Label**: SNAP emergency allotment
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

SNAP emergency allotment

**References**:
- https://www.law.cornell.edu/uscode/text/7/2017#a

### snap_excess_medical_expense_deduction

**Label**: SNAP excess medical expense deduction
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

Deduction from SNAP gross income for excess medical expenses

**References**:
- https://www.law.cornell.edu/uscode/text/7/2014#e_5

### snap_excess_shelter_expense_deduction

**Label**: SNAP shelter deduction
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

Excess shelter expense deduction for calculating SNAP benefit amount

**References**:
- United States Code, Title 7, Section 2014(e)(6)

### snap_expected_contribution

**Label**: SNAP expected food contribution
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

Expected food contribution from SNAP net income

**References**:
- https://www.law.cornell.edu/uscode/text/7/2017#a

### snap_fpg

**Label**: SNAP federal poverty guideline
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

The federal poverty guideline used to determine SNAP eligibility.

### snap_gross_income

**Label**: SNAP gross income
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

Gross income for calculating SNAP eligibility

**References**:
- https://www.law.cornell.edu/uscode/text/7/2014#d

### snap_gross_income_fpg_ratio

**Label**: SNAP gross income to FPL ratio
**Entity**: spm_unit
**Period**: month
**Unit**: /1

SNAP gross income as a percentage of the federal poverty line

### snap_individual_utility_allowance

**Label**: SNAP Individual Utility Allowance
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

The individual utility allowance deduction for SNAP

### snap_limited_utility_allowance

**Label**: SNAP Limited Utility Allowance
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

The limited utility allowance deduction for SNAP

### snap_limited_utility_allowance_by_household_size

**Label**: SNAP Limited Utility Allowance by household size
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

### snap_max_allotment

**Label**: SNAP maximum allotment
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

Maximum SNAP allotment for SPM unit, based on the state group and household size.

### snap_min_allotment

**Label**: SNAP minimum allotment
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

Minimum allotment for SNAP based on household size and state

### snap_net_income

**Label**: SNAP net income
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

Final net income, after all deductions

**References**:
- https://www.law.cornell.edu/uscode/text/7/2014

### snap_net_income_fpg_ratio

**Label**: SNAP net income to FPL ratio
**Entity**: spm_unit
**Period**: month
**Unit**: /1

SNAP net income as a percentage of the federal poverty line

### snap_net_income_pre_shelter

**Label**: SNAP net income (pre-shelter)
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

SNAP net income before the shelter deduction, needed as intermediate to calculate shelter deduction

**References**:
- https://www.law.cornell.edu/uscode/text/7/2014#e_6_A

### snap_normal_allotment

**Label**: SNAP normal allotment
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

Normal SNAP benefit amount, equal to net income minus food contribution

**References**:
- https://www.law.cornell.edu/uscode/text/7/2017#a

### snap_region

**Label**: SNAP region
**Entity**: household
**Period**: year

### snap_region_str

**Label**: SNAP region
**Entity**: household
**Period**: year

### snap_reported

**Label**: SNAP (reported amount)
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

Reported value of SNAP.

### snap_self_employment_expense_deduction

**Label**: SNAP self-employment expense deduction
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

Self-employment income deduction for calculating SNAP benefit amount

**References**:
- https://www.snapscreener.com/blog/self-employment

### snap_self_employment_income_after_expense_deduction

**Label**: Self-employment income after the SNAP self-employment expense deduction
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### snap_self_employment_income_expense

**Label**: All self-employment income expenses for the SNAP self-employment deduction
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### snap_standard_deduction

**Label**: SNAP standard deduction
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

Standard deduction for calculating SNAP benefit amount

**References**:
- https://www.law.cornell.edu/uscode/text/7/2014#e_1

### snap_standard_utility_allowance

**Label**: SNAP Standard Utility Allowance
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

The standard utility allowance deduction for SNAP

### snap_standard_utility_allowance_by_household_size

**Label**: SNAP Standard Utility Allowance by household size
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

### snap_state_using_standard_utility_allowance

**Label**: Whether a state always uses the standard utility allowance
**Entity**: spm_unit
**Period**: month

### snap_take_up_seed

**Label**: Randomly assigned seed for SNAP take-up
**Entity**: spm_unit
**Period**: year

### snap_unearned_income

**Label**: SNAP unearned income
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

Unearned income for calculating the SNAP benefit

**References**:
- https://www.law.cornell.edu/cfr/text/7/273.9#b_2

### snap_unit_size

**Label**: SNAP unit
**Entity**: spm_unit
**Period**: year

### snap_utility_allowance

**Label**: Standard Utility Allowance
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

The regular utility allowance deduction for SNAP

### snap_utility_allowance_type

**Label**: SNAP utility allowance eligibility
**Entity**: spm_unit
**Period**: month

The type of utility allowance that is eligible for the SPM unit

### snap_utility_region

**Label**: SNAP utility region
**Entity**: household
**Period**: year

Region deciding the SNAP utility allowances.

### snap_utility_region_str

**Label**: SNAP utility region
**Entity**: household
**Period**: year

### social_security

**Label**: Social Security
**Entity**: person
**Period**: year
**Unit**: currency-USD

Social Security benefits, not including SSI

### social_security_dependents

**Label**: Social Security dependents benefits
**Entity**: person
**Period**: year
**Unit**: currency-USD

### social_security_disability

**Label**: Social Security disability benefits (SSDI)
**Entity**: person
**Period**: year
**Unit**: currency-USD

### social_security_retirement

**Label**: Social Security retirement benefits
**Entity**: person
**Period**: year
**Unit**: currency-USD

### social_security_survivors

**Label**: Social Security survivors benefits
**Entity**: person
**Period**: year
**Unit**: currency-USD

### social_security_taxable_self_employment_income

**Label**: Taxable self-employment income for computing Social Security tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/1402#b

### solar_electric_property_expenditures

**Label**: Qualified solar electric property expenditures
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Expenditures for property which uses solar energy to generate electricity for use in a dwelling unit located in the United States and used as a residence by the taxpayer.

**References**:
- https://www.law.cornell.edu/uscode/text/26/25D#d_2

### solar_water_heating_property_expenditures

**Label**: Qualified solar water heating property expenditures
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Expenditures for property to heat water for use in a dwelling unit located in the United States and used as a residence by the taxpayer if at least half of the energy used by such property for such purpose is derived from the sun.

**References**:
- https://www.law.cornell.edu/uscode/text/26/25D#d_1

### specified_possession_income

**Label**: Income from Guam, American Samoa, or the Northern Mariana Islands
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Income generated in the above territories by any individual who is a bona fide resident.

**References**:
- https://www.law.cornell.edu/uscode/text/26/931

### spm_unit_assets

**Label**: SPM unit assets
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### spm_unit_benefits

**Label**: Benefits
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### spm_unit_broadband_subsidy

**Label**: SPM unit broadband subsidy
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### spm_unit_broadband_subsidy_reported

**Label**: SPM unit reported broadband subsidy
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### spm_unit_capped_housing_subsidy

**Label**: Housing subsidies
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### spm_unit_capped_housing_subsidy_reported

**Label**: SPM unit capped housing subsidy
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### spm_unit_capped_work_childcare_expenses

**Label**: SPM unit work and childcare expenses
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### spm_unit_cash_assets

**Label**: SPM unit cash assets
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### spm_unit_ccdf_subsidy

**Label**: SPM unit CCDF subsidy
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### spm_unit_count

**Label**: SPM units represented
**Entity**: spm_unit
**Period**: year

### spm_unit_count_adults

**Label**: adults in SPM unit
**Entity**: spm_unit
**Period**: year

### spm_unit_count_children

**Label**: children in SPM unit
**Entity**: spm_unit
**Period**: year

### spm_unit_energy_subsidy

**Label**: SPM unit school energy subsidy
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### spm_unit_energy_subsidy_reported

**Label**: SPM unit school energy subsidy (reported)
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### spm_unit_federal_tax

**Label**: Federal income tax
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### spm_unit_federal_tax_reported

**Label**: Federal income tax (reported
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### spm_unit_fpg

**Label**: SPM unit's federal poverty guideline
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### spm_unit_id

**Label**: SPM unit ID
**Entity**: spm_unit
**Period**: year

### spm_unit_income_decile

**Label**: Income decile
**Entity**: spm_unit
**Period**: year

The income decile of the SPM unit, person-weighted and using OECD-equivalised net income

### spm_unit_is_in_deep_spm_poverty

**Label**: SPM unit in deep SPM poverty
**Entity**: spm_unit
**Period**: year

### spm_unit_is_in_spm_poverty

**Label**: SPM unit in SPM poverty
**Entity**: spm_unit
**Period**: year

### spm_unit_is_married

**Label**: SPM unit is married
**Entity**: spm_unit
**Period**: year

Whether the adults in this SPM unit are married.

### spm_unit_market_income

**Label**: Market income
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### spm_unit_net_income

**Label**: Net income
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### spm_unit_net_income_reported

**Label**: Reported net income
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### spm_unit_oecd_equiv_net_income

**Label**: Equivalised income
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

Equivalised net income for the SPM unit under the OECD method (divided by the sqare root of the number of persons in the household)

**References**:
- https://www.oecd.org/economy/growth/OECD-Note-EquivalenceScales.pdf

### spm_unit_paycheck_withholdings

**Label**: Paycheck withholdings of the SPM unit
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### spm_unit_payroll_tax

**Label**: Payroll tax
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### spm_unit_payroll_tax_reported

**Label**: SPM unit payroll tax (reported)
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### spm_unit_pell_grant

**Label**: Pell Grant amount
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

SPM unit's Pell Grant educational subsidy

### spm_unit_pre_subsidy_childcare_expenses

**Label**: SPM unit pre subsidy child care expenses
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### spm_unit_school_lunch_subsidy

**Label**: SPM unit school lunch subsidy
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### spm_unit_self_employment_tax

**Label**: Self employment tax
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### spm_unit_size

**Label**: SPM unit size
**Entity**: spm_unit
**Period**: year

### spm_unit_snap

**Label**: SPM unit SNAP subsidy
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### spm_unit_spm_expenses

**Label**: SPM unit's SPM expenses (other than taxes)
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### spm_unit_spm_threshold

**Label**: SPM unit's SPM poverty threshold
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### spm_unit_state_fips

**Label**: SPM unit state FIPS code
**Entity**: spm_unit
**Period**: year

### spm_unit_state_tax

**Label**: State income tax
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### spm_unit_state_tax_reported

**Label**: State income tax (reported)
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### spm_unit_taxes

**Label**: Taxes
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### spm_unit_total_ccdf_copay

**Label**: SPM unit total CCDF copay
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.ocfs.ny.gov/programs/childcare/stateplan/assets/2022-plan/FFY2022-2024-CCDF-Plan.pdf#page=107

### spm_unit_total_income_reported

**Label**: SPM unit total income
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### spm_unit_weight

**Label**: SPM unit weight
**Entity**: spm_unit
**Period**: year

### spm_unit_wic

**Label**: SPM unit WIC
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### spm_unit_wic_reported

**Label**: SPM unit reported WIC
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### spouse_earned

**Label**: Spouse's adjusted earnings
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### spouse_is_dependent_elsewhere

**Label**: Tax-unit spouse is dependent elsewhere
**Entity**: tax_unit
**Period**: year

Whether the spouse of the filer for this tax unit is claimed as a dependent in another tax unit.

### spouse_is_disabled

**Label**: Tax unit spouse is disabled
**Entity**: tax_unit
**Period**: year

### spouse_separate_adjusted_gross_income

**Label**: Spouse's tax unit's adjusted gross income if they file separately
**Entity**: tax_unit
**Period**: year

### spouse_separate_tax_unit_size

**Label**: Size of spouse's tax unit if they file separately
**Entity**: tax_unit
**Period**: year

### ssi

**Label**: SSI
**Entity**: person
**Period**: year
**Unit**: currency-USD

Supplemental Security Income

**References**:
- https://www.law.cornell.edu/uscode/text/42/1382

### ssi_amount_if_eligible

**Label**: SSI amount if eligible
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/42/1382#b

### ssi_blind_or_disabled_working_student_exclusion

**Label**: SSI blind or disabled working student earned income exclusion
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/cfr/text/20/416.1112#c_3

### ssi_category

**Label**: SSI category
**Entity**: person
**Period**: year

### ssi_claim_is_joint

**Label**: SSI claim is joint
**Entity**: person
**Period**: year

### ssi_countable_income

**Label**: SSI countable income
**Entity**: person
**Period**: year
**Unit**: currency-USD


Calculates total countable income for SSI:
  - Earned (after ignoring blind/disabled student exclusion)
  - Unearned
  - Parental deemed if child
  - Spousal deemed if married to an ineligible spouse
  - Applies standard SSI exclusions.


**References**:
- https://www.law.cornell.edu/uscode/text/42/1382a#b

### ssi_countable_resources

**Label**: SSI countable resources
**Entity**: person
**Period**: year
**Unit**: currency-USD

### ssi_earned_income

**Label**: SSI earned income
**Entity**: person
**Period**: year
**Unit**: currency-USD

### ssi_earned_income_deemed_from_ineligible_spouse

**Label**: SSI earned income (deemed from ineligible spouse)
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/cfr/text/20/416.1163

### ssi_engaged_in_sga

**Label**: Income less than the SGA limit
**Entity**: person
**Period**: year

**References**:
- https://www.ssa.gov/OP_Home/cfr20/416/416-0971.htm

### ssi_income_deemed_from_ineligible_spouse

**Label**: SSI income (deemed from ineligible spouse)
**Entity**: person
**Period**: year
**Unit**: currency-USD


Spousal deeming: 
  1) If leftover spouse income <= (coupleFBR - indivFBR), then 0 is deemed.
  2) Otherwise, spouse's deemed = (couple combined countable) - (individual alone countable).
     This yields 816 for 1986 Example 3 and 12000 for the 2025 test.


**References**:
- https://www.law.cornell.edu/cfr/text/20/416.1163

### ssi_ineligible_child_allocation

**Label**: SSI ineligible child allocation
**Entity**: person
**Period**: year
**Unit**: currency-USD

The amount of income that SSI deems ought to be spent on this child, and therefore is not deemed to SSI claimants.

**References**:
- https://www.law.cornell.edu/cfr/text/20/416.1163

### ssi_ineligible_parent_allocation

**Label**: SSI ineligible parent allocation
**Entity**: person
**Period**: year
**Unit**: currency-USD

The amount of income that SSI does not to SSI claimants.

**References**:
- https://www.law.cornell.edu/cfr/text/20/416.1163

### ssi_marital_both_eligible

**Label**: Both members of the marital unit are eligible for SSI
**Entity**: person
**Period**: year

### ssi_marital_earned_income

**Label**: Total SSI earned income for a marital unit
**Entity**: person
**Period**: year

### ssi_marital_unearned_income

**Label**: Total SSI unearned income for a marital unit
**Entity**: person
**Period**: year

### ssi_qualifying_quarters_earnings

**Label**: SSI Qualifying Quarters of Earnings
**Entity**: person
**Period**: year

Number of qualifying quarters of earnings for SSI eligibility

**References**:
- https://secure.ssa.gov/poms.nsf/lnx/0500502135

### ssi_reported

**Label**: SSI (reported)
**Entity**: person
**Period**: year
**Unit**: currency-USD

### ssi_unearned_income

**Label**: SSI earned income
**Entity**: person
**Period**: year
**Unit**: currency-USD

### ssi_unearned_income_deemed_from_ineligible_parent

**Label**: SSI unearned income (deemed from ineligible parent)
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/cfr/text/20/416.1165

### ssi_unearned_income_deemed_from_ineligible_spouse

**Label**: SSI unearned income (deemed from ineligible spouse)
**Entity**: person
**Period**: year
**Unit**: currency-USD

This is ignored if total income is under the SSI individual allowance.

**References**:
- https://www.law.cornell.edu/cfr/text/20/416.1163

### ssn_card_type

**Label**: Social Security Number (SSN) card type as an enumeration type
**Entity**: person
**Period**: year

### standard_deduction

**Label**: Standard deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/63#c

### state_agi

**Label**: State adjusted gross income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### state_and_local_sales_or_income_tax

**Label**: State and local sales or income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### state_cdcc

**Label**: State Child and Dependent Care Tax Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### state_code

**Label**: State code
**Entity**: household
**Period**: year

### state_code_str

**Label**: State code (string)
**Entity**: household
**Period**: year

State code variable, stored as a string

### state_ctc

**Label**: State Child Tax Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### state_eitc

**Label**: State Earned Income Tax Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### state_filing_status_if_married_filing_separately_on_same_return

**Label**: State filing status for the tax unit if married couple file separately on same return
**Entity**: tax_unit
**Period**: year

### state_fips

**Label**: State FIPS code
**Entity**: household
**Period**: year

State FIPS code

### state_group

**Label**: State group
**Entity**: household
**Period**: year

### state_group_str

**Label**: State group (string)
**Entity**: household
**Period**: year

State group variable, stored as a string

### state_income_tax

**Label**: state income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### state_income_tax_before_refundable_credits

**Label**: state income tax before refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### state_income_tax_reported

**Label**: reported State income tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

### state_itemized_deductions

**Label**: State itemized deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### state_name

**Label**: State
**Entity**: household
**Period**: year

### state_or_federal_salary

**Label**: state or federal salary
**Entity**: person
**Period**: year
**Unit**: currency-USD

### state_property_tax_credit

**Label**: State Property Tax Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### state_refundable_credits

**Label**: state refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### state_sales_tax

**Label**: State sales tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### state_sales_tax_income_bracket

**Label**: State Sales Tax Income Bracket
**Entity**: tax_unit
**Period**: year

### state_standard_deduction

**Label**: State standard deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### state_taxable_income

**Label**: State taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### state_withheld_income_tax

**Label**: state income tax before refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### strike_benefits

**Label**: strike benefits
**Entity**: person
**Period**: year
**Unit**: currency-USD

### student_loan_interest

**Label**: Student loan interest expense
**Entity**: person
**Period**: year
**Unit**: currency-USD

### student_loan_interest_ald

**Label**: Student loan interest ALD
**Entity**: person
**Period**: year
**Unit**: currency-USD

Above-the-line deduction for student loan interest

**References**:
- https://www.law.cornell.edu/uscode/text/26/221

### student_loan_interest_ald_eligible

**Label**: Eligible for the Student loan interest ALD
**Entity**: person
**Period**: year

**References**:
- https://www.law.cornell.edu/uscode/text/26/221

### student_loan_interest_ald_magi

**Label**: Modified adjusted gross income for the student loan interest ALD
**Entity**: person
**Period**: year
**Unit**: currency-USD

Above-the-line deduction for student loan interest

**References**:
- https://www.law.cornell.edu/uscode/text/26/221#b_2_C

### substitution_elasticity

**Label**: substitution elasticity of labor supply
**Entity**: person
**Period**: year
**Unit**: /1

### substitution_elasticity_lsr

**Label**: substitution elasticity of labor supply response
**Entity**: person
**Period**: year
**Unit**: /1

### surviving_spouse_eligible

**Label**: Qualifies for surviving spouse filing status
**Entity**: tax_unit
**Period**: year

**References**:
- https://www.law.cornell.edu/uscode/text/26/2#a

### takes_up_aca_if_eligible

**Label**: Whether a random eligible SPM unit does not claim ACA Premium Tax Credit
**Entity**: tax_unit
**Period**: year

### takes_up_dc_ptc

**Label**: Takes up the DC property tax credit
**Entity**: tax_unit
**Period**: year

### takes_up_eitc

**Label**: takes up the EITC
**Entity**: tax_unit
**Period**: year

### takes_up_medicaid_if_eligible

**Label**: Whether a random eligible person unit does not enroll in Medicaid
**Entity**: person
**Period**: year

### takes_up_snap_if_eligible

**Label**: Whether a random eligible SPM unit does not claim SNAP
**Entity**: spm_unit
**Period**: year

### tanf

**Label**: TANF
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

Value of Temporary Assistance for Needy Families benefit received, summing all state-specific TANF programs.

### tanf_person

**Label**: Per-capita TANF
**Entity**: person
**Period**: year
**Unit**: currency-USD

Per-capita value of Temporary Assistance for Needy Families benefit.

### tanf_reported

**Label**: Reported TANF
**Entity**: person
**Period**: year
**Unit**: currency-USD

Amount of Temporary Assistance for Needy Families benefit reported.

### tax_exempt_401k_distributions

**Label**: Tax-exempt 401(k) distributions
**Entity**: person
**Period**: year
**Unit**: currency-USD

Tax-exempt distributions from 401(k) accounts (typically Roth).

### tax_exempt_403b_distributions

**Label**: tax-exempt 403(b) distributions
**Entity**: person
**Period**: year
**Unit**: currency-USD

Tax-exempt distributions from 403(b) accounts (typically Roth).

### tax_exempt_interest_income

**Label**: tax-exempt interest income
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/subtitle-A/chapter-1/subchapter-B/part-III

### tax_exempt_ira_distributions

**Label**: Tax-exempt IRA distributions
**Entity**: person
**Period**: year
**Unit**: currency-USD

Tax-exempt distributions from individual retirement accounts (qualifying Roth distributions).

### tax_exempt_pension_income

**Label**: tax-exempt pension income
**Entity**: person
**Period**: year
**Unit**: currency-USD

### tax_exempt_private_pension_income

**Label**: tax-exempt private pension income
**Entity**: person
**Period**: year
**Unit**: currency-USD

Tax-exempt income from non-government employee pensions.

### tax_exempt_public_pension_income

**Label**: tax-exempt public pension income
**Entity**: person
**Period**: year
**Unit**: currency-USD

Tax-exempt income from government employee pensions.

### tax_exempt_retirement_distributions

**Label**: Tax-exempt retirement account distributions
**Entity**: person
**Period**: year
**Unit**: currency-USD

### tax_exempt_sep_distributions

**Label**: tax-exempt SEP distributions
**Entity**: person
**Period**: year
**Unit**: currency-USD

### tax_exempt_social_security

**Label**: Tax-exempt Social Security
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### tax_exempt_unemployment_compensation

**Label**: Tax-exempt unemployment compensation
**Entity**: person
**Period**: year
**Unit**: currency-USD

### tax_liability_if_itemizing

**Label**: Tax liability if itemizing
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### tax_liability_if_not_itemizing

**Label**: Tax liability if not itemizing
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### tax_preparation_fees

**Label**: Tax preparation fees
**Entity**: person
**Period**: year
**Unit**: currency-USD

### tax_unit_child_dependents

**Label**: Number of child dependents in the tax unit
**Entity**: tax_unit
**Period**: year

### tax_unit_childcare_expenses

**Label**: Childcare expenses
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### tax_unit_children

**Label**: Number of children in tax unit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### tax_unit_combined_income_for_social_security_taxability

**Label**: Taxable Social Security combined income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/86https://www.ssa.gov/benefits/retirement/planner/taxes.html

### tax_unit_count

**Label**: Tax units represented
**Entity**: tax_unit
**Period**: year

### tax_unit_count_dependents

**Label**: Number of dependents
**Entity**: tax_unit
**Period**: year

### tax_unit_dependents

**Label**: Number of dependents in the tax unit
**Entity**: tax_unit
**Period**: year

### tax_unit_earned_income

**Label**: Tax unit earned income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### tax_unit_earned_income_last_year

**Label**: Tax unit earned income last year
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### tax_unit_fpg

**Label**: Tax unit's federal poverty guideline
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### tax_unit_grandparents

**Label**: Number of grandparents in the tax unit
**Entity**: tax_unit
**Period**: year

### tax_unit_household_id

**Label**: Tax unit household ID
**Entity**: tax_unit
**Period**: year

### tax_unit_id

**Label**: Unique reference for this tax unit
**Entity**: tax_unit
**Period**: year

### tax_unit_income_ami_ratio

**Label**: Ratio of tax unit income to area median income
**Entity**: tax_unit
**Period**: year

### tax_unit_is_filer

**Label**: files taxes
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Whether this tax unit has a non-zero income tax liability.

### tax_unit_is_joint

**Label**: Is joint-filing tax unit
**Entity**: tax_unit
**Period**: year

Whether this tax unit is a joint filer.

### tax_unit_itemizes

**Label**: Itemizes tax deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Whether tax unit elects to itemize deductions rather than claim the standard deduction.

### tax_unit_married

**Label**: Tax unit is married
**Entity**: tax_unit
**Period**: year

### tax_unit_medicaid_income_level

**Label**: Medicaid/CHIP-related modified adjusted gross income (MAGI) level
**Entity**: tax_unit
**Period**: year
**Unit**: /1

Medicaid/CHIP-related MAGI as fraction of federal poverty line.Documentation: 'Federal poverty level (FPL)' at the following URL:URL: https://www.healthcare.gov/glossary/federal-poverty-level-fpl/**Pregnant Women:**  * Pregnant women are counted as themselves plus the number of children they are expecting to deliver    when determining household size for Medicaid eligibility.  * Sources:      URL: https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11618&fileName=10%20CCR%25202505-10%208.100      URL: https://www.cms.gov/marketplace/technical-assistance-resources/special-populations-pregnant-women.pdf

### tax_unit_parents

**Label**: Number of parents in the tax unit
**Entity**: tax_unit
**Period**: year

### tax_unit_partnership_s_corp_income

**Label**: Tax unit partnership/S-corp income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Combined partnership/S-corporation income for the tax unit.

### tax_unit_rental_income

**Label**: Tax unit rental income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Combined rental income for the tax unit.

### tax_unit_size

**Label**: Tax unit size
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Number of people in the tax unit

### tax_unit_social_security

**Label**: Tax unit Social Security
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### tax_unit_ss_combined_income_excess

**Label**: Taxable Social Security combined income excess over base amount
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/86#b_1

### tax_unit_ssi

**Label**: Total SSI for the tax unit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### tax_unit_state

**Label**: Tax unit State
**Entity**: tax_unit
**Period**: year

### tax_unit_stillborn_children

**Label**: Number of stillborn children in the filing year
**Entity**: tax_unit
**Period**: year

### tax_unit_taxable_social_security

**Label**: Taxable Social Security benefits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Social security (OASDI) benefits included in AGI, including tier 1 railroad retirement benefits.

**References**:
- https://www.law.cornell.edu/uscode/text/26/86

### tax_unit_taxable_unemployment_compensation

**Label**: Taxable unemployment compensation
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Unemployment compensation included in AGI.

**References**:
- https://www.law.cornell.edu/uscode/text/26/85

### tax_unit_unemployment_compensation

**Label**: Tax unit unemployment compensation
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Combined unemployment compensation for the tax unit.

### tax_unit_weight

**Label**: Tax unit weight
**Entity**: tax_unit
**Period**: year

### taxable_401k_distributions

**Label**: Taxable 401(k) distributions
**Entity**: person
**Period**: year
**Unit**: currency-USD

Taxable distributions from 401k accounts (typically traditional).

### taxable_403b_distributions

**Label**: Taxable 403(b) distributions
**Entity**: person
**Period**: year
**Unit**: currency-USD

Taxable distributions from 403b accounts (typically traditional).

### taxable_earnings_for_social_security

**Label**: Taxable gross earnings for OASDI FICA
**Entity**: person
**Period**: year
**Unit**: currency-USD

### taxable_estate_value

**Label**: Taxable estate value
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/2001#b_1

### taxable_federal_pension_income

**Label**: Taxable federal pension income
**Entity**: person
**Period**: year
**Unit**: currency-USD

### taxable_income

**Label**: IRS taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### taxable_income_deductions

**Label**: Taxable income deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### taxable_income_deductions_if_itemizing

**Label**: Deductions if itemizing
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/63

### taxable_income_deductions_if_not_itemizing

**Label**: Deductions if not itemizing
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### taxable_income_less_qbid

**Label**: Taxable income (not considering QBID)
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### taxable_interest_income

**Label**: taxable interest income
**Entity**: person
**Period**: year
**Unit**: currency-USD

### taxable_ira_distributions

**Label**: Taxable IRA distributions
**Entity**: person
**Period**: year
**Unit**: currency-USD

Taxable distributions from individual retirement accounts (typically traditional IRAs).

### taxable_pension_income

**Label**: taxable pension income
**Entity**: person
**Period**: year
**Unit**: currency-USD

### taxable_private_pension_income

**Label**: taxable private pension income
**Entity**: person
**Period**: year
**Unit**: currency-USD

Taxable income from non-government employee pensions.

### taxable_public_pension_income

**Label**: taxable public pension income
**Entity**: person
**Period**: year
**Unit**: currency-USD

Taxable income from government employee pensions.

### taxable_retirement_distributions

**Label**: Taxable retirement account distributions
**Entity**: person
**Period**: year
**Unit**: currency-USD

### taxable_self_employment_income

**Label**: Taxable self-employment income
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/1402#a

### taxable_sep_distributions

**Label**: taxable SEP distributions
**Entity**: person
**Period**: year
**Unit**: currency-USD

### taxable_social_security

**Label**: Taxable Social Security
**Entity**: person
**Period**: year
**Unit**: currency-USD

### taxable_ss_magi

**Label**: Modified adjusted gross income (SS)
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Income used to determine taxability of Social Security.

**References**:
- https://www.law.cornell.edu/uscode/text/26/86

### taxable_uc_agi

**Label**: Taxable unemployment compensation for SS adjusted gross income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Income used to determine taxability of unemployment compensation.

**References**:
- https://www.law.cornell.edu/uscode/text/26/85

### taxable_unemployment_compensation

**Label**: Taxable unemployment compensation
**Entity**: person
**Period**: year
**Unit**: currency-USD

### taxpayer_has_itin

**Label**: Tax unit head or spouse has ITIN
**Entity**: tax_unit
**Period**: year

### taxsim_age1

**Label**: Age of first dependent
**Entity**: tax_unit
**Period**: year
**Unit**: year

Age of first dependent. Used for EITC, CTC and CCC. For 1991+ code students between 20 and 23 as 19 to get the EITC calculation correct. Code infants as "1". [For compatibiity with taxsim32, dep13-dep18 are accepted and have priority over age1-age3]. If niether dep19 or age1 are present in an uploaded file than depx is used for the number of child eligible for the EIC, CTC and CDCC.

### taxsim_age2

**Label**: Age of second dependent
**Entity**: tax_unit
**Period**: year
**Unit**: year

### taxsim_age3

**Label**: Age of third dependent
**Entity**: tax_unit
**Period**: year
**Unit**: year

### taxsim_childcare

**Label**: Childcare
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### taxsim_dep13

**Label**: Children under 13
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### taxsim_dep17

**Label**: Children under 17
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### taxsim_dep18

**Label**: Children under 13
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### taxsim_depx

**Label**: Number of dependents
**Entity**: tax_unit
**Period**: year
**Unit**: person

Number of dependents (for personal exemption calculation). In the case of a file submission, if no age1 or dep19 variable is present, depx is used for the number of eligible children. You can negate this assumption by putting a large number (such as 99) in the age1 field.

### taxsim_dividends

**Label**: Dividends
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### taxsim_fiitax

**Label**: Federal income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### taxsim_gssi

**Label**: Gross Social Security Income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### taxsim_intrec

**Label**: Taxable interest
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### taxsim_ltcg

**Label**: Long-term capital gains
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### taxsim_mstat

**Label**: Marital Status
**Entity**: tax_unit
**Period**: year

### taxsim_page

**Label**: Age of primary taxpayer
**Entity**: tax_unit
**Period**: year
**Unit**: year

Age of primary taxpayer December 31st of the tax year (or zero). Taxpayer and spouse age variables determine eligibility for additional standard deductions, personal exemption, EITC and AMT exclusions.

### taxsim_pbusinc

**Label**: QBI for the primary taxpayer (TAXSIM)
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### taxsim_pensions

**Label**: Pensions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### taxsim_pprofinc

**Label**: SSTB income for the primary taxpayer (TAXSIM). Assumed zero.
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### taxsim_psemp

**Label**: Self-employment income of taxpayer (excluding QBI)
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### taxsim_pui

**Label**: Unemployment compensation (primary taxpayer)
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Unemployment Compensation received - primary taxpayer.

### taxsim_pwages

**Label**: Wages for primary taxpayer
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Wage and salary income of Primary Taxpayer

### taxsim_sage

**Label**: Age of spouse
**Entity**: tax_unit
**Period**: year
**Unit**: year

Age of spouse (zero if unknown or not a joint return). It is an error to specify a non-zero spouse age for an unmarried taxpayer.

### taxsim_sbusinc

**Label**: QBI for the spouse taxpayer (TAXSIM)
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### taxsim_scorp

**Label**: S-corp income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### taxsim_siitax

**Label**: State income tax liability
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### taxsim_sprofinc

**Label**: SSTB income for the spouse of the taxpayer (TAXSIM). Assumed zero.
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### taxsim_ssemp

**Label**: Self-employment income of spouse (excluding QBI)
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### taxsim_state

**Label**: State code
**Entity**: tax_unit
**Period**: year

SOI codes. These run from 1 for Alabama to 51 for Wyoming and are not the Census or PSID codes. See state list,and also item two above.). Use zero for "no state tax calculation"

### taxsim_stcg

**Label**: Short-term capital gains
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### taxsim_swages

**Label**: Wages for spouse
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Wage and salary income of spouse

### taxsim_taxsimid

**Label**: Tax unit ID
**Entity**: tax_unit
**Period**: year

### taxsim_tfica

**Label**: Employee share of FICA + SECA + Additional Medicare Tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### taxsim_ui

**Label**: Unemployment compensation (spouse)
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Unemployment compensation received - secondary taxpayer. The split is relevant only 2020-2021.

### taxsim_v10

**Label**: Federal AGI
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

TAXSIM federal AGI

### taxsim_v11

**Label**: UI in AGI
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### taxsim_v12

**Label**: Social Security in AGI
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### taxsim_v18

**Label**: Taxable income in TAXSIM
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### taxsim_v25

**Label**: EITC
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### taxsim_year

**Label**: Policy year
**Entity**: tax_unit
**Period**: year

Tax year ending Dec 31(4 digits between 1960 and 2023, but state must be zero if year is before 1977. (We don't have code for state laws before 1977.) State tax laws are effectively inflated by 2.5%/year after 2021.

### technical_institution_student

**Label**: Is a technical institution student
**Entity**: person
**Period**: year

### tenure_type

**Label**: tenure type
**Entity**: household
**Period**: year

### three_digit_zip_code

**Label**: Three-digit zipcode
**Entity**: household
**Period**: year

### tip_income

**Label**: Tip income
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/cfr/text/26/31.3402(k)-1

### tip_income_deduction

**Label**: Tip income deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### tip_income_deduction_ssn_requirement_met

**Label**: SSN requirement met for the tip income deduction
**Entity**: tax_unit
**Period**: year

### total_disability_payments

**Label**: Disability (total) payments
**Entity**: person
**Period**: year
**Unit**: currency-USD

Wages (or payments in lieu thereof) paid to an individual for permanent and total disability

### total_itemized_taxable_income_deductions

**Label**: Total values of itemized taxable income deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### total_misc_deductions

**Label**: Total miscellaneous deductions subject to the AGI floor
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/67#b

### traditional_401k_contributions

**Label**: Traditional 401(k) contributions
**Entity**: person
**Period**: year
**Unit**: currency-USD

Contributions to traditional 401(k) accounts.

### traditional_403b_contributions

**Label**: Traditional 403(b) contributions
**Entity**: person
**Period**: year
**Unit**: currency-USD

Contributions to traditional 403(b) accounts.

### traditional_ira_contributions

**Label**: Traditional IRA contributions
**Entity**: person
**Period**: year
**Unit**: currency-USD

Contributions to traditional Individual Retirement Accounts.

### trash_expense

**Label**: Trash expense
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### tuition_and_fees

**Label**: Tuition and fees (from Form 8917)
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### tuition_and_fees_deduction

**Label**: Tuition and fees deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.irs.gov/pub/irs-pdf/f8917.pdf#page=2https://irc.bloombergtax.com/public/uscode/doc/irc/section_222

### tuition_and_fees_deduction_eligible

**Label**: Tuition and fees deduction eligible
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.irs.gov/pub/irs-pdf/f8917.pdf#page=2https://irc.bloombergtax.com/public/uscode/doc/irc/section_222

### tx_tanf_income_limit

**Label**: Texas TANF income limit
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.hhs.texas.gov/services/financial/cash/tanf-cash-help

### ucgid

**Label**: Unified Congressional Geographic Identifier (UCGID)
**Entity**: household
**Period**: year


Unified Congressional Geographic Identifier (UCGID) for the household as defined by the U.S. Census Bureau.


### ucgid_str

**Label**: UCGID (string)
**Entity**: household
**Period**: year

UCGID variable, stored as a string

### unadjusted_basis_qualified_property

**Label**: Unadjusted basis for qualified property
**Entity**: person
**Period**: year
**Unit**: currency-USD

Share of unadjusted basis upon acquisition of all property held by qualified pass-through businesses.

**References**:
- https://www.law.cornell.edu/uscode/text/26/199A#b_6

### uncapped_ssi

**Label**: Uncapped SSI
**Entity**: person
**Period**: year
**Unit**: currency-USD

Maximum SSI, less countable income (can be below zero).

### under_12_months_postpartum

**Label**: Under 12 months postpartum
**Entity**: person
**Period**: year

### under_60_days_postpartum

**Label**: Under 60 days postpartum
**Entity**: person
**Period**: year
**Unit**: currency-USD

### unemployment_compensation

**Label**: unemployment compensation
**Entity**: person
**Period**: year
**Unit**: currency-USD

Income from unemployment compensation programs.

### unrecaptured_section_1250_gain

**Label**: Un-recaptured section 1250 gain
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- {'title': '26 U.S. Code § 1250(a)', 'href': 'https://www.law.cornell.edu/uscode/text/26/1250#a'}

### unreimbursed_business_employee_expenses

**Label**: Unreimbursed business employee expenses
**Entity**: person
**Period**: year
**Unit**: currency-USD

### unreported_payroll_tax

**Label**: Unreported payroll taxes from Form 4137 or 8919
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### urgent_care_expense

**Label**: Urgent care expenses
**Entity**: person
**Period**: year
**Unit**: currency-USD

### us_bonds_for_higher_ed

**Label**: Income from U.S. bonds spent on higher education
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.law.cornell.edu/uscode/text/26/135

### us_govt_interest

**Label**: Interest on U.S. government obligations
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Interest on U.S. government obligations such as U.S. savings bonds, U.S. Treasury bills, and U.S. government certificates.

### used_clean_vehicle_credit

**Label**: Used clean vehicle credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Nonrefundable credit for the purchase of a previously-owned clean vehicle

**References**:
- https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=370

### used_clean_vehicle_credit_credit_limit

**Label**: Used clean vehicle credit credit limit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Nonrefundable credit for the purchase of a previously-owned clean vehicle

**References**:
- https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=370

### used_clean_vehicle_credit_eligible

**Label**: Eligible for used clean vehicle credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Eligible for nonrefundable credit for the purchase of a previously-owned clean vehicle

**References**:
- https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=370

### used_clean_vehicle_credit_potential

**Label**: Potential value of the Used clean vehicle credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Nonrefundable credit for the purchase of a previously-owned clean vehicle

**References**:
- https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=370

### used_clean_vehicle_sale_price

**Label**: Sale price of newly purchased used clean vehicle
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ut_additions

**Label**: Utah additions to income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Form TC-40, line 5

**References**:
- https://le.utah.gov/xcode/Title59/Chapter10/59-10-S114.html?v=C59-10-S114_2022032320220323

### ut_at_home_parent_credit

**Label**: Utah at-home parent credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://le.utah.gov/xcode/Title59/Chapter10/59-10-S1005.html
- https://www.taxformfinder.org/forms/2021/2021-utah-tc-40-full-packet.pdf#page=23

### ut_at_home_parent_credit_agi_eligible

**Label**: Eligible for the Utah at-home parent credit based on adjusted gross income
**Entity**: tax_unit
**Period**: year

**References**:
- https://le.utah.gov/xcode/Title59/Chapter10/59-10-S1005.html
- https://www.taxformfinder.org/forms/2021/2021-utah-tc-40-full-packet.pdf#page=23

### ut_at_home_parent_credit_earned_income_eligible_person

**Label**: Eligible person for the Utah at-home parent credit income based on the earned income
**Entity**: person
**Period**: year

**References**:
- https://le.utah.gov/xcode/Title59/Chapter10/59-10-S1005.html
- https://www.taxformfinder.org/forms/2021/2021-utah-tc-40-full-packet.pdf#page=23

### ut_claims_retirement_credit

**Label**: claims the Utah retirement credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Utah residents can claim only one of the retirement credit or the social security benefits credit. We assume they claim the one with higher value.

### ut_ctc

**Label**: Utah Child Tax Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ut_eitc

**Label**: Utah Earned Income Tax Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

This credit is a fraction of the federal EITC.

**References**:
- https://le.utah.gov/xcode/Title59/Chapter10/59-10-S1044.html?v=C59-10-S1044_2022050420220504

### ut_federal_deductions_for_taxpayer_credit

**Label**: Utah federal deductions considered for taxpayer credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

These federal deductions are added to the Utah personal exemption to determine the Utah taxpayer credit.

**References**:
- https://le.utah.gov/xcode/Title59/Chapter10/59-10-S114.html?v=C59-10-S114_2022032320220323

### ut_income_tax

**Label**: Utah income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.utah.gov/forms/current/tc-40.pdf#page=2

### ut_income_tax_before_credits

**Label**: Utah income tax before credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Form TC-40, line 10

**References**:
- https://le.utah.gov/xcode/Title59/Chapter10/59-10-S104.html?v=C59-10-S104_2022050420220504

### ut_income_tax_before_non_refundable_credits

**Label**: Utah income tax before non-refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.utah.gov/forms/current/tc-40.pdf#page=1

### ut_income_tax_before_refundable_credits

**Label**: Utah income tax before refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Form TC-40, line 32

### ut_income_tax_exempt

**Label**: exempt from Utah income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Form TC-40, line 21

**References**:
- https://le.utah.gov/xcode/Title59/Chapter10/59-10-S104.1.html?v=C59-10-S104.1_1800010118000101

### ut_non_refundable_credits

**Label**: Utah non-refundable tax credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ut_personal_exemption

**Label**: Utah personal exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://le.utah.gov/xcode/Title59/Chapter10/59-10-S114.html?v=C59-10-S114_2022032320220323
- https://le.utah.gov/xcode/Title59/Chapter10/59-10-S1018.html
- https://tax.utah.gov/forms/current/tc-40inst.pdf#page=4

### ut_personal_exemption_additional_dependent_eligible

**Label**: Utah additional dependent personal exemption eligible
**Entity**: person
**Period**: year

**References**:
- https://le.utah.gov/xcode/Title59/Chapter10/59-10-S1018.html

### ut_personal_exemption_additional_dependents

**Label**: Utah total additional dependents under the personal exemption
**Entity**: tax_unit
**Period**: year

**References**:
- https://le.utah.gov/xcode/Title59/Chapter10/59-10-S1018.html

### ut_refundable_credits

**Label**: Utah refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ut_retirement_credit

**Label**: Utah retirement credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ut_retirement_credit_max

**Label**: Utah retirement credit maximum amount
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://incometax.utah.gov/credits/retirement-credit

### ut_ss_benefits_credit

**Label**: Utah Social Security Benefits Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### ut_ss_benefits_credit_max

**Label**: Utah Social Security Benefits Credit maximum amount
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://incometax.utah.gov/credits/ss-benefits

### ut_state_tax_refund

**Label**: Utah state tax refund
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Form TC-40, line 7

### ut_subtractions

**Label**: Utah subtractions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Form TC-40, line 8

**References**:
- https://le.utah.gov/xcode/Title59/Chapter10/59-10-S114.html?v=C59-10-S114_2022032320220323

### ut_taxable_income

**Label**: Utah taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Form TC-40, line 9

**References**:
- https://tax.utah.gov/forms/2021/tc-40.pdf#page=1

### ut_taxpayer_credit

**Label**: Utah taxpayer credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Form TC-40, line 20

**References**:
- https://le.utah.gov/xcode/Title59/Chapter10/59-10-S1018.html?v=C59-10-S1018_2023050320230503

### ut_taxpayer_credit_max

**Label**: Utah initial taxpayer credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Form TC-40, line (12 through) 16

### ut_taxpayer_credit_phase_out_income

**Label**: Utah taxpayer credit phase-out income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Income that reduces the Utah taxpayer credit. Form TC-40, line 18

### ut_taxpayer_credit_reduction

**Label**: Utah taxpayer credit reduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Form TC-40, line 19

### ut_total_dependents

**Label**: Utah total dependents
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Form TC-40, line 2c

### ut_total_income

**Label**: Utah total income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Form TC-40, line 6

**References**:
- https://tax.utah.gov/forms/2021/tc-40.pdf#page=1

### ut_withheld_income_tax

**Label**: Utah withheld income tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

### utilities_included_in_rent

**Label**: Whether utilities are included in rent payments
**Entity**: tax_unit
**Period**: year

### utility_expense

**Label**: Utility expenses
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### va_additions

**Label**: Virginia additions to federal adjusted gross income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/
- https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=24

### va_age_deduction

**Label**: Virginia age deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=16

### va_age_deduction_agi

**Label**: Virginia adjusted gross income for the age deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/
- https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=17

### va_aged_blind_exemption

**Label**: Virginia aged/blind exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/

### va_aged_blind_exemption_person

**Label**: Virginia aged/blind exemption for each person
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/

### va_agi

**Label**: Virginia adjusted federal adjusted gross income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.tax.virginia.gov/sites/default/files/taxforms/individual-income-tax/2022/760-2022.pdf
- https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/

### va_agi_less_exemptions_person

**Label**: Difference between individual VAGI and personal exemption amounts
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=19

### va_agi_person

**Label**: Virginia adjusted gross income for each person
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.tax.virginia.gov/laws-rules-decisions/rulings-tax-commissioner/13-5

### va_agi_share

**Label**: Virginia share of state adjusted gross income of each person
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2021-760-instructions.pdf#page=20

### va_capped_state_and_local_sales_or_income_tax

**Label**: Capped state and local sales or income tax for Virginia itemized deductions purposes
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### va_child_dependent_care_deduction_cdcc_limit

**Label**: Federal CDCC-relevant care expense limit for Virginia tax purposes
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2021-760-instructions.pdf#page=29

### va_child_dependent_care_expense_deduction

**Label**: Virginia child and dependent care expense deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2021-760-instructions.pdf#page=29

### va_claims_refundable_eitc

**Label**: Filer claims refundable Virginia EITC
**Entity**: tax_unit
**Period**: year

Whether the filer claims the refundable over the non-refundable Virginia Earned Income Tax Credit.

### va_deductions

**Label**: Virginia deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/https://www.tax.virginia.gov/sites/default/files/taxforms/individual-income-tax/2022/760-2022.pdf#page=1

### va_disability_income_subtraction

**Label**: Virginia disability income subtraction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/

### va_eitc

**Label**: Virginia Earned Income Tax Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Refundable or non-refundable Virginia EITC

**References**:
- https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=32

### va_eitc_person

**Label**: Virginia Earned Income Tax Credit per individual when married filing seperately
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=32

### va_federal_state_employees_subtraction

**Label**: Virginia federal state employees subtraction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/

### va_income_tax

**Label**: Virginia income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### va_income_tax_before_non_refundable_credits

**Label**: Virginia income tax before non-refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/

### va_income_tax_before_refundable_credits

**Label**: Virginia income tax before credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/

### va_income_tax_if_claiming_non_refundable_eitc

**Label**: Virginia tax liability if claiming non-refundable Virginia EITC
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### va_income_tax_if_claiming_refundable_eitc

**Label**: Virginia tax liability if claiming refundable Virginia EITC
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### va_itemized_deductions

**Label**: Virginia itemized deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.tax.virginia.gov/sites/default/files/taxforms/individual-income-tax/2021/schedule-2021.pdf

### va_low_income_tax_credit

**Label**: Virginia low income tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=32
- https://law.lis.virginia.gov/vacodeupdates/title58.1/section58.1-339.8/

### va_low_income_tax_credit_agi_eligible

**Label**: Eligible for the Virginia low income tax credit
**Entity**: tax_unit
**Period**: year

### va_low_income_tax_credit_eligible

**Label**: Eligible for the Virginia Low Income Tax Credit
**Entity**: tax_unit
**Period**: year

### va_military_basic_pay_subtraction

**Label**: Virginia military basic pay subtraction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/

### va_military_benefit_subtraction

**Label**: Virginia military benefit subtraction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/

### va_must_file

**Label**: Tax unit must file Virginia income taxes
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2023-760-instructions.pdf#page=10

### va_national_guard_subtraction

**Label**: Virginia national guard pay subtraction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/

### va_non_refundable_credits

**Label**: Virginia non-refundable income tax credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/

### va_non_refundable_eitc

**Label**: Virginia non-refundable EITC
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=32

### va_non_refundable_eitc_if_claimed

**Label**: Virginia non-refundable EITC if claimed
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=32

### va_personal_exemption

**Label**: Virginia personal exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/

### va_personal_exemption_person

**Label**: Virginia personal exemption for each person
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/

### va_rebate

**Label**: Virginia rebate
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://budget.lis.virginia.gov/item/2023/2/HB6001/Introduced/3/3-5.28/

### va_reduced_itemized_deductions

**Label**: Virginia reduced itemized deductions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.tax.virginia.gov/sites/default/files/taxforms/individual-income-tax/2021/schedule-2021.pdf

### va_refundable_credits

**Label**: Virginia refundable income tax credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/

### va_refundable_eitc

**Label**: Virginia refundable earned income tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Refundable EITC credit reducing Virginia State income tax

**References**:
- https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=32

### va_refundable_eitc_if_claimed

**Label**: Virginia refundable earned income tax credit if claimed
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=32

### va_spouse_tax_adjustment

**Label**: Virginia Spouse Tax Adjustment
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=19

### va_spouse_tax_adjustment_eligible

**Label**: Eligible for Virginia's spouse tax adjustment
**Entity**: tax_unit
**Period**: year

**References**:
- https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=19

### va_standard_deduction

**Label**: Virginia standard deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/

### va_subtractions

**Label**: Virginia subtractions from the adjusted gross income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### va_taxable_income

**Label**: Virginia taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/https://www.tax.virginia.gov/sites/default/files/taxforms/individual-income-tax/2022/760-2022.pdf#page=1

### va_total_exemptions

**Label**: Virginia exemptions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/

### va_withheld_income_tax

**Label**: Virginia withheld income tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

### veterans_benefits

**Label**: Veterans benefits
**Entity**: person
**Period**: year
**Unit**: currency-USD

Veterans benefits from past military service.

### vita_eligible

**Label**: Eligible for the VITA program
**Entity**: person
**Period**: year

### vt_additions

**Label**: Vermont AGI additions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Additions to Vermont adjusted gross income

**References**:
- https://tax.vermont.gov/sites/tax/files/documents/IN-112-2022.pdf#page=1https://legislature.vermont.gov/statutes/section/32/151/05811

### vt_agi

**Label**: Vermont adjusted gross income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.vermont.gov/sites/tax/files/documents/IN-111-2022.pdf (Line 3)

### vt_amt

**Label**: Vermont alternative minimum tax (AMT)
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://casetext.com/statute/vermont-statutes/title-32-taxation-and-finance/chapter-151-income-taxes/subchapter-002-taxation-of-individuals-trusts-and-estates/section-5822-tax-on-income-of-individuals-estates-and-trusts
- https://tax.vermont.gov/sites/tax/files/documents/RateSched-2021.pdf#page=1
- https://tax.vermont.gov/sites/tax/files/documents/RateSched-2022.pdf#page=1

### vt_capital_gains_exclusion

**Label**: Vermont capital gains exclusion
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Vermont excludes a portion of capital gains, calculated either as a flat amount or as a fraction of adjusted net capital gains, and limited by a fraction of federal taxable income.

**References**:
- https://tax.vermont.gov/sites/tax/files/documents/IN-153-2022.pdf#page=1https://legislature.vermont.gov/statutes/section/32/151/05811https://tax.vermont.gov/sites/tax/files/documents/IN-153%20Instr-2022.pdf

### vt_cdcc

**Label**: Vermont child care and dependent care credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.vermont.gov/sites/tax/files/documents/IN-112-2022.pdf#page=2https://law.justia.com/codes/vermont/2022/title-32/chapter-151/section-5828c/https://www.irs.gov/pub/irs-prior/f2441--2022.pdf#page=1

### vt_charitable_contribution_credit

**Label**: Vermont charitable contribution credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/vermont/2022/title-32/chapter-151/section-5822/https://tax.vermont.gov/sites/tax/files/documents/IN-111-2022.pdf#page=1

### vt_csrs_retirement_pay_exclusion

**Label**: Vermont Civil Service Retirement System (CSRS) retirement income exclusion
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Vermont Civil Service Retirement System (CSRS) retirement benefits exempt from Vermont taxation.

**References**:
- https://tax.vermont.gov/individuals/seniors-and-retirees
- https://legislature.vermont.gov/statutes/section/32/151/05830e

### vt_ctc

**Label**: Vermont child tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://casetext.com/statute/vermont-statutes/title-32-taxation-and-finance/chapter-151-income-taxes/subchapter-002-taxation-of-individuals-trusts-and-estates/section-5830f-see-note-vermont-child-tax-credit/1

### vt_eitc

**Label**: Vermont earned income tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.vermont.gov/sites/tax/files/documents/IN-112-2022.pdf#page=1

### vt_elderly_or_disabled_credit

**Label**: Vermont elderly or disabled credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Schedule R credit for the elderly and the disabled

**References**:
- https://tax.vermont.gov/individuals/personal-income-tax/tax-credits

### vt_income_tax

**Label**: Vermont income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### vt_income_tax_before_non_refundable_credits

**Label**: Vermont income tax before non-refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://casetext.com/statute/vermont-statutes/title-32-taxation-and-finance/chapter-151-income-taxes/subchapter-002-taxation-of-individuals-trusts-and-estates/section-5822-tax-on-income-of-individuals-estates-and-trusts
- https://tax.vermont.gov/sites/tax/files/documents/RateSched-2021.pdf#page=1
- https://tax.vermont.gov/sites/tax/files/documents/RateSched-2022.pdf#page=1

### vt_income_tax_before_refundable_credits

**Label**: Vermont income tax before refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### vt_low_income_cdcc

**Label**: Vermont low-income child care and dependent care credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.vermont.gov/sites/tax/files/documents/IN-112-2021.pdf#page=2https://law.justia.com/codes/vermont/2021/title-32/chapter-151/section-5828c/

### vt_low_income_cdcc_eligible

**Label**: Eligible for the Vermont low-income child care and dependent care credit
**Entity**: tax_unit
**Period**: year

**References**:
- https://tax.vermont.gov/sites/tax/files/documents/IN-112-2021.pdf#page=2https://law.justia.com/codes/vermont/2021/title-32/chapter-151/section-5828c/

### vt_medical_expense_deduction

**Label**: Vermont medical expense deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Vermont medical expenses deducted from taxable income.

**References**:
- https://legislature.vermont.gov/statutes/section/32/151/05811https://tax.vermont.gov/sites/tax/files/documents/IN-112%20Instr-2022.pdf#page=2

### vt_military_retirement_pay_exclusion

**Label**: Vermont military retirement income exclusion
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Vermont military retirement benefits exempt from Vermont taxation.

**References**:
- https://tax.vermont.gov/individuals/seniors-and-retirees
- https://legislature.vermont.gov/statutes/section/32/151/05830e

### vt_non_refundable_credits

**Label**: Vermont non-refundable tax credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### vt_normal_income_tax

**Label**: Vermont normal income tax before non-refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://casetext.com/statute/vermont-statutes/title-32-taxation-and-finance/chapter-151-income-taxes/subchapter-002-taxation-of-individuals-trusts-and-estates/section-5822-tax-on-income-of-individuals-estates-and-trusts
- https://tax.vermont.gov/sites/tax/files/documents/RateSched-2021.pdf#page=1
- https://tax.vermont.gov/sites/tax/files/documents/RateSched-2022.pdf#page=1

### vt_percentage_capital_gains_exclusion

**Label**: Vermont percentage capital gains exclusion
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

This can be selected to be subtracted from federal adjusted gross income in Vermont as percentage capital gains exclusion.

**References**:
- https://tax.vermont.gov/sites/tax/files/documents/IN-153-2022.pdf#page=1https://legislature.vermont.gov/statutes/section/32/151/05811https://tax.vermont.gov/sites/tax/files/documents/IN-153%20Instr-2022.pdf

### vt_personal_exemptions

**Label**: Vermont personal exemptions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.vermont.gov/sites/tax/files/documents/IN-111-2022.pdf

### vt_refundable_credits

**Label**: Vermont refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### vt_renter_credit

**Label**: Vermont renter credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/vermont/2022/title-32/chapter-154/section-6066/https://tax.vermont.gov/sites/tax/files/documents/Income%20Booklet-2022.pdf#page=35https://tax.vermont.gov/individuals/renter-credit/calculator-and-credit-amounts

### vt_renter_credit_countable_tax_exempt_ss

**Label**: Vermont renter credit countable tax exempt social security
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/vermont/2022/title-32/chapter-154/section-6061/
- https://tax.vermont.gov/sites/tax/files/documents/Income%20Booklet-2022.pdf#page=36

### vt_renter_credit_income

**Label**: Vermont renter credit income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://law.justia.com/codes/vermont/2022/title-32/chapter-154/section-6061/
- https://tax.vermont.gov/sites/tax/files/documents/Income%20Booklet-2022.pdf#page=36

### vt_retirement_income_exemption

**Label**: Vermont retirement income exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Vermont retirement benefits exempt from Vermont taxation.

**References**:
- https://legislature.vermont.gov/statutes/section/32/151/05811
- https://legislature.vermont.gov/statutes/section/32/151/05830ehttps://tax.vermont.gov/sites/tax/files/documents/IN-112%20Instr-2022.pdf#page=3
- https://tax.vermont.gov/individuals/seniors-and-retirees

### vt_retirement_income_exemption_eligible

**Label**: Vermont retirement income exemption eligibility status
**Entity**: tax_unit
**Period**: year

Vermont filers use below criteria to check whether the tax unit is eligible for vermont retirement income exemption.

**References**:
- https://legislature.vermont.gov/statutes/section/32/151/05811
- https://legislature.vermont.gov/statutes/section/32/151/05830ehttps://tax.vermont.gov/sites/tax/files/documents/IN-112%20Instr-2022.pdf#page=3
- https://tax.vermont.gov/individuals/seniors-and-retirees

### vt_standard_deduction

**Label**: Vermont standard deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.vermont.gov/sites/tax/files/documents/IN-111-2022.pdf
- http://legislature.vermont.gov/statutes/section/32/151/05811

### vt_subtractions

**Label**: Vermont subtractions
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Subtractions from Vermont adjusted gross income

**References**:
- https://tax.vermont.gov/sites/tax/files/documents/IN-112-2022.pdf#page=1
- https://legislature.vermont.gov/statutes/section/32/151/05811
- https://tax.vermont.gov/sites/tax/files/documents/IN-112%20Instr-2022.pdf

### vt_taxable_income

**Label**: Vermont taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

VT AGI less taxable income deductions and exemptions

**References**:
- https://tax.vermont.gov/sites/tax/files/documents/IN-111-2022.pdf

### vt_withheld_income_tax

**Label**: Vermont withheld income tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

### w2_wages_from_qualified_business

**Label**: W2 wages
**Entity**: person
**Period**: year
**Unit**: currency-USD

Share of wages paid by this person to employees as part of a pass-through qualified business or trade.

**References**:
- https://www.law.cornell.edu/uscode/text/26/199A#b_4

### wa_capital_gains_tax

**Label**: Washington capital gains tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### wa_income_tax

**Label**: Washington income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### wa_income_tax_before_refundable_credits

**Label**: Washington income tax before refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### wa_refundable_credits

**Label**: Washington refundable tax credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### wa_tanf_countable_resources

**Label**: Countable resources for Washington TANF
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### wa_tanf_resources_eligible

**Label**: Washington TANF resources eligible
**Entity**: spm_unit
**Period**: year

### wa_working_families_tax_credit

**Label**: Washington Working Families Tax Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://app.leg.wa.gov/RCW/default.aspx?cite=82.08.0206

### wagering_losses_deduction

**Label**: Wagering losses deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

Deduction from taxable income for gambling losses, capped at gambling winnings.

**References**:
- https://www.law.cornell.edu/uscode/text/26/165#d

### was_in_foster_care

**Label**: Person was in the a qualifying foster care institution
**Entity**: person
**Period**: year

### water_expense

**Label**: Water expense
**Entity**: spm_unit
**Period**: year
**Unit**: currency-USD

### weekly_hours_worked

**Label**: average weekly hours worked
**Entity**: person
**Period**: year
**Unit**: hour

Hours worked per week on average.

### weekly_hours_worked_before_lsr

**Label**: average weekly hours worked (before labor supply responses)
**Entity**: person
**Period**: year
**Unit**: hour

### weekly_hours_worked_behavioural_response

**Label**: behavioural response in weekly hours worked
**Entity**: person
**Period**: year
**Unit**: hour

### weekly_hours_worked_behavioural_response_income_elasticity

**Label**: behavioural response in weekly hours worked (income effect)
**Entity**: person
**Period**: year
**Unit**: hour

### weekly_hours_worked_behavioural_response_substitution_elasticity

**Label**: behavioural response in weekly hours worked (substitution effect)
**Entity**: person
**Period**: year
**Unit**: hour

### wi_additional_exemption

**Label**: Wisconsin additional exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.wi.gov/TaxForms2021/2021-Form1f.pdfhttps://www.revenue.wi.gov/TaxForms2021/2021-Form1-Inst.pdfhttps://www.revenue.wi.gov/TaxForms2022/2022-Form1f.pdfhttps://www.revenue.wi.gov/TaxForms2022/2022-Form1-Inst.pdfhttps://docs.legis.wisconsin.gov/misc/lfb/informational_papers/january_2023/0002_individual_income_tax_informational_paper_2.pdf

### wi_additions

**Label**: Wisconsin additions to federal adjusted gross income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.wi.gov/TaxForms2021/2021-ScheduleAD.pdfhttps://www.revenue.wi.gov/TaxForms2021/2021-ScheduleAD-inst.pdfhttps://www.revenue.wi.gov/TaxForms2022/2022-ScheduleADf.pdfhttps://www.revenue.wi.gov/TaxForms2022/2022-ScheduleAD-Inst.pdf

### wi_agi

**Label**: Wisconsin Adjusted Gross Income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.wi.gov/TaxForms2021/2021-Form1f.pdfhttps://www.revenue.wi.gov/TaxForms2021/2021-Form1-Inst.pdfhttps://www.revenue.wi.gov/TaxForms2022/2022-Form1f.pdfhttps://www.revenue.wi.gov/TaxForms2022/2022-Form1-Inst.pdf

### wi_base_exemption

**Label**: Wisconsin base exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.wi.gov/TaxForms2021/2021-Form1f.pdfhttps://www.revenue.wi.gov/TaxForms2021/2021-Form1-Inst.pdfhttps://www.revenue.wi.gov/TaxForms2022/2022-Form1f.pdfhttps://www.revenue.wi.gov/TaxForms2022/2022-Form1-Inst.pdfhttps://docs.legis.wisconsin.gov/misc/lfb/informational_papers/january_2023/0002_individual_income_tax_informational_paper_2.pdf

### wi_capital_gain_loss_addition

**Label**: WI capital gain/loss addition to federal adjusted gross income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.wi.gov/TaxForms2021/2021-ScheduleAD-inst.pdf#page=2https://www.revenue.wi.gov/TaxForms2022/2022-ScheduleAD-Inst.pdf#page=2

### wi_capital_gain_loss_subtraction

**Label**: Wisconsin capital gain/loss subtraction from federal AGI
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.wi.gov/TaxForms2021/2021-ScheduleWDf.pdf#page=2https://www.revenue.wi.gov/TaxForms2022/2022-ScheduleWDf.pdf#page=2

### wi_capital_loss

**Label**: Wisconsin capital loss (limited differently than US capital loss)
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.wi.gov/TaxForms2021/2021-ScheduleWDf.pdf#page=2https://www.revenue.wi.gov/TaxForms2022/2022-ScheduleWDf.pdf#page=2

### wi_childcare_expense_credit

**Label**: Wisconsin childcare expense credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.wi.gov/TaxForms2022/2022-Form1f.pdf#page=2https://www.revenue.wi.gov/TaxForms2022/2022-Form1-Inst.pdf#page=17https://docs.legis.wisconsin.gov/misc/lfb/informational_papers/january_2023/0002_individual_income_tax_informational_paper_2.pdf

### wi_childcare_expense_subtraction

**Label**: Wisconsin childcare expense subtraction from federal AGI
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.wi.gov/TaxForms2021/2021-ScheduleSB.pdfhttps://www.revenue.wi.gov/TaxForms2021/2021-ScheduleSB-inst.pdf#page=7

### wi_earned_income_credit

**Label**: Wisconsin earned income credit (WI EITC)
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.wi.gov/TaxForms2021/2021-Form1f.pdf#page=2https://www.revenue.wi.gov/TaxForms2021/2021-Form1-Inst.pdf#page=26https://www.revenue.wi.gov/TaxForms2022/2022-Form1f.pdf#page=2https://www.revenue.wi.gov/TaxForms2022/2022-Form1-Inst.pdf#page=26https://docs.legis.wisconsin.gov/misc/lfb/informational_papers/january_2023/0002_individual_income_tax_informational_paper_2.pdf

### wi_exemption

**Label**: Wisconsin exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.wi.gov/TaxForms2021/2021-Form1f.pdfhttps://www.revenue.wi.gov/TaxForms2021/2021-Form1-Inst.pdfhttps://www.revenue.wi.gov/TaxForms2022/2022-Form1f.pdfhttps://www.revenue.wi.gov/TaxForms2022/2022-Form1-Inst.pdfhttps://docs.legis.wisconsin.gov/misc/lfb/informational_papers/january_2023/0002_individual_income_tax_informational_paper_2.pdf

### wi_homestead_credit

**Label**: Wisconsin homestead credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.wi.gov/TaxForms2021/2021-Form1f.pdf#page=3https://www.revenue.wi.gov/TaxForms2021/2021-Form1-Inst.pdf#page=27https://www.revenue.wi.gov/TaxForms2022/2022-Form1f.pdf#page=3https://www.revenue.wi.gov/TaxForms2022/2022-Form1-Inst.pdf#page=28https://docs.legis.wisconsin.gov/misc/lfb/informational_papers/january_2023/0002_individual_income_tax_informational_paper_2.pdf

### wi_homestead_eligible

**Label**: Wisconsin homestead credit eligibility status
**Entity**: tax_unit
**Period**: year

**References**:
- https://docs.legis.wisconsin.gov/misc/lfb/informational_papers/january_2021/0013_homestead_tax_credit_informational_paper_13.pdf#page=7

### wi_homestead_income

**Label**: Wisconsin homestead credit income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.wi.gov/TaxForms2021/2021-ScheduleH.pdfhttps://www.revenue.wi.gov/TaxForms2022/2022-ScheduleH.pdf

### wi_homestead_property_tax

**Label**: Wisconsin homestead credit property tax amount
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.wi.gov/TaxForms2021/2021-ScheduleH.pdf#page=2https://www.revenue.wi.gov/TaxForms2022/2022-ScheduleH.pdf#page=2

### wi_income_subtractions

**Label**: Wisconsin subtractions from federal adjusted gross income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.wi.gov/TaxForms2021/2021-ScheduleSB.pdfhttps://www.revenue.wi.gov/TaxForms2021/2021-ScheduleSB-inst.pdfhttps://www.revenue.wi.gov/TaxForms2022/2022-ScheduleSBf.pdfhttps://www.revenue.wi.gov/TaxForms2022/2022-ScheduleSB-Inst.pdf

### wi_income_tax

**Label**: Wisconsin income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.wi.gov/TaxForms2021/2021-Form1f.pdf#page=3https://www.revenue.wi.gov/TaxForms2021/2021-Form1-Inst.pdf#page=31https://www.revenue.wi.gov/TaxForms2022/2022-Form1f.pdf#page=3https://www.revenue.wi.gov/TaxForms2022/2022-Form1-Inst.pdf#page=31

### wi_income_tax_before_credits

**Label**: Wisconsin income tax before credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.wi.gov/TaxForms2021/2021-Form1f.pdfhttps://www.revenue.wi.gov/TaxForms2021/2021-Form1-Inst.pdfhttps://www.revenue.wi.gov/TaxForms2022/2022-Form1f.pdfhttps://www.revenue.wi.gov/TaxForms2022/2022-Form1-Inst.pdfhttps://docs.legis.wisconsin.gov/misc/lfb/informational_papers/january_2023/0002_individual_income_tax_informational_paper_2.pdf

### wi_income_tax_before_refundable_credits

**Label**: Wisconsin income tax before refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.wi.gov/TaxForms2021/2021-Form1f.pdfhttps://www.revenue.wi.gov/TaxForms2021/2021-Form1-Inst.pdfhttps://www.revenue.wi.gov/TaxForms2022/2022-Form1f.pdfhttps://www.revenue.wi.gov/TaxForms2022/2022-Form1-Inst.pdfhttps://docs.legis.wisconsin.gov/misc/lfb/informational_papers/january_2023/0002_individual_income_tax_informational_paper_2.pdf

### wi_itemized_deduction_credit

**Label**: Wisconsin itemized deduction credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.wi.gov/TaxForms2021/2021-Form1f.pdf#page=4https://www.revenue.wi.gov/TaxForms2022/2022-Form1f.pdf#page=4https://docs.legis.wisconsin.gov/misc/lfb/informational_papers/january_2023/0002_individual_income_tax_informational_paper_2.pdf#page=19

### wi_married_couple_credit

**Label**: Wisconsin married couple credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.wi.gov/TaxForms2021/2021-Form1f.pdf#page=4https://www.revenue.wi.gov/TaxForms2021/2021-Form1-Inst.pdf#page=21https://www.revenue.wi.gov/TaxForms2022/2022-Form1f.pdf#page=4https://www.revenue.wi.gov/TaxForms2022/2022-Form1-Inst.pdf#page=21https://docs.legis.wisconsin.gov/misc/lfb/informational_papers/january_2023/0002_individual_income_tax_informational_paper_2.pdf

### wi_nonrefundable_credits

**Label**: Wisconsin nonrefundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.wi.gov/TaxForms2021/2021-Form1f.pdfhttps://www.revenue.wi.gov/TaxForms2021/2021-Form1-Inst.pdfhttps://www.revenue.wi.gov/TaxForms2022/2022-Form1f.pdfhttps://www.revenue.wi.gov/TaxForms2022/2022-Form1-Inst.pdfhttps://docs.legis.wisconsin.gov/misc/lfb/informational_papers/january_2023/0002_individual_income_tax_informational_paper_2.pdf

### wi_property_tax_credit

**Label**: Wisconsin property tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.wi.gov/TaxForms2021/2021-Form1f.pdf#page=2https://www.revenue.wi.gov/TaxForms2021/2021-Form1-Inst.pdf#page=17https://www.revenue.wi.gov/TaxForms2022/2022-Form1f.pdf#page=2https://www.revenue.wi.gov/TaxForms2022/2022-Form1-Inst.pdf#page=17https://docs.legis.wisconsin.gov/misc/lfb/informational_papers/january_2023/0002_individual_income_tax_informational_paper_2.pdf#page=19

### wi_refundable_credits

**Label**: Wisconsin refundable credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.wi.gov/TaxForms2021/2021-Form1f.pdfhttps://www.revenue.wi.gov/TaxForms2021/2021-Form1-Inst.pdfhttps://www.revenue.wi.gov/TaxForms2022/2022-Form1f.pdfhttps://www.revenue.wi.gov/TaxForms2022/2022-Form1-Inst.pdfhttps://docs.legis.wisconsin.gov/misc/lfb/informational_papers/january_2023/0002_individual_income_tax_informational_paper_2.pdf

### wi_retirement_income_subtraction

**Label**: Wisconsin retirement income subtraction from federal AGI
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.wi.gov/TaxForms2021/2021-ScheduleSB.pdfhttps://www.revenue.wi.gov/TaxForms2021/2021-ScheduleSB-inst.pdf#page=9https://www.revenue.wi.gov/TaxForms2022/2022-ScheduleSBf.pdfhttps://www.revenue.wi.gov/TaxForms2022/2022-ScheduleSB-Inst.pdf#page=7

### wi_retirement_income_subtraction_agi_eligible

**Label**: Wisconsin retirement income subtraction AGI eligibility
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.wi.gov/TaxForms2021/2021-ScheduleSB.pdfhttps://www.revenue.wi.gov/TaxForms2021/2021-ScheduleSB-inst.pdf#page=9https://www.revenue.wi.gov/TaxForms2022/2022-ScheduleSBf.pdfhttps://www.revenue.wi.gov/TaxForms2022/2022-ScheduleSB-Inst.pdf#page=7

### wi_standard_deduction

**Label**: Wisconsin standard deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.wi.gov/TaxForms2021/2021-Form1f.pdfhttps://www.revenue.wi.gov/TaxForms2021/2021-Form1-Inst.pdfhttps://www.revenue.wi.gov/TaxForms2022/2022-Form1f.pdfhttps://www.revenue.wi.gov/TaxForms2022/2022-Form1-Inst.pdfhttps://docs.legis.wisconsin.gov/misc/lfb/informational_papers/january_2023/0002_individual_income_tax_informational_paper_2.pdf

### wi_taxable_income

**Label**: Wisconsin taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.wi.gov/TaxForms2021/2021-Form1f.pdfhttps://www.revenue.wi.gov/TaxForms2021/2021-Form1-Inst.pdfhttps://www.revenue.wi.gov/TaxForms2022/2022-Form1f.pdfhttps://www.revenue.wi.gov/TaxForms2022/2022-Form1-Inst.pdfhttps://docs.legis.wisconsin.gov/misc/lfb/informational_papers/january_2023/0002_individual_income_tax_informational_paper_2.pdf

### wi_unemployment_compensation_subtraction

**Label**: Wisconsin unemployment compensation subtraction from federal AGI
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://www.revenue.wi.gov/TaxForms2021/2021-ScheduleSB-inst.pdf#page=2https://www.revenue.wi.gov/TaxForms2022/2022-ScheduleSB-Inst.pdf#page=1

### wi_withheld_income_tax

**Label**: Wisconsin withheld income tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

### wic

**Label**: WIC
**Entity**: person
**Period**: month
**Unit**: currency-USD

Benefit value for the Special Supplemental Nutrition Program for Women, Infants and Children (WIC)

**References**:
- https://fns-prod.azureedge.net/sites/default/files/resource-files/WICPC2018FoodPackage-Summary.pdf#page=2
- https://www.law.cornell.edu/cfr/text/7/246.7

### wic_category

**Label**: WIC demographic category
**Entity**: person
**Period**: year

Demographic category for the Special Supplemental Nutrition Program for Women, Infants and Children (WIC)

**References**:
- https://www.law.cornell.edu/uscode/text/42/1786#b

### wic_category_str

**Label**: WIC category (string)
**Entity**: person
**Period**: year

WIC category variable, stored as a string

### wic_fpg

**Label**: Pregnancy-adjusted poverty line for WIC
**Entity**: spm_unit
**Period**: month
**Unit**: currency-USD

Federal poverty guideline for WIC, with family size incremented by one for pregnant women

**References**:
- https://www.law.cornell.edu/uscode/text/42/1786#d_2_D

### workers_compensation

**Label**: worker's compensation
**Entity**: person
**Period**: year
**Unit**: currency-USD

### would_claim_wic

**Label**: Would claim WIC
**Entity**: person
**Period**: month

### wv_additions

**Label**: West Virginia additions to the adjusted gross income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### wv_agi

**Label**: West Virginia adjusted gross income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### wv_cdcc

**Label**: West Virginia Child and Dependent Care Credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://code.wvlegislature.gov/11-21-26/

### wv_gross_household_income

**Label**: West Virginia gross household income
**Entity**: tax_unit
**Period**: year

**References**:
- https://code.wvlegislature.gov/11-21-23/https://tax.wv.gov/Documents/TaxForms/2021/it140.pdf#page=13https://tax.wv.gov/Documents/PIT/2022/PersonalIncomeTaxFormsAndInstructions.2022.pdf#page=14

### wv_homestead_excess_property_tax_credit

**Label**: West Virginia homestead excess property tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://code.wvlegislature.gov/11-21-23/https://tax.wv.gov/Documents/TaxForms/2021/it140.pdf#page=13https://tax.wv.gov/Documents/PIT/2022/PersonalIncomeTaxFormsAndInstructions.2022.pdf#page=14

### wv_homestead_excess_property_tax_credit_eligible

**Label**: Eligible for the West Virginia homestead excess property tax credit
**Entity**: tax_unit
**Period**: year

**References**:
- https://code.wvlegislature.gov/11-21-23/https://tax.wv.gov/Documents/TaxForms/2021/it140.pdf#page=13https://tax.wv.gov/Documents/PIT/2022/PersonalIncomeTaxFormsAndInstructions.2022.pdf#page=14

### wv_homestead_exemption

**Label**: West Virginia homestead exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://code.wvlegislature.gov/11-21-21/

### wv_income_tax

**Label**: West Virginia income tax
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### wv_income_tax_before_non_refundable_credits

**Label**: West Virginia income tax before non-refundable tax credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### wv_income_tax_before_refundable_credits

**Label**: West Virginia income tax before refundable tax credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### wv_low_income_earned_income_exclusion

**Label**: West Virginia low-income earned income exclusion
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://code.wvlegislature.gov/11-21-10/https://tax.wv.gov/Documents/TaxForms/2021/it140.pdf#page=20https://tax.wv.gov/Documents/PIT/2022/PersonalIncomeTaxFormsAndInstructions.2022.pdf#page=27

### wv_low_income_earned_income_exclusion_eligible

**Label**: Eligible for the West Virginia low-income earned income exclusion
**Entity**: tax_unit
**Period**: year

**References**:
- https://code.wvlegislature.gov/11-21-10/https://tax.wv.gov/Documents/TaxForms/2021/it140.pdf#page=20https://tax.wv.gov/Documents/PIT/2022/PersonalIncomeTaxFormsAndInstructions.2022.pdf#page=27

### wv_low_income_family_tax_credit

**Label**: West Virginia low-income family tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### wv_low_income_family_tax_credit_agi

**Label**: Adjusted gross income for the West Virginia low-income family tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://code.wvlegislature.gov/11-21-12/

### wv_low_income_family_tax_credit_eligible

**Label**: Eligible for the West Virginia low-income family tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://code.wvlegislature.gov/11-21-22/

### wv_low_income_family_tax_credit_fpg

**Label**: Federal poverty guidelines for the West Virginia low-income family tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### wv_non_refundable_credits

**Label**: West Virginia refundable tax credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### wv_personal_exemption

**Label**: West Virginia personal exemption
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://code.wvlegislature.gov/11-21/

### wv_public_pension_subtraction

**Label**: West Virginia public pension subtraction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://code.wvlegislature.gov/11-21-12/

### wv_public_pension_subtraction_person

**Label**: West Virginia public pension subtraction for each person
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://code.wvlegislature.gov/11-21-12/

### wv_refundable_credits

**Label**: West Virginia refundable tax credits
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### wv_sctc

**Label**: West Virginia senior citizens tax credit
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://code.wvlegislature.gov/11-21-21/

### wv_sctc_eligible

**Label**: Eligible for the West Virginia senior citizens tax credit
**Entity**: tax_unit
**Period**: year

**References**:
- https://code.wvlegislature.gov/11-21-21/https://tax.wv.gov/Documents/TaxForms/2021/it140.pdf#page=27 https://tax.wv.gov/Documents/PIT/2022/PersonalIncomeTaxFormsAndInstructions.2022.pdf#page=35

### wv_senior_citizen_disability_deduction

**Label**: West Virginia senior citizen or disability deduction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### wv_senior_citizen_disability_deduction_eligible_person

**Label**: Eligible person for the West Virginia senior citizen or disability deduction
**Entity**: person
**Period**: year

**References**:
- https://code.wvlegislature.gov/11-21-12/

### wv_senior_citizen_disability_deduction_person

**Label**: West Virginia senior citizen or disability deduction for each person
**Entity**: person
**Period**: year
**Unit**: currency-USD

### wv_senior_citizen_disability_deduction_total_modifications

**Label**: West Virginia total modifications for the senior citizen or disability deduction
**Entity**: person
**Period**: year
**Unit**: currency-USD

### wv_social_security_benefits_subtraction

**Label**: West Virginia social security benefits subtraction
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.wv.gov/Documents/TaxForms/2020/it140.booklet.pdf#page=24
- https://tax.wv.gov/Documents/TaxForms/2021/it140.booklet.pdf#page=24
- https://tax.wv.gov/Documents/PIT/2022/PersonalIncomeTaxFormsAndInstructions.2022.pdf#page=25
- https://code.wvlegislature.gov/11-21-12/

### wv_social_security_benefits_subtraction_eligible

**Label**: Eligible for the West Virginia social security benefits subtraction
**Entity**: tax_unit
**Period**: year

**References**:
- https://tax.wv.gov/Documents/TaxForms/2020/it140.booklet.pdf#page=24
- https://tax.wv.gov/Documents/TaxForms/2021/it140.booklet.pdf#page=24
- https://tax.wv.gov/Documents/PIT/2022/PersonalIncomeTaxFormsAndInstructions.2022.pdf#page=25
- https://code.wvlegislature.gov/11-21-12/

### wv_social_security_benefits_subtraction_person

**Label**: West Virginia social security benefits subtraction for each person
**Entity**: person
**Period**: year
**Unit**: currency-USD

**References**:
- https://tax.wv.gov/Documents/TaxForms/2020/it140.booklet.pdf#page=24
- https://tax.wv.gov/Documents/TaxForms/2021/it140.booklet.pdf#page=24
- https://tax.wv.gov/Documents/PIT/2022/PersonalIncomeTaxFormsAndInstructions.2022.pdf#page=25
- https://code.wvlegislature.gov/11-21-12/

### wv_subtractions

**Label**: West Virginia subtractions from the adjusted gross income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

### wv_taxable_income

**Label**: West Virginia taxable income
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://code.wvlegislature.gov/11-21-4E/

### wv_taxable_property_value

**Label**: West Virginia taxable property value
**Entity**: tax_unit
**Period**: year
**Unit**: currency-USD

**References**:
- https://code.wvlegislature.gov/11-21-21/

### wv_withheld_income_tax

**Label**: West Virginia withheld income tax
**Entity**: person
**Period**: year
**Unit**: currency-USD

### year_deceased

**Label**: Year in which the person deceased
**Entity**: person
**Period**: year

### year_of_retirement

**Label**: Year of retirement
**Entity**: person
**Period**: year

### years_in_military

**Label**: Years served in military
**Entity**: person
**Period**: year

### zip_code

**Label**: ZIP code
**Entity**: household
**Period**: year
