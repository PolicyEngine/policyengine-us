from policyengine_us.model_api import *


class pa_nontaxable_pension_income(Variable):
    value_type = float
    entity = Person
    label = "Pension income taxable by US but not by PA"
    unit = USD
    documentation = (
        "US taxable pension income excluded from PA AGI. Pennsylvania sets no "
        "statutory age for employer pension plans: 61 Pa. Code Sec. "
        "101.6(c)(8) and the PA-40 instructions exempt payments made upon or "
        "after the recipient retires from service after reaching the plan's "
        "own age or stated period of employment. The model does not hold plan "
        "terms, so it approximates that condition with the age the PA "
        "Personal Income Tax Guide applies to plans that are not employer "
        "provided and have no specific retirement criteria, such as an IRA. "
        "Employer pension recipients below that age who have already met "
        "their plan's retirement conditions are still taxed by the model."
    )
    definition_period = YEAR
    reference = (
        # PA PIT Guide - Gross Compensation (old age or retirement benefits).
        "https://www.pa.gov/agencies/revenue/forms-and-publications/"
        "pa-personal-income-tax-guide/gross-compensation.html",
        # 61 Pa. Code Sec. 101.6 - Compensation (old age or retirement plans).
        "https://www.pacodeandbulletin.gov/Display/pacode?file=/secure/pacode/data/061/chapter101/s101.6.html",
        # 2023 PA-40 IN - Retirement, pensions, and deferred compensation.
        "https://www.pa.gov/content/dam/copapwp-pagov/en/revenue/documents/formsandpublications/formsforindividuals/pit/documents/2023/2023_pa-40in.pdf",
    )
    defined_for = StateCode.PA

    def formula(person, period, parameters):
        # Proxy for having met the plan's retirement conditions. See the
        # documentation above: this is an approximation, not a statutory age.
        p = parameters(period).gov.states.pa.tax.income
        retired = person("age", period) >= p.retirement_age_threshold
        us_taxable_pension = person("taxable_pension_income", period)
        return where(retired, us_taxable_pension, 0)
