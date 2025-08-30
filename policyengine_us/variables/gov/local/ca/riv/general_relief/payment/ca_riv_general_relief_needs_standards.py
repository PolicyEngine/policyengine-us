from policyengine_us.model_api import *


class ca_riv_general_relief_needs_standards(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Riverside County General Relief needs standards"
    definition_period = MONTH
    defined_for = "in_riv"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.local.ca.riv.general_relief.needs_standards
        size = spm_unit("ca_riv_general_relief_budget_unit_size", period)
        capped_size = clip(size, 1, 5)
        # Verify the housing cost using the DPSS 1140, GA Housing Information/Verification,
        # or any other sufficient verification, such as lease agreement
        housing_expense = spm_unit("housing_cost", period)
        capped_housing_benefit = min_(housing_expense, p.housing[capped_size])
        return (
            capped_housing_benefit
            + p.food[capped_size]
            + p.personal_needs[capped_size]
        )
