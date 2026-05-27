from policyengine_us.model_api import *


class or_statewide_transit_taxable_wages(Variable):
    value_type = float
    entity = Person
    label = "Oregon statewide transit taxable wages"
    documentation = (
        "Wages subject to Oregon statewide transit tax withholding, following "
        "the income tax withholding wage base."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.OR

    def formula(person, period, parameters):
        return person("irs_employment_income", period)
