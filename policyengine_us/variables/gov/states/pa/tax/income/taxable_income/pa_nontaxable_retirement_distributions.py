from policyengine_us.model_api import *


class pa_nontaxable_retirement_distributions(Variable):
    value_type = float
    entity = Person
    label = "Retirement distributions taxable by US but not by PA"
    unit = USD
    documentation = (
        "US taxable distributions from IRAs and eligible employer retirement "
        "plans (401(k), 403(b), SEP, Keogh) excluded from PA compensation "
        "once the recipient has reached Pennsylvania's qualifying retirement "
        "age. 61 Pa. Code Sec. 101.6 treats IRAs, SEPs, Keogh plans and "
        "federally qualified employee pension plans alike: distributions made "
        "on or after retirement after reaching a specific age (or a stated "
        "period of employment) are not taxable compensation."
    )
    definition_period = YEAR
    reference = (
        # PA PIT Guide - Gross Compensation (old age or retirement benefits).
        "https://www.pa.gov/agencies/revenue/forms-and-publications/"
        "pa-personal-income-tax-guide/gross-compensation.html",
        # 61 Pa. Code Sec. 101.6 - Compensation (old age or retirement plans).
        "https://www.pacodeandbulletin.gov/Display/pacode?file=/secure/pacode/data/061/chapter101/s101.6.html",
        # PA DOR 1099-R FAQ (Code 7 normal distribution from an eligible plan).
        "https://revenue-pa.custhelp.com/app/answers/detail/a_id/1470/",
    )
    defined_for = StateCode.PA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.pa.tax.income
        retired = person("age", period) >= p.retirement_age_threshold
        distributions = add(
            person, period, p.nontaxable_retirement_distribution_sources
        )
        return where(retired, distributions, 0)
