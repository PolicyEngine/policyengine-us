from policyengine_us.model_api import *


class tx_dta_csfp_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Income used for Texas CSFP direct eligibility"
    documentation = (
        "SPM unit income for Texas CSFP direct eligibility. The model retains its "
        "existing approximation pending a separate review of program exclusions."
    )
    reference = "https://squaremeals.org/Portals/8/FND%20Forms/Program%20Handbooks/CSFP_Section_3_Managing_Program_V700_260410.pdf#page=14"

    adds = "gov.states.tx.dta.csfp.income.sources"
