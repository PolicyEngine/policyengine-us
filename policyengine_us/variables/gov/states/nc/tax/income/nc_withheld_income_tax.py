from policyengine_us.model_api import *


class nc_withheld_income_tax(Variable):
    value_type = float
    entity = Person
    label = "North Carolina withheld income tax"
    defined_for = StateCode.NC
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        employment_income = person("irs_employment_income", period)
        p = parameters(period).gov.states.nc.tax.income
        # We apply the base standard deduction amount
        standard_deduction = p.deductions.standard.amount["SINGLE"]
        reduced_employment_income = max_(
            employment_income - standard_deduction, 0
        )
        return p.rate * reduced_employment_income
