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

        thr = tax_unit("mi_household_resources", period)

        # disabled
        disabled_people = add(tax_unit, period, ["is_disabled"])
        nf_percentage = where(
            disabled_people > 0,
            p.disabled.not_refundable_percentage.calc(thr),
            p.not_refundable_percentage,
        )

        # seniors
        age_older = tax_unit("age_head", period)
        nf_percentage = where(
            age_older >= p.senior.min_age,
            p.senior.not_refundable_percentage.calc(thr),
            p.not_refundable_percentage,
        )
        po_percentage = where(
            age_older >= p.senior.min_age,
            p.senior.phase_out_percentage.calc(thr),
            p.phase_out_percentage.calc(thr),
        )

        property_value = add(tax_unit, period, ["assessed_property_value"])
        rents = add(tax_unit, period, ["rent"])
        eligibility = where(
            rents > 0,
            (rents * p.rent_percentage > thr * nf_percentage),
            (property_value > thr * nf_percentage)
            & (property_value < p.max_property_value),
        )
        difference = where(
            rents > 0,
            rents * p.rent_percentage - thr * nf_percentage,
            property_value - thr * nf_percentage,
        )

        return min_(eligibility * difference * po_percentage, p.max_amount)
