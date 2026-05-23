from policyengine_us.model_api import *


class state_payroll_tax_social_security_capped_wages(Variable):
    value_type = float
    entity = Person
    label = "state payroll tax Social Security capped wages"
    documentation = (
        "Gross employment wages capped at the Social Security contribution and "
        "benefit base for state payroll taxes that use that cap but do not "
        "exclude federal FICA pre-tax payroll deductions."
    )
    definition_period = YEAR
    unit = USD
    reference = "https://www.ssa.gov/oact/cola/cbb.html"

    def formula(person, period, parameters):
        return min_(
            person("state_payroll_tax_gross_wages", period),
            parameters(period).gov.irs.payroll.social_security.cap,
        )
