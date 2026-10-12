from policyengine_us.model_api import *


class salt_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "SALT deduction"
    unit = USD
    documentation = (
        "State and local taxes plus real estate tax deduction from taxable income."
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/164"

    def formula(tax_unit, period, parameters):
        salt = tax_unit("salt", period)
        p = parameters(period).gov.simulation
        if p.limit_itemized_deductions_to_taxable_income:
            agi = tax_unit("adjusted_gross_income", period)
            exemptions = tax_unit("exemptions", period)
            salt = min_(salt, max_(0, agi - exemptions))
        cap = tax_unit("salt_cap", period)
        return min_(cap, salt)
