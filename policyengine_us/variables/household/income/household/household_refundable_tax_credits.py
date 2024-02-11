from policyengine_us.model_api import *


class household_refundable_tax_credits(Variable):
    value_type = float
    entity = Household
    label = "refundable tax credits"
    definition_period = YEAR
    unit = USD

    def formula(household, period, parameters):
        p = parameters(period)
        added_components = p.gov.household_refundable_credits
        if p.gov.contrib.ubi_center.flat_tax.abolish_federal_income_tax:
            added_components = [
                c
                for c in added_components
                if c != "income_tax_refundable_credits"
            ]
        if p.simulation.reported_state_income_tax:
            added_components = [
                "income_tax_refundable_credits",  # Federal.
            ]
        return add(household, period, added_components)
