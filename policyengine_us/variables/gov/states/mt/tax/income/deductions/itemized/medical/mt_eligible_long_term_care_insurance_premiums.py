from policyengine_us.model_api import *


class mt_eligible_long_term_care_insurance_premiums(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Montana long-term care insurance premiums deductible in full"
    documentation = (
        "A person's long-term care insurance premiums that Montana's "
        "2021-2023 Itemized Deductions Schedule line 3 deducts in full, "
        "without the federal age-based limit, less any of those premiums the "
        "person deducted through the self-employed health insurance "
        "deduction. That deduction is applied first to the medical insurance "
        "premiums on line 2 and the remainder to these premiums; lines 2 and "
        "3 are both deducted in full, so the order does not change the total."
    )
    reference = (
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2/2022_Montana_Individual_Income_Tax_Return_Form_2.pdf#page=7",
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2022_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=33",
        # MCA 2021 § 15-30-2131(1)(a)(iv) and (1)(g)(ii)
        "https://mca.legmt.gov/bills/2022/mca/title_0150/chapter_0300/part_0210/section_0310/0150-0300-0210-0310.html",
        # 26 U.S.C. 162(l)(2)(C): eligible long-term care premiums can be part
        # of the self-employed health insurance deduction.
        "https://www.law.cornell.edu/uscode/text/26/162#l_2_C",
    )
    unit = USD
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        premiums = person("long_term_health_insurance_premiums", period)
        deduction = max_(0, person("self_employed_health_insurance_ald_person", period))
        used_on_line_2 = person(
            "self_employed_health_insurance_ald_excluded_premiums", period
        )
        return max_(0, premiums - (deduction - used_on_line_2))
