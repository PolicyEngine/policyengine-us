from policyengine_us.model_api import *


class nm_ccap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "New Mexico CCAP countable income"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.NM
    reference = "https://www.srca.nm.gov/parts/title08/08.015.0002.html"

    adds = "gov.states.nm.ececd.ccap.income.countable_income.sources"
