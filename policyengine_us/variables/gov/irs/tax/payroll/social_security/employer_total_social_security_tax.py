from policyengine_us.model_api import *


class employer_total_social_security_tax(Variable):
    value_type = float
    entity = Person
    label = "Employer total Social Security payroll tax"
    documentation = (
        "Employer-level Social Security payroll tax liability from aggregate "
        "taxable earnings inputs."
    )
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.payroll.social_security.rate
        taxable_earnings = person(
            "employer_total_taxable_earnings_for_social_security", period
        )
        return p.employer * taxable_earnings
