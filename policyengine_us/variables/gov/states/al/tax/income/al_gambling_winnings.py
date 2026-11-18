from policyengine_us.model_api import *


class al_gambling_winnings(Variable):
    value_type = float
    entity = Person
    label = "Alabama gambling winnings"
    unit = USD
    documentation = (
        "Gambling winnings reported on the Alabama return of the tax unit's "
        "head or spouse. A dependent who must file reports their own "
        "winnings on their own return."
    )
    definition_period = YEAR
    reference = (
        # 2025 Form 40 booklet: who must file, and taxable income
        # PDF pages 5, 7
        "https://www.revenue.alabama.gov/wp-content/uploads/2026/01/25f40bk.pdf#page=5",
    )
    defined_for = StateCode.AL

    def formula(person, period, parameters):
        is_dependent = person("is_tax_unit_dependent", period)
        return ~is_dependent * person("gambling_winnings", period)
