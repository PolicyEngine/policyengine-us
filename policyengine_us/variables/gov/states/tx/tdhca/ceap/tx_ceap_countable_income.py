from policyengine_us.model_api import *


class tx_ceap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Texas Comprehensive Energy Assistance Program (CEAP) countable income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.TX
    reference = (
        "https://www.tdhca.texas.gov/sites/default/files/community-affairs/docs/26-LIHEAP-Plan-Amend1.pdf#page=8",
        "https://www.law.cornell.edu/regulations/texas/10-Tex-Admin-Code-SS-6-4",
    )
    adds = ["tx_ceap_countable_income_person", "tanf"]
