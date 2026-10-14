from policyengine_us.model_api import *


class ny_heap_countable_earned_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "New York HEAP countable earnings"
    unit = USD
    defined_for = StateCode.NY
    # PDF pages 37, 39, 42, 43.
    reference = ("https://otda.ny.gov/programs/heap/HEAP-manual.pdf#page=37",)
    documentation = (
        "Existing net business income is used without further deductions. "
        "HEAP-specific depreciation add-backs, separate accounting periods and wage "
        "bonus exclusions are unsupported."
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ny.otda.heap.income
        earnings = 0
        for source in p.sources.earned:
            earnings = earnings + max_(person(source, period), 0)
        dependent = person("is_tax_unit_dependent", period)
        exempt = dependent & (
            (person("age", period) < p.dependent_child_age)
            | person("is_full_time_student", period)
        )
        return where(exempt, 0, earnings)
