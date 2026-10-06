from policyengine_us.model_api import *


class used_clean_vehicle_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Eligible for used clean vehicle credit"
    documentation = "Eligible for nonrefundable credit for the purchase of a previously-owned clean vehicle"
    unit = USD
    reference = "https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=370"
    defined_for = "purchased_qualifying_used_clean_vehicle"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.credits.clean_vehicle.used
        # One Big Beautiful Bill Act (Pub. L. 119-21 § 70501) terminates the
        # credit for vehicles acquired after September 30, 2025. See
        # eligibility/in_effect.yaml for the annual-resolution approximation
        # of this intra-year cutoff.
        if not p.eligibility.in_effect:
            return False
        # 26 U.S.C. 25E(b)(1): no credit if the lesser of this year's and
        # the preceding year's modified adjusted gross income exceeds the
        # limit. Modified AGI adds back income excluded under sections 911,
        # 931 and 933 (25E(b)(3)). If the filing status changed, each year's
        # modified AGI is compared with the limit for that year's status
        # (26 CFR 1.25E-1(c)(3)); otherwise this is the lesser-of test.
        magi = tax_unit("agi_plus_section_911_931_933_exclusions", period)
        prior_magi = tax_unit("clean_vehicle_credit_prior_year_magi", period)
        filing_status = tax_unit("filing_status", period)
        prior_filing_status = tax_unit(
            "clean_vehicle_credit_prior_year_filing_status", period
        )
        income_limit = p.eligibility.income_limit
        income_eligible = (magi <= income_limit[filing_status]) | (
            prior_magi <= income_limit[prior_filing_status]
        )
        # Purchase price limit.
        sale_price = tax_unit("used_clean_vehicle_sale_price", period)
        price_eligible = sale_price <= p.eligibility.sale_price_limit
        return income_eligible & price_eligible
