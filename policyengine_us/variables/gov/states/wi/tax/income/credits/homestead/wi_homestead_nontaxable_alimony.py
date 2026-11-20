from policyengine_us.model_api import *


class wi_homestead_nontaxable_alimony(Variable):
    value_type = float
    entity = Person
    label = "Wisconsin homestead credit maintenance outside adjusted gross income"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Alimony (maintenance) received that federal gross income leaves out, "
        "which Wisconsin counts in homestead credit household income (Wis. "
        "Stat. 71.52(6), 'maintenance payments'; Schedule H line 9i). "
        "Adjusted gross income already holds maintenance under a divorce or "
        "separation instrument executed before 2019, so only the rest is "
        "added and maintenance counts once."
    )
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/viii/52/6",
        "https://www.revenue.wi.gov/TaxForms2025/2025-ScheduleH-inst.pdf#page=14",
    )
    defined_for = StateCode.WI

    def formula(person, period, parameters):
        alimony = person("alimony_income", period)
        sources = parameters(period).gov.irs.gross_income.sources
        # Federal gross income holds taxable_alimony_income, the alimony under
        # pre-2019 divorce instruments, when that is a listed source.
        if "taxable_alimony_income" in sources:
            taxable_alimony = person("taxable_alimony_income", period)
            return max_(alimony - taxable_alimony, 0)
        return alimony
