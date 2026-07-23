from policyengine_us.model_api import *


class taxable_alimony_income(Variable):
    value_type = float
    entity = Person
    label = "Taxable alimony income"
    unit = USD
    documentation = "Alimony income included in gross income, for divorces executed before the TCJA cutoff year."
    definition_period = YEAR
    reference = "https://www.irs.gov/taxtopics/tc452"

    def formula(person, period, parameters):
        alimony_income = person("alimony_income", period)
        divorce_year = person("divorce_year", period)
        p = parameters(period).gov.irs.ald.alimony_expense
        # Mirror the payer-side deduction: alimony from divorces before the TCJA
        # cutoff (2019) is taxable to the recipient; later divorces are not.
        taxable = p.divorce_year_threshold.calc(divorce_year)
        return alimony_income * taxable
