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
        # the formula used in this file is based on the excel sheet provided on the official Vermont government website
        "https://tax.vermont.gov/individuals/renter-credit/calculator-and-credit-amounts"  # link for the excel sheet
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
        tax_unit_size = tax_unit("tax_unit_size", period)
        county = tax_unit.household("county", period)
        shared_rent = tax_unit("rent_is_shared_with_another_tax_unit", period)
        has_housing_assistance = tax_unit.spm_unit(("housing_assistance"), period) > 0
        rent_amount = add(tax_unit, period, ["rent"])

        # locate the values by family size and county
        full_credit_income_limit = p.income_limit.full_credit[tax_unit_size][
            county
        ]
        partial_credit_income_limit = p.income_limit.partial_credit[
            tax_unit_size
        ][county]
        base_credit_amount = (
            p.fair_market_rent[tax_unit_size][county]
            * MONTHS_IN_YEAR
            * p.fmr_rate
        )

        # Compute percent reabte claimable amount
        income_diff = partial_credit_income_limit - vt_renter_credit_income
        income_threshold_diff = (
            partial_credit_income_limit - full_credit_income_limit
        )
        percent_reabte_claimable = income_diff / income_threshold_diff
        # if share rent, miltiple by share rent rate
        share = where(shared_rent, 1/p.shared_residence_reduction, 1)        
        # if subsidized, get base credit
        base_credit_subsidized = rent_amount * p.fmr_rate

        high_income = vt_renter_credit_income > partial_credit_income_limit
        low_income = vt_renter_credit_income < full_credit_income_limit
        mid_income = ~(high_income | low_income)
        credit_value = select(
            [
                high_income,
                low_income & ~has_housing_assistance,
                low_income & has_housing_assistance,
                mid_income & ~has_housing_assistance,
                mid_income & has_housing_assistance,
            ],
            [
                0,
                base_credit_amount,
                base_credit_subsidized,
                percent_reabte_claimable * base_credit_amount,
                percent_reabte_claimable * base_credit_subsidized,
            ],
            default = 0
        )
        return np.round(credit_value * share, 0)
