from policyengine_us.model_api import *


class ny_paid_family_leave_tax(Variable):
    value_type = float
    entity = Person
    label = "New York Paid Family Leave payroll tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NY
    reference = {
        "title": "New York State Paid Family Leave",
        "href": "https://paidfamilyleave.ny.gov/cost",
    }

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ny.tax.payroll.paid_family_leave
        gross_wages = person("irs_employment_income", period)
        uncapped_tax = gross_wages * p.rate
        max_contribution = p.maximum_annual_contribution
        return min_(uncapped_tax, max_contribution)
