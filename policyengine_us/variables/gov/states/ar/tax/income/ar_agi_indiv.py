from policyengine_us.model_api import *


class ar_agi_indiv(Variable):
    value_type = float
    entity = Person
    label = "Arkansas adjusted gross income for each individual"
    documentation = (
        "Arkansas adjusted gross income in the head's and spouse's columns of "
        "the return. A tax unit dependent's income belongs on the dependent's "
        "own Arkansas return, so a dependent's column is zero."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dfa.arkansas.gov/wp-content/uploads/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=14",
        # PDF pages 10, 12: who must file (the gross income minimums apply to
        # each person, dependents included), and Filing Status 4 (the
        # primary's income in column A, the spouse's in column B)
        "https://www.dfa.arkansas.gov/wp-content/uploads/2025_AR1000F_and_AR1000NR_Instructions.pdf#page=10",
        # Ark. Code 26-51-801(a)-(b): every person over the gross income
        # minimum files a return; only spouses may combine their income on
        # a single joint return.
        "https://codes.findlaw.com/ar/title-26-taxation/ar-code-sect-26-51-801/",
    )
    defined_for = StateCode.AR

    def formula(person, period, parameters):
        gross_income = person("ar_gross_income_indiv", period)
        income_exemptions = person("ar_exemptions", period)
        net_income = max_(gross_income - income_exemptions, 0)
        # Each spouse's column holds their own income. A dependent's income
        # goes on the dependent's own return, not on the filer's.
        is_dependent = person("is_tax_unit_dependent", period)
        return where(is_dependent, 0, net_income)
