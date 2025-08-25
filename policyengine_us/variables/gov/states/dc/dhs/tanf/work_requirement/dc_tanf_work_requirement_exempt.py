from policyengine_us.model_api import *


class dc_tanf_work_requirement_exempt(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Exempted from working requirement for DC Temporary Assistance for Needy Families (TANF)"
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.19g"
    )
    defined_for = StateCode.DC

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.dc.dhs.tanf.work_requirement.work_exempted
        age = person("monthly_age", period)
        # (1) Eligible child who are not the head of an assistance unit can exempt
        eligible_child = person("dc_pap_eligible_child", period)
        # (2) Single parent works more than 30 hours per week (modeled in work requirements)
        # (3) Two-parent work more than 35 hours per week (modeled in work requirements)
        # (4) Single parent can exempt with infant less than 1 years old can exempt
        filing_status = person.tax_unit("filing_status", period)
        joint = filing_status == filing_status.possible_values.JOINT
        has_infant = person.spm_unit.any(age < p.infant_age_threshold)
        is_head = person("is_tax_unit_head", period)
        single_parent_exempt = ~joint & has_infant & is_head
        # (5) Person older than 60 can exempt
        elderly = age > p.elderly_age_threshold
        # (6) Individuals who are enrolled in post-secondary educational institutions
        is_college_student = person("is_full_time_college_student", period)

        return (
            eligible_child
            | single_parent_exempt
            | elderly
            | is_college_student
        )
