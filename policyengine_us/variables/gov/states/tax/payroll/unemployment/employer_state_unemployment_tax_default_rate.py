from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.payroll.unemployment._jurisdictions import (
    select_state_unemployment_tax_parameter,
)


class employer_state_unemployment_tax_default_rate(Variable):
    value_type = float
    entity = Person
    label = "Default employer state unemployment tax rate"
    documentation = (
        "Default employer-side state unemployment tax rate. Uses the state's "
        "published new-employer rate when a single statewide rate exists, and "
        "falls back to the reported average tax rate on taxable wages when the "
        "state uses industry-average or other employer-specific schedules."
    )
    definition_period = YEAR
    unit = "/1"

    def formula(person, period, parameters):
        return select_state_unemployment_tax_parameter(
            person, period, parameters, "default_rate"
        )
