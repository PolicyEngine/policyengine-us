from policyengine_us.model_api import *


class mi_homestead_allowable(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan allowable Homestead Property Tax Credit"
    unit = USD
    definition_period = YEAR
    defined_for = "mi_homestead_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mi.tax.income.credits.homestead_property_tax_credit

        total_household_resources = tax_unit("mi_household_resources", period)
        refundable_amount = tax_unit("mi_homestead_refundable", period)

        # seniors
        age_older_eligible = (
            tax_unit("greater_age_head_spouse", period) >= p.senior.min_age
        )
        phase_out_rate = p.senior.phase_out_rate.calc(
            total_household_resources
        )
        senior_allowable = min_(
            phase_out_rate * refundable_amount,
            p.max.amount,
        )

        # disabled or disabled & seniors
        disabled_eligible = add(tax_unit, period, ["is_disabled"]) > 0
        both_eligible = age_older_eligible & disabled_eligible
        disabled_both_eligible = min_(
            refundable_amount,
            p.max.amount,
        )

        # other
        credit_rate = p.rate.credit
        other_allowable = min_(
            credit_rate * refundable_amount,
            p.max.amount,
        )

        return select(
            [(disabled_eligible | both_eligible), age_older_eligible],
            [disabled_both_eligible, senior_allowable],
            default=other_allowable,
        )
