from policyengine_us.model_api import *

class id_retirement_benefit_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "ID retirement benefit deduction"
    unit = USD
    definition_period = YEAR

    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):
        