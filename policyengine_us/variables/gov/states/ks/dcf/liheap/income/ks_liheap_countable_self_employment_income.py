from policyengine_us.model_api import *


class ks_liheap_countable_self_employment_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "Kansas LIEAP countable self-employment income"
    defined_for = StateCode.KS
    reference = (
        "https://content.dcf.ks.gov/ees/KEESM/Robo10-24/Robo_10_01_24/keesm13360.htm",
        "https://content.dcf.ks.gov/ees/KEESM/Robo01-26/Robo_01_01_26/keesm13360.htm",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ks.dcf.liheap.income
        gross = person("ks_liheap_self_employment_gross_income", period)
        expenses = person("ks_liheap_self_employment_expenses", period)
        deduction = max_(gross * p.self_employment_expense_rate, expenses)
        # Tax-net earnings cannot identify gross receipts or allowable costs.
        net_fallback = 0
        for source in p.sources.self_employment:
            net_fallback = net_fallback + max_(person(source, period), 0)
        return where(gross >= 0, max_(gross - deduction, 0), net_fallback)
