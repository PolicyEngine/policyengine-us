from policyengine_us.model_api import *


class dc_employer_paid_leave_tax(Variable):
    value_type = float
    entity = Person
    label = "District of Columbia employer paid leave tax"
    documentation = "Employer-side District of Columbia Paid Family Leave tax."
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.DC

    def formula(person, period, parameters):
        return person("dc_employer_paid_leave_tax_rate", period) * person(
            "dc_paid_leave_taxable_wages", period
        )
