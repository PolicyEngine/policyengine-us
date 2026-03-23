from policyengine_us.model_api import *


class id_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho standard deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID
    reference = "https://legislature.idaho.gov/statutesrules/idstat/title63/t63ch30/sect63-3022/"

    def formula(tax_unit, period, parameters):
        return tax_unit("standard_deduction", period)
