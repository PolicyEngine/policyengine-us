from policyengine_us.model_api import *


class snap_eligible_share_of_expense(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP eligible share of expense"
    documentation = "Share of household expense that is deductible for SNAP after excluding ineligible members' portion"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/7/273.11#c_3"

    def formula(spm_unit, period, parameters):
        # Per 273.11(c)(1): Deductible expenses are divided evenly among all members
        # including the ineligible ones. All but the ineligible alien's share is counted
        # as a deductible expense for the remaining household members.
        #
        # This returns (1 - ineligible_fraction / spm_unit_size) which is the proportion
        # of the expense that is deductible after excluding ineligible members' share

        ineligible_fraction = spm_unit(
            "snap_ineligible_members_fraction", period
        )
        spm_unit_size = spm_unit("spm_unit_size", period)

        # Avoid division by zero
        return where(
            spm_unit_size > 0, 1 - ineligible_fraction / spm_unit_size, 1
        )
