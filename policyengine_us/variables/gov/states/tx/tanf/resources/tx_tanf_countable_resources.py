from policyengine_us.model_api import *


class tx_tanf_countable_resources(Variable):
    value_type = float
    entity = SPMUnit
    label = "Texas TANF countable resources"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-1210-general-policy",
        "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-1220-limits",
    )
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        # Countable resources = liquid resources + excess vehicle value
        # Household must have countable resources ≤ $1,000 to be eligible

        # Liquid resources (cash, checking, savings) - stocks use period.this_year
        cash_assets = spm_unit("spm_unit_cash_assets", period.this_year)

        # Vehicle resources (apply vehicle exemption: one automobile up to $4,650)
        vehicle_value = spm_unit.household(
            "household_vehicles_value", period.this_year
        )
        p = parameters(period).gov.states.tx.tanf.resources
        countable_vehicle_value = max_(vehicle_value - p.vehicle_exemption, 0)

        # Total countable resources (no period conversion - resources are stocks)
        return cash_assets + countable_vehicle_value
