from policyengine_us.model_api import *


class la_aged_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana aged exemption"
    unit = USD
    definition_period = YEAR
    reference = "https://www.legis.la.gov/legis/Law.aspx?d=102133"
    defined_for = StateCode.LA

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        pension_income = person("pension_income", period)
        age = person("age", period)
        p = parameters(period).gov.states.la.tax.income.exemptions.aged
        meets_age_test = age >= p.thresholds[-1]
        deductible_pensions = meets_age_test * min_(
            pension_income, p.amounts[-1]
        )

        return tax_unit.sum(deductible_pensions)
