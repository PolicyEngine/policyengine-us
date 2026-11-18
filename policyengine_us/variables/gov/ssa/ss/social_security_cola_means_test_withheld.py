from policyengine_us.model_api import *
from policyengine_us.tools.social_security.means_test import tax_unit_withholding


class social_security_cola_means_test_withheld(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Social Security COLA prior-year income test"
    documentation = "Prior-tax-year MAGI strictly exceeds the CPI-U-indexed filing-group line. Beneficiary scope is applied separately."
    reference = "https://www.ssa.gov/OACT/solvency/provisions/cola.html"

    def formula(tax_unit, period, parameters):
        return tax_unit_withholding(tax_unit, period, parameters)
