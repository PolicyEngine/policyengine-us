from policyengine_us.model_api import *


class mt_medical_expense_deduction_indiv(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = (
        "Montana medical expense deduction when married couples are filing separately"
    )
    reference = (
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2023_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=36",
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2/2022_Montana_Individual_Income_Tax_Return_Form_2.pdf#page=7",
        # PDF pages 32-33
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2022_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=32",
        # MCA 2021 § 15-30-2131(1)(a) and (1)(g)
        "https://mca.legmt.gov/bills/2022/mca/title_0150/chapter_0300/part_0210/section_0310/0150-0300-0210-0310.html",
    )
    unit = USD
    defined_for = "mt_married_filing_separately_on_same_return_eligible"
    documentation = (
        "Each spouse's medical deduction when filing separately on the same "
        "form. While the Itemized Deductions Schedule applies (2021-2023), "
        "line 1 floors the spouse's medical and dental expenses other than "
        "premiums at 7.5% of their Montana AGI, and lines 2 and 3 add their "
        "medical and long-term care insurance premiums in full, net of their "
        "self-employed health insurance deduction. If a reform allows "
        "separate filing in a later year, the premiums net of that deduction "
        "stay under the floor with the other expenses. Premium inputs use "
        "payer attribution: report all premiums paid by a person on that "
        "person, including family coverage regardless of the covered "
        "beneficiary."
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.deductions.itemized
        floor = parameters(period).gov.irs.deductions.itemized.medical.floor
        expense = person("other_medical_expenses", period)
        # Law does not define Montana AGI as the cap.
        # Tax form points to page 1, line 14, which is Montana AGI.
        medical_floor = floor * person("mt_agi_indiv", period)
        premiums = person("mt_eligible_medical_insurance_premiums", period)
        if p.state_specific_deduction_applies:
            # Line 1 floors expenses other than premiums; lines 2 and 3
            # deduct the premiums in full.
            long_term_care_premiums = person(
                "mt_eligible_long_term_care_insurance_premiums", period
            )
            deduction = (
                max_(0, expense - medical_floor) + premiums + long_term_care_premiums
            )
        else:
            deduction = max_(0, premiums + expense - medical_floor)
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return is_head_or_spouse * deduction
