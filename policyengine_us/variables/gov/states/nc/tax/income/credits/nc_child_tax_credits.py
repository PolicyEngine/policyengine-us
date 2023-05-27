from policyengine_us.model_api import *

class nc_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "NC CTC"
    definition_period = YEAR
    unit = USD
    documentation = "North Carolina Tax Credit"
    reference = "https://www.ncdor.gov/taxes-forms/individual-income-tax/credit-children"
    defined_for = NCDOR

    def formula()