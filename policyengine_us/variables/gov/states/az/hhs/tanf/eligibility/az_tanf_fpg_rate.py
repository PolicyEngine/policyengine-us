from policyengine_us.model_api import *


class az_tanf_fpg_rate(Variable):
    value_type = float
    entity = SPMUnit
    label = "Arizona TANF needy family FPG rate"
    definition_period = MONTH
    reference = "https://www.azleg.gov/ars/46/00292.htm"
    defined_for = StateCode.AZ

    def formula(spm_unit, period, parameters):
        # 130% FPG for non-parent relative heads requesting CA only for dependent children
        # 100% FPG for all other families (default)
        # Reference: A.R.S. § 46-292
        p = parameters(period).gov.states.az.hhs.tanf.income.fpg_limit

        person = spm_unit.members
        # Use period.this_year for YEAR-defined demographic variables
        is_head = person("is_tax_unit_head", period.this_year)
        # Use is_parent which checks own_children_in_household > 0
        is_parent = person("is_parent", period.this_year)
        is_child = person("is_child", period.this_year)

        # Check if head is a parent (has own children in household)
        head_is_parent = spm_unit.any(is_head & is_parent)
        # Check if there are children in the unit
        has_children = spm_unit.any(is_child)

        # Non-parent relative caretaker: head is NOT a parent but unit HAS children
        is_non_parent_relative_case = ~head_is_parent & has_children

        return where(is_non_parent_relative_case, p.non_parent, p.base)
