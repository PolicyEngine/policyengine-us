from policyengine_us.model_api import *


class nj_wages(Variable):
    value_type = float
    entity = Person
    label = "New Jersey wages"
    unit = USD
    documentation = (
        "Wages, salaries and tips New Jersey taxes (NJ-1040 line 15, W-2 box "
        "16): employment income less 401(k) elective deferrals, which "
        "N.J.S.A. 54A:6-21 leaves out of gross income. Employee contributions "
        "to 403(b), 457 and SEP plans and to the federal Thrift Savings Plan "
        "stay in New Jersey wages, as do salary reduction and premium "
        "conversion cafeteria plan amounts."
    )
    definition_period = YEAR
    reference = (
        # N.J.S.A. 54A:6-21
        "https://law.justia.com/codes/new-jersey/title-54a/section-54a-6-21/",
        # 2025 NJ-1040 instructions, PDF pages 10-11: income New Jersey
        # taxes and does not tax, and line 15
        "https://www.nj.gov/treasury/taxation/pdf/current/1040i.pdf#page=10",
    )
    defined_for = StateCode.NJ

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nj.tax.income.gross_income
        employment_income = person("employment_income", period)
        excluded_deferrals = add(person, period, p.excluded_wage_deferrals)
        return max_(0, employment_income - excluded_deferrals)
