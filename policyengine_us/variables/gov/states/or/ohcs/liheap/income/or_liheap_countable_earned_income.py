from policyengine_us.model_api import *


class or_liheap_countable_earned_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Oregon LIHEAP countable earned income"
    unit = USD
    defined_for = StateCode.OR
    # PDF pages 35, 41, 45, 53.
    reference = "https://www.oregon.gov/ohcs/energy-weatherization/Documents/2026%20Final%20Energy%20Assistance%20Intake%20Operations%20%26%20Policy%20Manual.pdf#page=35"
    documentation = (
        "Existing net self-employment inputs are used without an additional expense "
        "deduction. Flooring each source at zero is a modeling convention; the manual "
        "does not specify current-period loss offsets."
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states["or"].ohcs.liheap.income
        earned = 0
        for source in p.sources.earned:
            earned = earned + max_(person(source, period), 0)
        counted = (person("age", period) >= p.earned_income_min_age) & ~person(
            "is_in_secondary_school", period
        )
        return where(counted, earned, 0)
