from policyengine_us.model_api import *


class ri_ccap_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Rhode Island CCAP based on activity requirements"
    definition_period = MONTH
    defined_for = StateCode.RI
    reference = "https://rules.sos.ri.gov/regulations/part/218-20-00-4#4.4"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ri.dhs.ccap.activity_requirements
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        hours_worked = person("weekly_hours_worked", period.this_year)
        meets_work_requirement = hours_worked >= p.weekly_hours
        is_student = person("is_full_time_student", period.this_year)
        individually_eligible = meets_work_requirement | is_student
        return spm_unit.sum(is_head_or_spouse & ~individually_eligible) == 0
