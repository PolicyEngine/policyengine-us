from policyengine_us.model_api import *


class tx_ccs_work_requirement_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Texas CCS work requirement eligible"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/texas/40-Tex-Admin-Code-SS-809-56"
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.tx.twc.ccs.work_requirements

        # Get work hours for tax unit heads and spouses in the SPM unit
        person = spm_unit.members
        is_tax_unit_head_or_spouse = person(
            "is_tax_unit_head_or_spouse", period
        )
        work_hours = person("weekly_hours_worked", period.this_year)
        parent_work_hours = where(is_tax_unit_head_or_spouse, work_hours, 0)

        # Count number of parents (tax unit heads and spouses)
        num_parents = spm_unit.sum(is_tax_unit_head_or_spouse)

        # Sum total work hours
        total_work_hours = spm_unit.sum(parent_work_hours)

        # Check requirements based on number of parents
        single_parent = num_parents == 1
        two_parent = num_parents >= 2

        single_parent_eligible = single_parent & (
            total_work_hours >= p.single_parent
        )
        two_parent_eligible = two_parent & (total_work_hours >= p.two_parent)

        # If no parents, not eligible
        no_parents = num_parents == 0

        return where(
            no_parents, False, single_parent_eligible | two_parent_eligible
        )
