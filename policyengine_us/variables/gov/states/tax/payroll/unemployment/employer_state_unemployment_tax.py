from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.payroll.unemployment._jurisdictions import (
    STATE_EMPLOYER_UNEMPLOYMENT_TAX_VARIABLES,
)


class employer_state_unemployment_tax(Variable):
    value_type = float
    entity = Person
    label = "Employer state unemployment tax"
    documentation = (
        "Employer-side state unemployment insurance tax liability, aggregated "
        "from jurisdiction-specific variables and using household state as a "
        "proxy for work state."
    )
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        return add(person, period, STATE_EMPLOYER_UNEMPLOYMENT_TAX_VARIABLES)
