from policyengine_us.model_api import *


class ia_gambling_winnings(Variable):
    value_type = float
    entity = Person
    label = "Iowa gambling winnings"
    unit = USD
    documentation = (
        "Gambling winnings reported on IA 1040 line 13 by the tax unit's "
        "head or spouse, for the returns before 2023 that start from Iowa "
        "gross income. A dependent reports their own winnings on their own "
        "return."
    )
    definition_period = YEAR
    reference = (
        "https://revenue.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdf#page=1",
        "https://revenue.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdf#page=1",
    )
    defined_for = StateCode.IA

    def formula(person, period, parameters):
        is_dependent = person("is_tax_unit_dependent", period)
        return ~is_dependent * person("gambling_winnings", period)
