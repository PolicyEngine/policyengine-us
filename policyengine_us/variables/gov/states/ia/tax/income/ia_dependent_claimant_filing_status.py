from policyengine_us.model_api import *
from policyengine_us.variables.household.demographic.tax_unit.filing_status import (
    FilingStatus,
)


class ia_dependent_claimant_filing_status(Variable):
    value_type = Enum
    entity = Person
    possible_values = FilingStatus
    default_value = FilingStatus.SINGLE
    label = "Filing status of the person claiming this filer as a dependent"
    documentation = (
        "Selects the Iowa Code 422.5 income limit that applies to the "
        "claiming person: the larger one for a joint, head of household or "
        "surviving spouse return, the smaller one otherwise."
    )
    definition_period = YEAR
    defined_for = StateCode.IA
    reference = (
        "https://www.legis.iowa.gov/docs/code/2022/422.5.pdf#page=3",
        # PDF pages 1-2
        "https://www.legis.iowa.gov/docs/code/2024/422.5.pdf#page=1",
    )
