from policyengine_us.model_api import *


class pa_tanf_gross_earned_income(Variable):
    value_type = float
    entity = Person
    label = "Pennsylvania TANF gross earned income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.PA
    reference = "55 Pa. Code Section 183.21 - Earned income"
    documentation = "Gross earned income from wages, tips, salary, commissions, bonuses, and self-employment profit, before any deductions or disregards. https://www.pacodeandbulletin.gov/Display/pacode?file=/secure/pacode/data/055/chapter183/s183.21.html"

    adds = "gov.hhs.tanf.cash.income.sources.earned"
