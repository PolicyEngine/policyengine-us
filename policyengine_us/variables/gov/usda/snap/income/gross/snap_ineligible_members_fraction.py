from policyengine_us.model_api import *


class snap_ineligible_members_fraction(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP ineligible members fraction"
    documentation = "Fraction of household members who are ineligible for SNAP (used in proration calculations)"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/7/273.11#c_3"

    def formula(spm_unit, period, parameters):
        # Per 273.11(c)(1): Deductible expenses are divided evenly among all members
        # including the ineligible ones. All but the ineligible alien's share is counted
        # as a deductible expense for the remaining household members.

        prorate_people_count = spm_unit(
            "snap_unit_prorate_people_count", period
        )
        total_size = spm_unit("spm_unit_size", period)
        # Avoid division by zero
        return where(total_size > 0, prorate_people_count / total_size, 0)
