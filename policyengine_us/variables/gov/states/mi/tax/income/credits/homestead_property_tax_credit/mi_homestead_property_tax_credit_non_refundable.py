from policyengine_us.model_api import *


class mi_homestead_property_tax_credit_non_refundable(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan non-refundable Homestead Property Tax Credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mi.tax.income.credits.homestead_property_tax_credit

        total_household_resources = tax_unit("mi_household_resources", period)

        # disabled
        disabled_people = add(tax_unit, period, ["is_disabled"])
        disabled_non_refundable_rate = where(
            disabled_people > 0,
            p.disabled.not_refundable_rate.calc(total_household_resources),
            p.not_refundable_rate,
        )

        # seniors
        age_older = tax_unit("age_head", period)
        senior_non_refundable_rate = where(
            age_older >= p.senior.min_age,
            p.senior.not_refundable_rate.calc(total_household_resources),
            p.not_refundable_rate,
        )

        non_refundable_rate = min_(
            disabled_non_refundable_rate, senior_non_refundable_rate
        )

        return total_household_resources * non_refundable_rate
