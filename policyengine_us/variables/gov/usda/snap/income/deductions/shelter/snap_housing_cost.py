from policyengine_us.model_api import *


class snap_housing_cost(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP housing cost with proration"
    unit = USD
    documentation = "Total housing costs for SNAP with proration applied to all shelter expenses per 7 CFR 273.11(c)"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/uscode/text/7/2014#e_6"

    def formula(spm_unit, period, parameters):
        # Sum all housing costs
        person_level_costs = add(
            spm_unit, period, ["snap_housing_cost_person"]
        )

        spm_level_costs = add(
            spm_unit,
            period,
            [
                "mortgage_payments",
                "homeowners_insurance",
                "homeowners_association_fees",
            ],
        )

        # Apply proration to SPMUnit-level costs
        # Person-level costs are already prorated in snap_housing_cost_person
        prorate_factor = spm_unit(
            "snap_eligible_share_of_expense", period.this_year
        )

        # Apply proration only to SPMUnit-level costs (person-level already prorated)
        return person_level_costs + (spm_level_costs * prorate_factor)
