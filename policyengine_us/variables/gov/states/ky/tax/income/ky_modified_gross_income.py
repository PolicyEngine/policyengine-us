from policyengine_us.model_api import *


class ky_modified_gross_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky modified gross income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.KY
    adds = "gov.states.ky.tax.income.modified_gross_income.sources"