from policyengine_us.model_api import *


class mt_eligible_medical_insurance_premiums(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Montana medical insurance premiums deductible in full"
    documentation = (
        "Each person's medical insurance premiums that Montana's Itemized "
        "Deductions Schedule line 2 deducts in full, before the 2024 switch "
        "to federal itemized deductions: the premiums counted as federal "
        "medical expenses, including Medicare Part B, less the premiums "
        "deducted as the self-employed health insurance deduction in "
        "Montana AGI. Pre-tax premiums are excluded because they are not "
        "counted as federal medical expenses."
    )
    reference = (
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2/2022_Montana_Individual_Income_Tax_Return_Form_2.pdf#page=7",
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2022_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=33",
        # MCA 2021 § 15-30-2131(1)(a)(iii) and (1)(g)(i)
        "https://mca.legmt.gov/bills/2022/mca/title_0150/chapter_0300/part_0210/section_0310/0150-0300-0210-0310.html",
    )
    unit = USD
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        premiums = person("medical_expense_health_insurance_premiums", period)
        # Premiums deducted in determining Montana AGI do not qualify, such as
        # the self-employed health insurance deduction (Schedule 1, line 17).
        deducted_in_agi = person("self_employed_health_insurance_ald_person", period)
        return max_(0, premiums - deducted_in_agi)
