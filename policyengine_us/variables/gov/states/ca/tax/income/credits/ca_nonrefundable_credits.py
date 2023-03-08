from policyengine_us.model_api import *


class ca_nonrefundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "California nonrefundable income tax credits"
    defined_for = StateCode.CA
    unit = USD
    definition_period = YEAR
    reference = "https://www.ftb.ca.gov/forms/Search/Home/Confirmation"

    adds = "gov.states.ca.tax.income.credits.nonrefundable"
