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
        # if no subsidized: (upper cap - lower cap)/(upper cap - income) * fair market rent * 0.5 if shared rent

        # if subsidized: (upper cap - lower cap)/(upper cap - income) * actual pay rent amount * 0.1  * 0.5 if shared rent
        p = parameters(period).gov.states.vt.tax.income.credits.renter
        vt_renter_credit_income = tax_unit("vt_renter_credit_income", period)
        family_size = tax_unit("tax_unit_size", period)
        # bedroom_count = tax_unit("vt_bedroom_count", period)
        county_str = tax_unit("county_str", period)
        share_rent = tax_unit("vt_share_rent", period)
        subsidized = tax_unit("vt_subsidy", period)
        rent_pay = tax_unit("rents", period)
        match_full_credit_income = p.full_credit_income_limits[family_size][
            county_str
        ]
        match_partial_credit_income = p.partial_credit_income_limits[
            family_size
        ][county_str]
        match_base_credit_amount = p.base_credit_amount[family_size][
            county_str
        ]

        if vt_renter_credit_income < match_full_credit_income:
            if subsidized == 0:
                return (
                    match_base_credit_amount * p.share_rent_rate**share_rent
                )
            else:
                return rent_pay * p.rent_rate * p.share_rent_rate**share_rent
        elif vt_renter_credit_income > match_partial_credit_income:
            return 0
        else:
            if subsidized == 0:
                return (
                    (match_partial_credit_income - match_full_credit_income)
                    / (match_partial_credit_income - vt_renter_credit_income)
                    * match_base_credit_amount
                    * p.share_rent_rate**share_rent
                )
            else:
                return (
                    (match_partial_credit_income - match_full_credit_income)
                    / (match_partial_credit_income - vt_renter_credit_income)
                    * rent_pay
                    * p.rent_rate
                    * p.share_rent_rate**share_rent
                )
