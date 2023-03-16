from policyengine_us.model_api import *


class oh_agi_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "OH total additions to AGI"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.OH


    def formula(tax_unit, period, parameters):
        investment_in_529_plan = tax_unit("investment_in_529_plan", period)
        #return investment_in_529_plan + oh_bonus_depreciation_add_back + oh_other_add_backs
        #or
        #adds = ["investment_in_529_plan", "oh_bonus_depreciation_add_back", "oh_other_add_backs"]
        
