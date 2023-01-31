from policyengine_us.model_api import *


class ut_total_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "UT total income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.UT

    adds = ["adjusted_gross_income", "ut_additions_to_income"]
