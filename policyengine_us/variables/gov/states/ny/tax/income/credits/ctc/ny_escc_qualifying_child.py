from policyengine_us.model_api import *


class ny_escc_qualifying_child(Variable):
    value_type = bool
    entity = Person
    label = "Qualifies as a child for NY Empire State Child Credit"
    documentation = (
        "Whether a child qualifies for the NY Empire State Child Credit. "
        "Unlike the federal CTC, NY allows children with ITINs to qualify "
        "for the enhanced ESCC (2025-2028)."
    )
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/606"
    defined_for = "is_tax_unit_dependent"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ny.tax.income.credits.ctc
        age = person("age", period)
        # NY ESCC allows both SSN and ITIN holders
        # (decoupled from federal CTC SSN requirement)
        has_valid_id = person("has_itin", period)  # has_itin includes SSN
        age_eligible = age < p.post_2024.amount.thresholds[-1]
        meets_minimum_age = age >= p.minimum_age
        return has_valid_id & age_eligible & meets_minimum_age
