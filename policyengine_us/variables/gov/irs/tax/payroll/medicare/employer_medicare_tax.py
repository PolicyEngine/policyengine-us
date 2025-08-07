from policyengine_us.model_api import *


class employer_medicare_tax(Variable):
    value_type = float
    entity = Person
    label = "Employer-side health insurance payroll tax"
    documentation = (
        "Total liability for employer-side health insurance payroll tax."
    )
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.payroll.medicare.rate
        return p.employer * person("payroll_tax_gross_wages", period)
