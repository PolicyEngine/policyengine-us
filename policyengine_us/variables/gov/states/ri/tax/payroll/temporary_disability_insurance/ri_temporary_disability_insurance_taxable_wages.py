from policyengine_us.model_api import *


class ri_temporary_disability_insurance_taxable_wages(Variable):
    value_type = float
    entity = Person
    label = "Rhode Island temporary disability insurance taxable wages"
    documentation = (
        "Wages subject to Rhode Island temporary disability insurance "
        "contributions, following the income tax wage base."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.RI

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ri.tax.payroll.temporary_disability_insurance
        return min_(person("irs_employment_income", period), p.taxable_wage_base)
