from policyengine_us.model_api import *


class new_clean_vehicle_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Eligible for new clean vehicle credit"
    documentation = (
        "Eligible for nonrefundable credit for the purchase of a new clean vehicle"
    )
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/30D"
    defined_for = "purchased_qualifying_new_clean_vehicle"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.credits.clean_vehicle.new.eligibility
        # One Big Beautiful Bill Act (Pub. L. 119-21 § 70502) terminates the
        # credit for vehicles acquired after September 30, 2025. See
        # in_effect.yaml for the annual-resolution approximation of this
        # intra-year cutoff.
        if not p.in_effect:
            return False
        # Capacity limit applies with and without the Inflation Reduction Act.
        capacity = tax_unit("new_clean_vehicle_battery_capacity", period)
        meets_capacity_requirement = capacity >= p.min_kwh
        # 26 U.S.C. 30D(f)(10): no credit if the lesser of this year's and
        # the preceding year's modified adjusted gross income exceeds the
        # limit. Modified AGI adds back income excluded under sections 911,
        # 931 and 933 (30D(f)(10)(C)). If the filing status changed, each
        # year's modified AGI is compared with the limit for that year's
        # status (26 CFR 1.30D-4(b)(3)); otherwise this is the lesser-of test.
        magi = tax_unit("agi_plus_section_911_931_933_exclusions", period)
        prior_magi = tax_unit("clean_vehicle_credit_prior_year_magi", period)
        filing_status = tax_unit("filing_status", period)
        prior_filing_status = tax_unit(
            "clean_vehicle_credit_prior_year_filing_status", period
        )
        meets_income_limit = (magi <= p.income_limit[filing_status]) | (
            prior_magi <= p.income_limit[prior_filing_status]
        )
        msrp = tax_unit("new_clean_vehicle_msrp", period)
        classification = tax_unit("new_clean_vehicle_classification", period)
        meets_msrp_limit = msrp <= p.msrp_limit[classification]
        return meets_capacity_requirement & meets_income_limit & meets_msrp_limit
