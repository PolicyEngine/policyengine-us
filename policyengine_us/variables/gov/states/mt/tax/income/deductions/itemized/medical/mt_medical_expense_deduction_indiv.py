from policyengine_us.model_api import *


class mt_medical_expense_deduction_indiv(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = (
        "Montana medical expense deduction when married couples are filing separately"
    )
    reference = (
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2/2022_Montana_Individual_Income_Tax_Return_Form_2.pdf#page=7",
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2022_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=32",
        # MCA 2021 § 15-30-2131(1)(a) and (1)(g)
        "https://mca.legmt.gov/bills/2022/mca/title_0150/chapter_0300/part_0210/section_0310/0150-0300-0210-0310.html",
    )
    unit = USD
    # Separate filing on the same form, and with it the Itemized Deductions
    # Schedule, ended after 2023.
    defined_for = "mt_married_filing_separately_on_same_return_eligible"

    def formula(person, period, parameters):
        floor = parameters(period).gov.irs.deductions.itemized.medical.floor
        # Itemized Deductions Schedule line 1 takes medical and dental expenses
        # other than the insurance premiums deducted in full on lines 2 and 3.
        expense = person("other_medical_expenses", period)
        # Law does not define Montana AGI as the cap.
        # Tax form points to page 1, line 14, which is Montana AGI.
        montana_agi = person("mt_agi_indiv", period)
        floored_expense = max_(0, expense - floor * montana_agi)
        # Line 2: medical insurance premiums not deducted elsewhere.
        # Line 3: long-term care insurance premiums, without the federal
        # age-based limit.
        premiums = add(
            person,
            period,
            [
                "mt_eligible_medical_insurance_premiums",
                "long_term_health_insurance_premiums",
            ],
        )
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return is_head_or_spouse * (floored_expense + premiums)
