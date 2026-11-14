from policyengine_us.model_api import *


class federal_scholarship_qualified_contributions_eligible(Variable):
    value_type = float
    entity = Person
    label = "Eligible qualified scholarship cash contributions on this tax return"
    unit = USD
    definition_period = YEAR
    reference = "https://uscode.house.gov/us/usc/t26/s25F/"

    def formula_2027_01_01(person, period, parameters):
        if not parameters(period).gov.irs.credits.federal_scholarship.in_effect:
            return np.zeros(person.count)
        qualified = person("federal_scholarship_qualified_contributions", period)
        cash = person("resolved_charitable_cash_donations_50_pct", period)
        filer = person("is_tax_unit_head", period) | person(
            "is_tax_unit_spouse", period
        )
        return where(filer, min_(max_(qualified, 0), max_(cash, 0)), 0)
