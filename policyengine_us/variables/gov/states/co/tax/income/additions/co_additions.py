from policyengine_us.model_api import *


class co_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado additions to federal AGI"
    unit = USD
    definition_period = YEAR
    reference = (
        "",
        ""
    )
    defined_for = StateCode.CO
    adds = "gov.states.co.tax.income.additions.sources"
    