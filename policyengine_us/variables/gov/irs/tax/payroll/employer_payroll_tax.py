from policyengine_us.model_api import *


class employer_payroll_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "employer-side payroll tax"
    definition_period = YEAR
    unit = USD

    def formula(tax_unit, period, parameters):
        return add(
            tax_unit,
            period,
            [
                "employer_social_security_tax",
                "employer_medicare_tax",
            ],
        )
