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
    )
    defined_for = StateCode.VT

    def formula(tax_unit, period, parameters):
        # income > uppder cap, then credit is 0
        # income < lower cap, then credit is fair market rent
        # income is between upper cap and lower cap:
        ## if no subsidized: (upper cap - income)/(upper cap - lower cap) * fair market rent * 0.5 if shared rent

        ## if subsidized: (upper cap - income)/(upper cap - lower cap) * actual pay rent amount * 0.1  * 0.5 if shared rent
        p = parameters(period).gov.states.vt.tax.income.credits.renter
        vt_renter_credit_income = tax_unit("vt_renter_credit_income", period)
        family_size = tax_unit("tax_unit_size", period)
        county = tax_unit.household("county", period)
        share_rent = tax_unit("share_rent", period)
        subsidized = tax_unit("rent_is_subsidized", period)
        rent_pay = add(tax_unit, period, ["rent"])
        match_full_credit_income = p.limit.full_credit_income[family_size][
            county
        ]
        match_partial_credit_income = p.limit.partial_credit_income[
            family_size
        ][county]
        match_base_credit_amount = p.base[family_size][county]
        percent_reabte_claimable = (
            match_partial_credit_income - vt_renter_credit_income
        ) / (match_partial_credit_income - match_full_credit_income)
        conditions = [
            vt_renter_credit_income > match_partial_credit_income,
            (vt_renter_credit_income < match_full_credit_income) & ~subsidized,
            (vt_renter_credit_income < match_full_credit_income) & subsidized,
            (
                match_full_credit_income
                <= vt_renter_credit_income
                <= match_partial_credit_income
            )
            & ~subsidized,
            (
                match_full_credit_income
                <= vt_renter_credit_income
                <= match_partial_credit_income
            )
            & subsidized,
        ]
        values = [
            0,
            match_base_credit_amount * p.share_rent_rate**share_rent,
            rent_pay * p.rent_rate * p.share_rent_rate**share_rent,
            percent_reabte_claimable
            * match_base_credit_amount
            * p.share_rent_rate**share_rent,
            percent_reabte_claimable
            * rent_pay
            * p.rent_rate
            * p.share_rent_rate**share_rent,
        ]
        return np.round(select(conditions, values), 0)
