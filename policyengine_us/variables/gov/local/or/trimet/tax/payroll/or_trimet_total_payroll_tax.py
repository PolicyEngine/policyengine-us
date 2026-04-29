from policyengine_us.model_api import *


class or_trimet_total_payroll_tax(Variable):
    value_type = float
    entity = Person
    label = "Total TriMet payroll tax"
    documentation = (
        "Employer-side TriMet transit payroll tax liability from aggregate "
        "district wage inputs."
    )
    definition_period = YEAR
    unit = USD
    reference = (
        "https://www.oregon.gov/dor/programs/businesses/Pages/TriMet-Transit.aspx"
    )

    def formula(person, period, parameters):
        state_code = person.household("state_code", period)
        taxable_wages = person("employer_total_or_trimet_taxable_wages", period)
        rate = parameters(period).gov.local["or"].trimet.tax.payroll.rate
        return where(state_code == StateCode.OR, rate * taxable_wages, 0)
