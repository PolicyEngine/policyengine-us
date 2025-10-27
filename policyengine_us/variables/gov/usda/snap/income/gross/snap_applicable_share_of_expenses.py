from policyengine_us.model_api import *


class snap_applicable_share_of_expenses(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP applicable share of expenses"
    documentation = "Share of household expense that is deductible for SNAP after excluding ineligible members' portion"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/7/273.11#c_3"

    def formula(spm_unit, period, parameters):
        # Per 273.11(c)(1): Deductible expenses are divided evenly among all members
        # including the ineligible ones. All but the ineligible alien's share is counted
        # as a deductible expense for the remaining household members.
        #
        # The correct formula is: 1 - ineligible_fraction²
        # This accounts for the fact that each ineligible member's share of expenses
        # is reduced by the ineligible fraction (their proportionate share)

        ineligible_fraction = spm_unit(
            "snap_ineligible_members_fraction", period
        )
        spm_unit_size = spm_unit("spm_unit_size", period)

        # Avoid division by zero
        return where(
            spm_unit_size > 0,
            1 - ineligible_fraction * ineligible_fraction,
            1,
        )
