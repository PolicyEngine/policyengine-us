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
        # Income eligibility based on lesser of MAGI in current and prior year.
        # Assume current-year MAGI for now. 26 U.S.C. 25E(b)(3): modified
        # adjusted gross income adds back income excluded under sections
        # 911, 931 and 933.
        magi = tax_unit("agi_plus_section_911_931_933_exclusions", period)
        filing_status = tax_unit("filing_status", period)
        income_limit = p.eligibility.income_limit[filing_status]
        income_eligible = magi <= income_limit
        # Purchase price limit.
        sale_price = tax_unit("used_clean_vehicle_sale_price", period)
        price_eligible = sale_price <= p.eligibility.sale_price_limit
        return income_eligible & price_eligible
