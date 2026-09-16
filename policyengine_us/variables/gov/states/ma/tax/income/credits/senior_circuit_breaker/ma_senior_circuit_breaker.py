from policyengine_us.model_api import *


class ma_senior_circuit_breaker(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA Senior Circuit Breaker Credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.mass.gov/info-details/mass-general-laws-c62-ss-6",  # Part (k)
        "https://malegislature.gov/Laws/GeneralLaws/PartI/TitleIX/Chapter62/Section6",  # c.62 s.6(k)(5)
        "https://www.mass.gov/doc/2023-schedule-cb-circuit-breaker-credit/download",
    )
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        scb = parameters(period).gov.states.ma.tax.income.credits.senior_circuit_breaker

        # Age-based eligibility.
        person = tax_unit.members
        age = person("age", period)
        is_dependent = person("is_tax_unit_dependent", period)
        aged = age >= scb.eligibility.min_age
        meets_age_condition = tax_unit.any(~is_dependent & aged)

        # Real-estate-based phase-in.
        real_estate_tax = add(tax_unit, period, ["real_estate_taxes"])
        rent = add(tax_unit, period, ["rent"])
        equivalent_rent = rent * scb.amount.rent_tax_share
        real_estate_tax_or_equiv = real_estate_tax + equivalent_rent

        # Comparison to income for maximum credit determination.
        income = tax_unit("ma_scb_total_income", period)
        income_threshold = income * scb.amount.min_real_estate_tax
        ret_over_threshold = max_(0, real_estate_tax_or_equiv - income_threshold)
        max_payment = min_(ret_over_threshold, scb.amount.max)

        # Means-test conditions based on income (cliff).
        filing_status = tax_unit("ma_filing_status", period)
        meets_max_income_condition = income <= scb.eligibility.max_income[filing_status]

        # Means-tested conditions based on property value (cliff).
        assessed_value = add(tax_unit, period, ["assessed_property_value"])
        meets_max_property_value_condition = (
            assessed_value <= scb.eligibility.max_property_value
        )
        # Married taxpayers filing separately do not qualify. M.G.L. c.62
        # Section 6(k)(5) ("No credit shall be allowed for a married
        # individual unless a joint return is filed") is the all-years
        # statutory authority; annual Schedule CB guidance restates it.
        separate = filing_status == filing_status.possible_values.SEPARATE
        eligible = (
            meets_age_condition
            & meets_max_income_condition
            & meets_max_property_value_condition
            & ~separate
        )

        return eligible * max_payment
