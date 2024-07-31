from policyengine_us.model_api import *


class ct_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CT

    adds = "gov.states.ct.tax.income.additions.additions"
