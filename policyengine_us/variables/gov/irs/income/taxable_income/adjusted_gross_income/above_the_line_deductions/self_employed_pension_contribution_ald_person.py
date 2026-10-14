from policyengine_us.model_api import *


class self_employed_pension_contribution_ald_person(Variable):
    value_type = float
    entity = Person
    label = "Self-employed pension contribution ALD for each person"
    unit = USD
    documentation = (
        "Personal above-the-line deduction for self-employed SEP, SIMPLE and "
        "qualified plan contributions (Schedule 1 line 16), capped at the "
        "Pub. 560 maximum deductible contribution."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/62#a_6",
        "https://www.law.cornell.edu/uscode/text/26/404#a_8_C",
        "https://www.irs.gov/pub/irs-pdf/p560.pdf#page=39",
    )

    def formula(person, period, parameters):
        contributions = person("self_employed_pension_contributions", period)
        # The limit applies again here so the deduction stays within it when
        # contributions are supplied directly rather than from desired
        # contributions.
        limit = person("self_employed_pension_contribution_limit", period)
        return min_(contributions, limit)
