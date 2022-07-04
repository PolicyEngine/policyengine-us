from openfisca_us.model_api import *

class il_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = ""
    
    def formula(tax_unit, period, parameters):
        federal_agi = tax_unit("adjusted_gross_income", period)
        il_add_backs = tax_unit("il_add_backs", period)
        il_deductions = tax_unit("il_deductions", period)
        il_exemptions = tax_unit("il_exemptions", period)

        return federal_agi + il_add_backs - il_deductions - il_exemptions