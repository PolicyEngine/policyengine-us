from policyengine_us.model_api import *


class vt_renter_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont renter credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/vermont/2022/title-32/chapter-154/section-6066/"  # b
        "https://tax.vermont.gov/sites/tax/files/documents/Income%20Booklet-2022.pdf#page=35"
        # the formula used in this file is based on the excel sheet download from the official Vermont government website
    )
    defined_for = StateCode.VT

    def formula(tax_unit, period, parameters):
        # income > uppder cap, then credit is 0
        # income < lower cap, then credit is fair market rent
        # income is between upper cap and lower cap:
        ## if no subsidized: (upper cap - income)/(upper cap - lower cap) * fair market rent
        ## if subsidized: (upper cap - income)/(upper cap - lower cap) * actual pay rent amount * rent rate
        # for all of the above situations, mulitple by the share rent rate if the the rental unit was shared
        p = parameters(period).gov.states.vt.tax.income.credits.renter
        vt_renter_credit_income = tax_unit("vt_renter_credit_income", period)
        family_size = tax_unit("tax_unit_size", period)
        county = tax_unit.household("county", period)
        shared_rent = tax_unit("rent_is_shared_with_another_tax_unit", period)
        subsidized_rent = tax_unit("rent_is_subsidized", period)
        rent_pay = add(tax_unit, period, ["rent"])

        # locate the values by family size and county
        match_full_credit_income = p.income_limit.full_credit[family_size][
            county
        ]
        match_partial_credit_income = p.income_limit.partial_credit[
            family_size
        ][county]
        match_base_credit_amount = (
            p.fair_market_rent[family_size][county]
            * MONTHS_IN_YEAR
            * p.rate.rent
        )

        # Compute percent reabte claimable amount
        income_diff = match_partial_credit_income - vt_renter_credit_income
        partial_full_income_diff = (
            match_partial_credit_income - match_full_credit_income
        )
        percent_reabte_claimable = income_diff / partial_full_income_diff
        # if share rent, miltiple by share rent rate
        share = p.rate.share_rent**shared_rent
        # if subsidized, get base credit
        base_credit_subsidized = rent_pay * p.rate.rent

        high_income = vt_renter_credit_income > match_partial_credit_income
        low_income = vt_renter_credit_income < match_full_credit_income
        mid_income = (
            match_full_credit_income
            <= vt_renter_credit_income
            <= match_partial_credit_income
        )
        credit_value = select(
            [
                high_income,
                low_income & ~subsidized_rent,
                low_income & subsidized_rent,
                mid_income & ~subsidized_rent,
                mid_income & subsidized_rent,
            ],
            [
                0,
                match_base_credit_amount,
                base_credit_subsidized,
                percent_reabte_claimable * match_base_credit_amount,
                percent_reabte_claimable * base_credit_subsidized,
            ],
        )
        return np.round(credit_value * share, 0)
