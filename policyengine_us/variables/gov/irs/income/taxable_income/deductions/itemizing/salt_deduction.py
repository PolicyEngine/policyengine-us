from policyengine_us.model_api import *


class salt_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "SALT deduction"
    unit = USD
    documentation = "State and local taxes plus real estate tax deduction from taxable income."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/164"

    def formula(tax_unit, period, parameters):
        reported_salt = tax_unit("reported_salt", period)
        cap = tax_unit("salt_cap", period)
        return min_(cap, reported_salt)
