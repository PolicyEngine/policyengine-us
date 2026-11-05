from policyengine_us.model_api import *


class federal_income_tax_in_force(Variable):
    value_type = bool
    entity = Household
    label = "federal income tax in force"
    documentation = (
        "False in a year the contributed parameter abolishing the federal "
        "income tax is on."
    )
    definition_period = YEAR
    default_value = True

    def formula(household, period, parameters):
        abolished = parameters(
            period
        ).gov.contrib.ubi_center.flat_tax.abolish_federal_income_tax
        return np.ones(household.count, dtype=bool) * (not abolished)
