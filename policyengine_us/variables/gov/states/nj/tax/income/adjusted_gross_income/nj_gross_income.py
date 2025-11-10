from policyengine_us.model_api import *


class nj_gross_income(Variable):
    value_type = float
    entity = Person
    label = "New Jersey gross income"
    unit = USD
    documentation = "Gross income calculated from specific income categories per NJ statute, before additions and subtractions. This is built from gross income sources, not federal AGI."
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/new-jersey/title-54a/section-54a-5-1/",
        "https://www.nj.gov/treasury/taxation/pdf/current/1040.pdf",  # Lines 15-27
    )
    defined_for = StateCode.NJ

    def formula(person, period, parameters):
        # Build NJ gross income from specific income categories per NJ statute 54A:5-1
        # This corresponds to lines 15-27 on Form NJ-1040
        p = parameters(period).gov.states.nj.tax.income
        return add(person, period, p.gross_income_sources)
