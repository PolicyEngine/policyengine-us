from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.wv.tax.income.credits.sctc.wv_sctc_eligible import (
    _sctc_eligibility_facts,
)


class wv_sctc_eligibility_available(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "West Virginia SCTC eligibility can be determined"
    reference = (
        "https://code.wvlegislature.gov/11-21-21/",
        "https://tax.wv.gov/Documents/PIT/2025/it140.PersonalIncomeTaxFormsAndInstructions.2025.pdf#page=36",
    )
    defined_for = StateCode.WV

    def formula_2025_01_01(tax_unit, period, parameters):
        known_ineligible, known_eligible = _sctc_eligibility_facts(
            tax_unit, period, parameters
        )
        return known_ineligible | known_eligible
