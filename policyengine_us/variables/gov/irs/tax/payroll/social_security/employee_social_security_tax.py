from policyengine_us.model_api import *


class employee_social_security_tax(Variable):
    value_type = float
    entity = Person
    label = "employee-side OASDI payroll tax"
    documentation = "Total liability for employee-side OASDI payroll tax."
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.payroll.social_security.rate
        return p.employee * person(
            "taxable_earnings_for_social_security", period
        )
