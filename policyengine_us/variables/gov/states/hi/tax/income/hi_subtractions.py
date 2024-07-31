from policyengine_us.model_api import *


class hi_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii subtractions from federal adjusted gross income"
    reference = "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=13"
    defined_for = StateCode.HI
    unit = USD
    definition_period = YEAR
    adds = "gov.states.hi.tax.income.subtractions.subtractions"
