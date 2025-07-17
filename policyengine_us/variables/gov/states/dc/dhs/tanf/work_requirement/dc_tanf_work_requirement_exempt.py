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
        # Person older than 60 can exempt
        elderly = age > p.elderly_age_threshold
        # Pregnant person can exempt
        is_pregnant = person("is_pregnant", period)
        # Eligible child can exempt
        eligible_child = person("dc_pap_eligible_child", period)
        # Single parent can exempt with infant less than 1 years old can exempt
        filing_status = person.tax_unit("filing_status", period)
        joint = filing_status == filing_status.possible_values.JOINT
        has_infant = person.spm_unit.any(age < p.infant_age_threshold)
        is_head = person("is_tax_unit_head", period)
        single_parent_exempt = ~joint & has_infant & is_head
        # The household can be exempted from working if there is an incapable of self care person
        is_incapable_of_self_care = person("is_incapable_of_self_care", period)
        has_incapable_person = person.spm_unit.any(is_incapable_of_self_care)

        return (
            elderly
            | is_pregnant
            | eligible_child
            | single_parent_exempt
            | has_incapable_person
        )
