from policyengine_us.model_api import *


class wa_long_term_care_taxable_wages(Variable):
    value_type = float
    entity = Person
    label = "Washington WA Cares taxable wages"
    documentation = (
        "Wages subject to WA Cares premiums, excluding tips and including "
        "federal pre-tax payroll deductions."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.WA

    def formula(person, period, parameters):
        return max_(
            0,
            person("employment_income", period) - person("tip_income", period),
        )
