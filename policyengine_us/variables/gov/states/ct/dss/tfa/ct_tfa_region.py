"""
Connecticut TFA regional payment standard determination.
"""

from policyengine_us.model_api import *


class ct_tfa_region(Variable):
    value_type = str
    entity = SPMUnit
    label = "Connecticut TFA payment region"
    definition_period = YEAR
    defined_for = StateCode.CT
    documentation = (
        "Connecticut divides the state into three payment regions (A, B, C) "
        "based on average cost of rent in each area. Region A has the highest "
        "benefit amounts (highest housing costs), Region B has middle amounts, "
        "and Region C has the lowest amounts."
    )
    reference = "Connecticut TANF State Plan 2024-2026, Addendum A (Regional Assignments)"

    def formula(spm_unit, period, parameters):
        # NOTE: Specific town/city assignments to regions are in Addendum A
        # of the TANF State Plan, which is not publicly available online.
        # This implementation returns a default of Region B as a placeholder.
        # In a full implementation, this would need to map county/town to region.

        # For now, return Region B as the default
        # TODO: Implement proper geographic mapping when Addendum A is available
        return spm_unit("ct_tfa_region_str", period)


class ct_tfa_region_str(Variable):
    value_type = str
    entity = SPMUnit
    label = "Connecticut TFA payment region (user input)"
    definition_period = YEAR
    defined_for = StateCode.CT
