from policyengine_us.model_api import *


class estate_net_investment_income(Variable):
    value_type = float
    entity = Person
    label = "Net investment income from estates and trusts"
    unit = USD
    documentation = (
        "Estate and trust income counted in net investment income: the "
        "Schedule E Part III amount that Form 8960 line 4a includes, plus the "
        "Schedule K-1 (Form 1041) box 14 code H adjustment taken on line 7. "
        "A tax unit dependent's estate and trust income belongs on the "
        "dependent's own return, as in irs_gross_income, so it is excluded."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/1411#c_1_A",
        "https://www.irs.gov/pub/irs-prior/i8960--2024.pdf#page=7",
    )

    def formula(person, period, parameters):
        estate_income = person("estate_income", period)
        adjustment = person("estate_income_net_investment_income_adjustment", period)
        not_dependent = ~person("is_tax_unit_dependent", period)
        return not_dependent * (estate_income + adjustment)
