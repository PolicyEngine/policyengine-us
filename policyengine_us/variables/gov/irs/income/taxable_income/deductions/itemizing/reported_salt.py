from policyengine_us.model_api import *


class reported_salt(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Reported State and local sales or income tax and real estate taxes subject to the SALT deduction limited to taxable income"
    unit = USD

    def formula(tax_unit, period, parameters):
        salt = tax_unit("salt", period)
        p = parameters(period).gov.simulation
        if p.limit_itemized_deductions_to_taxable_income:
            agi = tax_unit("adjusted_gross_income", period)
            exemptions = tax_unit("exemptions", period)
            agi_less_exemptions = max_(0, agi - exemptions)
            return min_(salt, agi_less_exemptions)
        return salt
