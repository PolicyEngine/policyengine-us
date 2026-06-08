from policyengine_us.model_api import *


class hi_ccap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Hawaii CCAP countable monthly income"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.HI
    reference = "https://humanservices.hawaii.gov/bessd/files/2013/01/HAR-17-798.2-Child-Care-Services-Rules.pdf#page=19"

    adds = "gov.states.hi.bessd.ccap.income.countable_income.sources"
