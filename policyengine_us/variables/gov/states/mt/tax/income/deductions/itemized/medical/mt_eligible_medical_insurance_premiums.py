from policyengine_us.model_api import *


class mt_eligible_medical_insurance_premiums(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Montana medical insurance premiums deductible in full"
    documentation = (
        "A person's medical insurance premiums that Montana's 2021-2023 "
        "Itemized Deductions Schedule line 2 deducts in full: the premiums "
        "counted as federal medical expenses, including Medicare Part B, "
        "less the premiums that person deducted through the self-employed "
        "health insurance deduction. For the head and spouse that deduction "
        "is part of Montana AGI; a dependent takes it on the dependent's own "
        "return, so those premiums were not paid by the filer. Pre-tax "
        "premiums are a separate input that never enters "
        "medical_expense_health_insurance_premiums. Premium inputs use payer "
        "attribution: each person reports the premiums that person paid."
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
        # Premiums deducted in determining Montana AGI do not qualify: the
        # self-employed health insurance deduction (Schedule 1, line 17).
        deducted = person("self_employed_health_insurance_ald_excluded_premiums", period)
        return premiums - deducted
