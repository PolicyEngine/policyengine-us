from policyengine_us.model_api import *


class ar_agi_joint(Variable):
    value_type = float
    entity = Person
    label = "Arkansas adjusted gross income for each individual"
    documentation = (
        "Arkansas adjusted gross income of the head and spouse on a return "
        "that is not married filing separately on the same return. A tax "
        "unit dependent's income belongs on the dependent's own Arkansas "
        "return, so a dependent's amount is zero."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dfa.arkansas.gov/wp-content/uploads/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=14",
        # Ark. Code 26-51-801(a)-(b): every person over the gross income
        # minimum files a return; only spouses may combine their income on
        # a single joint return.
        "https://codes.findlaw.com/ar/title-26-taxation/ar-code-sect-26-51-801/",
        # Who must file: the gross income minimums apply to each person,
        # dependents included
        "https://www.dfa.arkansas.gov/wp-content/uploads/2025_AR1000F_and_AR1000NR_Instructions.pdf#page=10",
    )
    defined_for = StateCode.AR

    def formula(person, period, parameters):
        gross_income = person("ar_gross_income_joint", period)
        income_exemptions = person("ar_exemptions", period)
        net_income = gross_income - income_exemptions
        # On a return that is not married filing separately on the same
        # return, all income goes in Column A, so one spouse's loss offsets
        # the other's income; the tax unit total is floored at zero when it
        # is used as a tax base. A dependent's income goes on the
        # dependent's own return, not on the filer's.
        is_dependent = person("is_tax_unit_dependent", period)
        return where(is_dependent, 0, net_income)
