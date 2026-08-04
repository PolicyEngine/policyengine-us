from policyengine_us.model_api import *


class ut_homeowner_renter_relief_pre_one_claimant_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for Utah Homeowner's/Renter's Relief before one-claimant limit"
    definition_period = YEAR
    reference = (
        "https://tax.utah.gov/relief/homeowner-renter-relief/",
        "https://tax.utah.gov/relief/renter-refund/",
        "https://le.utah.gov/xcode/Title59/Chapter2A/C59-2a_2026010120250507.pdf#page=1",
    )
    defined_for = StateCode.UT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ut.tax.property.homeowner_renter_relief
        age_head = tax_unit("age_head", period)
        age_spouse = tax_unit("age_spouse", period)
        filing_status = tax_unit("filing_status", period)
        statuses = filing_status.possible_values
        age_eligible = (age_head >= p.age_threshold) | (age_spouse >= p.age_threshold)
        surviving_spouse = filing_status == statuses.SURVIVING_SPOUSE
        renter_income = tax_unit.household(
            "ut_homeowner_renter_relief_household_income", period
        )
        homeowner_income = tax_unit.household(
            "ut_homeowner_renter_relief_household_income", period.last_year
        )
        rent = add(tax_unit, period, ["rent"])
        real_estate_taxes = add(tax_unit, period, ["real_estate_taxes"])
        income_eligible = ((rent > 0) & (renter_income <= p.income_limit)) | (
            (real_estate_taxes > 0) & (homeowner_income <= p.income_limit)
        )
        claimants = tax_unit.members("is_tax_unit_head_or_spouse", period)
        claimant_is_tax_unit_dependent = tax_unit.any(
            claimants & tax_unit.members("is_tax_unit_dependent", period)
        )
        claimant_is_dependent_elsewhere = tax_unit(
            "head_is_dependent_elsewhere", period
        ) | tax_unit("spouse_is_dependent_elsewhere", period)
        claimant_is_dependent = (
            claimant_is_tax_unit_dependent | claimant_is_dependent_elsewhere
        )
        return (
            (age_eligible | surviving_spouse) & income_eligible & ~claimant_is_dependent
        )
