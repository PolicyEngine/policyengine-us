from policyengine_us.model_api import *


class wv_withheld_income_tax(Variable):
    value_type = float
    entity = Person
    label = "West Virginia withheld income tax"
    defined_for = StateCode.WV
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        employment_income = person("irs_employment_income", period)
        p = parameters(period).gov.states.wv.tax.income
        # Since West Virginia does not have a standard deduction, we apply the maximum
        # personal exemption amount
        personal_exmptions = p.exemptions.base_personal + p.exemptions.personal
        reduced_employment_income = max_(
            employment_income - personal_exmptions, 0
        )
        return p.rates.single.calc(reduced_employment_income)
