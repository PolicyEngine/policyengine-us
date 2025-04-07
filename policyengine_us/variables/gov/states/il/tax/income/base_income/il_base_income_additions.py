from policyengine_us.model_api import *


class il_base_income_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL base income additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.IL

    adds = "gov.states.il.tax.income.base.additions"
