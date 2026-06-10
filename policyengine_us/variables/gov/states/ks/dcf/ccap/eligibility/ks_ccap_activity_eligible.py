from policyengine_us.model_api import *


class ks_ccap_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Kansas CCAP based on activity requirements"
    definition_period = MONTH
    defined_for = StateCode.KS
    reference = "https://content.dcf.ks.gov/ees/keesm/Current/keesm2810.htm"

    def formula(spm_unit, period, parameters):
        # KEESM 2820: non-TANF caretakers must maintain employment of at least
        # 20 hours per week. We use is_full_time_student as a proxy for the
        # post-secondary education-while-employed pathway. We don't model the
        # federal minimum-wage earnings floor, nor the other need pathways at the
        # moment: the unemployed food assistance work program participant and the
        # "children need child care to prevent abuse and/or neglect" pathways
        # (both exempt from the financial-need test under KEESM 7540), nor
        # teen-parent education, crisis services, Early Head Start partnership,
        # or foster care.
        p = parameters(period).gov.states.ks.dcf.ccap.eligibility
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        # Use the pre-labor-supply-response hours to avoid a circular dependency
        # in reform/microsimulation runs.
        hours_worked = person("weekly_hours_worked_before_lsr", period.this_year)
        is_student = person("is_full_time_student", period.this_year)
        individually_eligible = (hours_worked >= p.activity_hours) | is_student
        has_caretaker = spm_unit.sum(is_head_or_spouse) > 0
        no_ineligible_caretaker = (
            spm_unit.sum(is_head_or_spouse & ~individually_eligible) == 0
        )
        non_tanf_eligible = has_caretaker & no_ineligible_caretaker
        # KEESM 2820: TANF work-program participants have no minimum-hours test.
        is_tanf = spm_unit("is_tanf_enrolled", period)
        return is_tanf | non_tanf_eligible
