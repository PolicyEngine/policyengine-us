from openfisca_us.model_api import *

# Line 5. OTHER ADDITIONS TO INCOME. If one or more of these apply to you, enter the total amount on line 5 and identify each item using the code letter: CODE LETTER

# a. Part-year residents: losses or adjustments to federal income that were realized or paid when you were a nonresident of Maryland.

# b. Net additions to income from pass-through entities not attributable to decoupling.
class md_pass_through_not_attributable_to_decoupling(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD Pass-Through Not Attributable to Decoupling"
    documentation = "Net additions to income from pass-through entities not attributable to decoupling"
    unit = USD
    definition_period = YEAR


# c. Net additions to income from a trust as reported by the fiduciary.
class md_trust_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD Trust Income"
    documentation = (
        "Net additions to income from a trust as reported by the fiduciary"
    )
    unit = USD
    definition_period = YEAR


# d. S corporation taxes included on lines 13 and 14 of Form 502CR, Part A, Tax Credits for Income Taxes Paid to Other States and Localities. (See instructions for Part A of Form 502CR.)
class md_s_corp_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD S Corporation Tax Credit"
    documentation = "S corporation taxes included on lines 13 and 14 of Form 502CR, Part A, Tax Credits for Income Taxes Paid to Other States and Localities. (See instructions for Part A of Form 502CR.)"
    unit = USD
    definition_period = YEAR


# e. Total amount of credit(s) claimed in the current tax year to 6 the extent allowed on Form 500CR for the following Business Tax Credits: Enterprise Zone Tax Credit, Maryland Disability Employment Tax Credit, Small Business Research & Development Tax Credit, Maryland Employer Security Clearance Costs Tax Credit (do not include Small Business First-Year Leasing Costs Tax Credit), and Endowments of Maryland Historically Black Colleges and Universities Tax Credit. In addition, include any amount deducted as a donation to the extent that the amount of the donation is included in an application for the Endow Maryland Tax Credit and/or Endowments of Maryland Historically Black Colleges and Universities Tax Credit on Form 500CR or 502CR.


# f. Oil percentage depletion allowance claimed under IRC Section 613.
class md_oil_percentage_depletion_allowance(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD Oil Percentage Depletion Allowance"
    documentation = (
        "Oil percentage depletion allowance claimed under IRC Section 613"
    )
    unit = USD
    definition_period = YEAR


# g. Income exempt from federal tax by federal law or treaty that is not exempt from Maryland tax.
class md_income_exempt_from_federal_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD Income Exempt From Federal Tax"
    documentation = "Income exempt from federal tax by federal law or treaty that is not exempt from Maryland tax"
    unit = USD
    definition_period = YEAR


# h. Net operating loss deduction to the extent of a double benefit. See Administrative Release 18 at www.marylandtaxes.gov.
class md_net_operating_loss_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD Net Operating Loss Deduction"
    documentation = "Net operating loss deduction to the extent of a double benefit. See Administrative Release 18 at www.marylandtaxes.gov."
    unit = USD
    definition_period = YEAR


# i. Taxable tax preference items from line 5 of Form 502TP. The items of tax preference are defined in IRC Section 57. If the total of your tax preference items is more than $10,000 ($20,000 for married taxpayers filing joint returns) you must complete and attach Form 502TP, whether or not you are required to file federal Form 6251 (Alternative Minimum Tax) with your federal Form 1040.
class md_taxable_tax_preference_items(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD Taxable Tax Preference Items"
    documentation = "Taxable tax preference items from line 5 of Form 502TP. The items of tax preference are defined in IRC Section 57. If the total of your tax preference items is more than $10,000 ($20,000 for married taxpayers filing joint returns) you must complete and attach Form 502TP, whether or not you are required to file federal Form 6251 (Alternative Minimum Tax) with your federal Form 1040."
    unit = USD
    definition_period = YEAR


# j. Amount deducted for federal income tax purposes for expenses attributable to operating a family day care home or a child care center in Maryland without having the registration or license required by the Family Law Article.
class md_unlicensed_child_care_expenses(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD Unlicensed Child Care Expenses"
    documentation = "Amount deducted for federal income tax purposes for expenses attributable to operating a family day care home or a child care center in Maryland without having the registration or license required by the Family Law Article."
    unit = USD
    definition_period = YEAR


# k. Any refunds of advanced tuition payments made under the Maryland Prepaid College Trust, to the extent the payments were subtracted from federal adjusted gross income and were not used for qualified higher education expenses, and any refunds of contributions made under the Maryland College Investment Plan, to the extent the contributions were subtracted from federal adjusted gross income and were not used for qualified higher education expenses. See Administrative Release 32.
class md_refunds_of_advanced_tuition_payments(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD refunds of advanced tuition payments"
    documentation = "Any refunds of advanced tuition payments made under the Maryland Prepaid College Trust, to the extent the payments were subtracted from federal adjusted gross income and were not used for qualified higher education expenses, and any refunds of contributions made under the Maryland College Investment Plan, to the extent the contributions were subtracted from federal adjusted gross income and were not used for qualified higher education expenses. See Administrative Release 32."
    unit = USD
    definition_period = YEAR


# l. Net addition modification to Maryland taxable income when claiming the federal depreciation allowances from which the State of Maryland has decoupled. Complete and attach Form 500DM. See Administrative Release 38.
class md_decoupled_depreciation_allowances(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD decoupled depreciation allowances"
    documentation = "Net addition modification to Maryland taxable income when claiming the federal depreciation allowances from which the State of Maryland has decoupled. Complete and attach Form 500DM. See Administrative Release 38."
    unit = USD
    definition_period = YEAR


# m. Net addition modification to Maryland taxable income when the federal special 2-year carryback (farming loss only) period was used for a net operating loss under federal law compared to Maryland taxable income without regard to federal provisions. Complete and attach Form 500DM.
class md_farming_loss_carryback(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD farming loss carryback"
    documentation = "Net addition modification to Maryland taxable income when the federal special 2-year carryback (farming loss only) period was used for a net operating loss under federal law compared to Maryland taxable income without regard to federal provisions. Complete and attach Form 500DM."
    unit = USD
    definition_period = YEAR


# n. Amount deducted on your federal income tax return for domestic production activities.
class md_domestic_production_activities(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD domestic production activities"
    documentation = "Amount deducted on your federal income tax return for domestic production activities."
    unit = USD
    definition_period = YEAR


# o. Amount deducted on your federal income tax return for tuition and related expenses. Do not include adjustments to income for Educator Expenses or Student Loan Interest deduction.
class md_tuition_and_related_expenses(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD tuition and related expenses"
    documentation = "Amount deducted on your federal income tax return for tuition and related expenses. Do not include adjustments to income for Educator Expenses or Student Loan Interest deduction."
    unit = USD
    definition_period = YEAR


# p. Any refunds received by an ABLE account contributor under the Maryland ABLE Program or any distribution received by an ABLE account holder, to the extent the distribution was not used for the benefit of the designated beneficiary for qualified disability expense, that were subtracted from federal adjusted gross income.
class md_able_refunds(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD able refunds"
    documentation = "Any refunds received by an ABLE account contributor under the Maryland ABLE Program or any distribution received by an ABLE account holder, to the extent the distribution was not used for the benefit of the designated beneficiary for qualified disability expense, that were subtracted from federal adjusted gross income."
    unit = USD
    definition_period = YEAR


# q. If you sold or exchanged a property for which you claimed a subtraction modification under Senate Bill 367 (Chapter 231, Acts of 2017) or Senate Bill 580/House Bill 600 (Chapter 544 and Chapter 545, Acts of 2012), enter the amount of the difference between your federal adjusted gross income as reportable under the federal Mortgage Forgiveness Debt Relief Act of 2007 and your federal adjusted gross income as claimed in the taxable year.
class md_property_subtraction_modification(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD property subtraction modification"
    documentation = "If you sold or exchanged a property for which you claimed a subtraction modification under Senate Bill 367 (Chapter 231, Acts of 2017) or Senate Bill 580/House Bill 600 (Chapter 544 and Chapter 545, Acts of 2012), enter the amount of the difference between your federal adjusted gross income as reportable under the federal Mortgage Forgiveness Debt Relief Act of 2007 and your federal adjusted gross income as claimed in the taxable year."
    unit = USD
    definition_period = YEAR


# r. Members of pass-through entities that elected to make payments attributable to members’ share of the pass-through entity taxable income. If you received a credit for tax paid by the pass-through entity on your distributive or pro rata share of income on Maryland Schedule K-1 (510), part D enter the amount of the credit claimed on Form 502CR part CC line 9.
class md_pass_through_member_share(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD pass-through member share"
    documentation = "Members of pass-through entities that elected to make payments attributable to members’ share of the pass-through entity taxable income. If you received a credit for tax paid by the pass-through entity on your distributive or pro rata share of income on Maryland Schedule K-1 (510), part D enter the amount of the credit claimed on Form 502CR part CC line 9."
    unit = USD
    definition_period = YEAR


# s. Amount of funds withdrawn from a first-time homebuyer savings account for a purpose other than eligible costs for the purchase of a home in the State. However, do not include any amount withdrawn by the account holder(s) for the purpose of rolling over earnings and principal into another designated account or a withdrawal protected by an account holder(s)’ bankruptcy filing. An account holder(s) must use the funds in the designated account within 15 years from the date on which the account was established. Include the amount of any funds remaining after the end of the 15-year period for which the firsttime home-buyer subtraction was claimed in a prior year and which were not withdrawn and applied to eligible costs related the purchase of a home by the account holder(s). The account holder(s) may be subject to a penalty of 10% of the amount withdrawn (see Instruction 22).
class md_first_time_homebuyer_savings_withdrawn(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD first time homebuyer savings withdrawn"
    documentation = "Amount of funds withdrawn from a first-time homebuyer savings account for a purpose other than eligible costs for the purchase of a home in the State. However, do not include any amount withdrawn by the account holder(s) for the purpose of rolling over earnings and principal into another designated account or a withdrawal protected by an account holder(s)’ bankruptcy filing. An account holder(s) must use the funds in the designated account within 15 years from the date on which the account was established. Include the amount of any funds remaining after the end of the 15-year period for which the firsttime home-buyer subtraction was claimed in a prior year and which were not withdrawn and applied to eligible costs related the purchase of a home by the account holder(s). The account holder(s) may be subject to a penalty of 10% of the amount withdrawn (see Instruction 22)."
    unit = USD
    definition_period = YEAR


# cd. Net addition modification to Maryland taxable income resulting from the federal deferral of income arising from business indebtedness discharged by reacquisition of a debt instrument. See Form 500DM and Administrative Release 38.
class md_deferred_income_by_debt_reacquisition(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD deferred income by debt reacquisition"
    documentation = "Net addition modification to Maryland taxable income resulting from the federal deferral of income arising from business indebtedness discharged by reacquisition of a debt instrument. See Form 500DM and Administrative Release 38."
    unit = USD
    definition_period = YEAR


# dm. Net addition modification from multiple decoupling provisions. See the table at the bottom of Form 500DM for the line numbers and code letters to use.
class md_multiple_decoupling_modification(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD multiple decoupling modification"
    documentation = "Net addition modification from multiple decoupling provisions. See the table at the bottom of Form 500DM for the line numbers and code letters to use."
    unit = USD
    definition_period = YEAR


# dp. Net addition decoupling modification from a pass-through entity. See Form 500DM.
class md_pass_through_entity_decoupling_modification(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD pass-through entity decoupling modification"
    documentation = "Net addition decoupling modification from a pass-through entity. See Form 500DM."
    unit = USD
    definition_period = YEAR


"""
git mv openfisca_us/variables/gov/states/md/tax/income/subtractions/md_child_dependent_care_expense_deduction.py openfisca_us/variables/gov/states/md/tax/income/subtractions/md_child_dependent_care_deduction.py

"""
