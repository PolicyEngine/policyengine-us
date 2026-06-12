from policyengine_us.model_api import *


class mi_ccap_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Michigan CDC based on need reasons"
    definition_period = MONTH
    defined_for = StateCode.MI
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/BP/Public/BEM/703.pdf#page=5"
    )

    def formula(spm_unit, period, parameters):
        # BEM 703 p.4-14: each parent/substitute-parent (P/SP) must have a
        # valid need reason; in a two-parent household both must. We model
        # employment/self-employment (hours worked), approved activity and
        # high-school completion (full-time student), and family preservation
        # (protective services). We use hours before labor supply responses to
        # avoid a circular dependency with the labor supply model.
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        hours_worked = person("weekly_hours_worked_before_lsr", period.this_year)
        is_employed = hours_worked > 0
        is_student = person("is_full_time_student", period.this_year)
        needs_protective_services = person(
            "receives_or_needs_protective_services", period.this_year
        )
        has_need_reason = is_employed | is_student | needs_protective_services
        # Every P/SP must individually have a need reason.
        return spm_unit.sum(is_head_or_spouse & ~has_need_reason) == 0
