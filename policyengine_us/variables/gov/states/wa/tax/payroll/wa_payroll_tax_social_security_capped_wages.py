from policyengine_us.model_api import *


class wa_payroll_tax_social_security_capped_wages(Variable):
    value_type = float
    entity = Person
    label = "Washington payroll tax Social Security capped wages"
    documentation = (
        "Washington paid leave gross wages, excluding tips, capped at the "
        "Social Security contribution and benefit base."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.WA
    reference = "https://paidleave.wa.gov/employer-roles-responsibilities/"

    def formula(person, period, parameters):
        return min_(
            person("wa_payroll_tax_gross_wages", period),
            parameters(period).gov.irs.payroll.social_security.cap,
        )
