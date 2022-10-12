from policyengine_us.model_api import *


class or_tax_before_credits_in_prior_year(Variable):
    value_type = float
    entity = TaxUnit
    label = "OR tax before credits in prior year"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.OR
