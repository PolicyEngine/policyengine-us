from policyengine_us.model_api import *


class alimony_expense_ald(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alimony expense ALD"
    unit = USD
    documentation = "Above-the-line deduction from gross income for alimony expenses."
    definition_period = YEAR
    reference = "https://www.irs.gov/taxtopics/tc452"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        divorce_year = person("divorce_year", period)
        alimony_expense = person("alimony_expense", period)
        p = parameters(period).gov.irs.ald.alimony_expense
        eligible_person = p.divorce_year_threshold.calc(divorce_year)
        # A tax unit dependent who pays alimony deducts it on their own return.
        not_dependent = ~person("is_tax_unit_dependent", period)
        return tax_unit.sum(alimony_expense * eligible_person * not_dependent)
