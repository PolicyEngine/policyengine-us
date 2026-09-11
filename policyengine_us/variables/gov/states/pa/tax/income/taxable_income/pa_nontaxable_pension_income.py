from policyengine_us.model_api import *


class pa_nontaxable_pension_income(Variable):
    value_type = float
    entity = Person
    label = "Pension income taxable by US but not by PA"
    unit = USD
    documentation = "US taxable pension income excluded from PA AGI."
    definition_period = YEAR
    reference = (
        # PA PIT Guide - Gross Compensation (old age or retirement benefits).
        "https://www.pa.gov/agencies/revenue/forms-and-publications/"
        "pa-personal-income-tax-guide/gross-compensation.html",
        # 61 Pa. Code Sec. 101.6 - Compensation (old age or retirement plans).
        "https://www.pacodeandbulletin.gov/Display/pacode?file=/secure/pacode/data/061/chapter101/s101.6.html",
    )
    defined_for = StateCode.PA

    def formula(person, period, parameters):
        # 61 Pa. Code Sec. 101.6 treats federally qualified employee pension
        # plans the same as IRAs, SEPs, and Keogh plans: distributions after
        # reaching the plan's retirement age are not taxable compensation. Use
        # the same PA retirement-age threshold as pa_nontaxable_retirement_
        # distributions rather than the age-65 is_retired default.
        p = parameters(period).gov.states.pa.tax.income
        retired = person("age", period) >= p.retirement_age_threshold
        us_taxable_pension = person("taxable_pension_income", period)
        return where(retired, us_taxable_pension, 0)
