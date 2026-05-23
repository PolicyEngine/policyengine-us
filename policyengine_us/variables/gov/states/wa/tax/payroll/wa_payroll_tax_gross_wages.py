from policyengine_us.model_api import *


class wa_payroll_tax_gross_wages(Variable):
    value_type = float
    entity = Person
    label = "Washington payroll tax gross wages"
    documentation = (
        "Gross wages for Washington paid leave and WA Cares premiums, excluding tips."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.WA
    reference = "https://paidleave.wa.gov/employer-roles-responsibilities/"

    def formula(person, period, parameters):
        return max_(
            0,
            person("employment_income", period) - person("tip_income", period),
        )
