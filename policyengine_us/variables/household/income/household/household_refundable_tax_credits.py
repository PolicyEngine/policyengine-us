from policyengine_us.model_api import *


class household_refundable_tax_credits(Variable):
    value_type = float
    entity = Household
    label = "refundable tax credits"
    definition_period = YEAR
    unit = USD

    def formula(household, period, parameters):
        credits = add(
            household,
            period,
            [
                "household_refundable_state_tax_credits",
                "household_refundable_local_tax_credits",
            ],
        )
        # `income_tax` nets federal refundable credits and is zero when the
        # federal income tax is abolished, so the credits go too.
        if parameters(
            period
        ).gov.contrib.ubi_center.flat_tax.abolish_federal_income_tax:
            return credits
        return credits + add(household, period, ["income_tax_refundable_credits"])
