from policyengine_us.model_api import *


class mi_homestead_property_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan Homestead Property Tax Credit"
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
        non_refundable_percentage = where(
            disabled_people > 0,
            p.disabled.not_refundable_percentage.calc(
                total_household_resources
            ),
            p.not_refundable_percentage,
        )

        # seniors
        age_older = tax_unit("age_head", period)
        non_refundable_percentage = where(
            age_older >= p.senior.min_age,
            p.senior.not_refundable_percentage.calc(total_household_resources),
            p.not_refundable_percentage,
        )
        phase_out_percentage = where(
            age_older >= p.senior.min_age,
            p.senior.phase_out_percentage.calc(total_household_resources),
            p.phase_out_percentage.calc(total_household_resources),
        )

        property_value = add(tax_unit, period, ["assessed_property_value"])
        rents = add(tax_unit, period, ["rent"])

        # eligibility
        rent_eligibility = (
            rents * p.rent_percentage
            > total_household_resources * non_refundable_percentage
        )
        property_eligibility = (
            property_value
            > total_household_resources * non_refundable_percentage
        ) & (property_value < p.max_property_value)
        eligibility = where(
            rents > 0,
            rent_eligibility,
            property_eligibility,
        )

        # difference
        rent_difference = (
            rents * p.rent_percentage
            - total_household_resources * non_refundable_percentage
        )
        property_difference = (
            property_value
            - total_household_resources * non_refundable_percentage
        )
        difference = where(
            rents > 0,
            rent_difference,
            property_difference,
        )

        return min_(
            eligibility * difference * phase_out_percentage, p.max_amount
        )
