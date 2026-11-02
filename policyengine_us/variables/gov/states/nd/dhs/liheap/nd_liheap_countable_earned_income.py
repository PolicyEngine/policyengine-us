from policyengine_us.model_api import *


class nd_liheap_countable_earned_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "North Dakota LIHEAP countable earned income"
    reference = (
        "https://www.nd.gov/dhs/policymanuals/415/415_25_05_05.htm",
        "https://www.nd.gov/dhs/policymanuals/415/415_25_05_20_05.htm",
        "https://www.nd.gov/dhs/policymanuals/415/415_25_05_27_15.htm",
        "https://www.nd.gov/dhs/policymanuals/415/415_25_05_50.htm",
    )
    defined_for = StateCode.ND

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nd.dhs.liheap.income
        # Supplied net business inputs omit policy depreciation addbacks.
        # Separate source/person losses cannot offset other earnings; losses
        # within an aggregated business input cannot be isolated.
        earnings = 0
        for source in p.earned_sources:
            earnings = earnings + max_(person(source, period), 0)
        school = person("is_in_k12_school", period) | person(
            "is_in_secondary_school", period
        )
        # Tax dependency and reported school attendance approximate parental
        # control and half-time elementary/high-school/GED attendance.
        exempt_child = (
            person("is_tax_unit_dependent", period)
            & (person("age", period) < p.child_earnings_age_limit)
            & school
        )
        return where(exempt_child, 0, earnings * (1 - p.earned_income_deduction))
