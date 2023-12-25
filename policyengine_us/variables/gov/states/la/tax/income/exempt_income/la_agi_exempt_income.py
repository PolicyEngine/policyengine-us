from policyengine_us.model_api import *


class la_agi_exempt_income(Variable):
    value_type = float
    entity = TaxUnit
    label = (
        "Louisiana income that is exempt from the adjusted gross income income"
    )
    defined_for = StateCode.LA
    unit = USD
    definition_period = YEAR

    adds = "gov.states.la.tax.income.exempt_income.exempt_income"
