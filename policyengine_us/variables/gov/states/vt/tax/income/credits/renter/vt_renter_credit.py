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
        p = parameters(period).gov.states.vt.tax.income.credits.renter
        # get tax unit size and county.
        tax_unit_size = tax_unit("tax_unit_size", period)
        county = tax_unit.household("county", period)
        # locate the values by family size and county
        full_credit_income_limit = p.income_limit_ami.thirty_percent[
            tax_unit_size
        ][county]
        partial_credit_income_limit = p.income_limit_ami.fifty_percent[
            tax_unit_size
        ][county]
        fmr = p.fair_market_rent[tax_unit_size][county]
        base_credit_amount = fmr * MONTHS_IN_YEAR * p.fmr_rate

        # Compute what the spreadsheet calls the "percent reabte claimable"
        vt_renter_credit_income = tax_unit("vt_renter_credit_income", period)
        income_diff = partial_credit_income_limit - vt_renter_credit_income
        income_threshold_diff = (
            partial_credit_income_limit - full_credit_income_limit
        )
        percent_rebate_claimable = income_diff / income_threshold_diff
        # If shared residence, reduce by a given fraction.
        shared_rent = tax_unit("rent_is_shared_with_another_tax_unit", period)
        shared_residence_reduction = shared_rent * p.shared_residence_reduction
        # if subsidized, get base credit
        has_housing_assistance = (
            tax_unit.spm_unit("housing_assistance", period) > 0
        )
        rent_amount = add(tax_unit, period, ["rent"])
        base_credit_subsidized = rent_amount * p.fmr_rate

        # income > partial credit income limit, then credit is 0
        # income < full credit income limit, then credit is fair market rent
        # income is between partial credit income limit and full credit income limit:
        ## if no subsidized: (partial credit income limit - income)/(partial credit income limit - full credit income limit) * fair market rent
        ## if subsidized: (partial credit income limit - income)/(partial credit income limit - full credit income limit) * actual pay rent amount * rent rate
        # for all of the above situations, mulitple by the share rent rate if the the rental unit was shared
        high_income = vt_renter_credit_income > partial_credit_income_limit
        low_income = vt_renter_credit_income < full_credit_income_limit
        mid_income = ~(high_income | low_income)
        credit_value = select(
            [
                low_income & ~has_housing_assistance,
                low_income & has_housing_assistance,
                mid_income & ~has_housing_assistance,
                mid_income & has_housing_assistance,
            ],
            [
                base_credit_amount,
                base_credit_subsidized,
                percent_rebate_claimable * base_credit_amount,
                percent_rebate_claimable * base_credit_subsidized,
            ],
            default=0,
        )
        unrounded = credit_value * (1 - shared_residence_reduction)
        return np.round(unrounded)
