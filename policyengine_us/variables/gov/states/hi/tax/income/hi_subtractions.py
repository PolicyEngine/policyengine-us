from policyengine_us.model_api import *


class hi_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii subtractions from Federal AGI"
    reference = "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=13"
    defined_for = StateCode.HI
    unit = USD
    definition_period = YEAR
    subtracts = "gov.states.hi.tax.income.subtractions"
