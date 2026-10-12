from policyengine_us.model_api import *


class tx_ccs_work_requirement_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Texas CCS work requirement eligible"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/texas/40-Tex-Admin-Code-SS-809-56"
    )
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.tx.twc.ccs.work_requirements

        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        is_exempt = person("tx_ccs_work_exempt", period)
        work_hours = person("weekly_hours_worked", period.this_year)

        # Count non-exempt parents and calculate their total work hours
        is_non_exempt_parent = is_head_or_spouse & ~is_exempt
        num_non_exempt_parents = spm_unit.sum(is_non_exempt_parent)
        total_work_hours = spm_unit.sum(where(is_non_exempt_parent, work_hours, 0))

        # Determine work hours requirement based on non-exempt parents
        # If 0-1 non-exempt parents: 25 hours
        # If 2+ non-exempt parents: 50 hours
        requirement = where(num_non_exempt_parents > 1, p.two_parent, p.single_parent)

        # The SPM unit is eligible if the non-exempt parents' combined work
        # hours meet the requirement, or if every parent is exempt.
        household_meets_work_requirement = total_work_hours >= requirement
        all_parents_exempt = num_non_exempt_parents == 0
        return household_meets_work_requirement | all_parents_exempt
