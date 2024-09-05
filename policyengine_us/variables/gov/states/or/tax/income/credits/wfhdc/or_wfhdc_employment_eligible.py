from policyengine_us.model_api import *


class or_wfhdc_employment_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Employment eligible for the Oregon working family household and dependent care credit"
    documentation = "Oregon Working Family Household and Dependent Care Credit household eligibility"
    definition_period = YEAR
    reference = (
        "https://www.oregon.gov/dor/forms/FormsPubs/schedule-or-wfhdc-inst_101-195-1_2022.pdf#pahe=1",
        "https://law.justia.com/codes/oregon/2021/volume-08/chapter-315/section-315-264/",
    )
    defined_for = StateCode.OR

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        # 1) you are working
        earned_income = person("earned_income", period)
        head = person("is_tax_unit_head", period)
        earned_income_eligible = tax_unit.any(head * earned_income) > 0
        # 2)  you are single and you attended school (full-time or part-time)
        filing_status = tax_unit("filing_status", period)
        attend_school = tax_unit.any(head & person("is_in_k12_school", period))
        single_student = (
            filing_status == filing_status.possible_values.SINGLE
        ) & attend_school
        # 3) you are married filing jointly and one spouse attended school (full-time) or was disabled
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        is_full_time_student = person("is_full_time_student", period)
        married_eligible = tax_unit.any(
            is_full_time_student & is_head_or_spouse
        )
        joint_head_or_spouse_student = (
            filing_status == filing_status.possible_values.JOINT
        ) & married_eligible

        return (
            earned_income_eligible
            | single_student
            | joint_head_or_spouse_student
        )
