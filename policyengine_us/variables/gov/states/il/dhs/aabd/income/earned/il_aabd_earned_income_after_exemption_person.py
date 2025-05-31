from policyengine_us.model_api import *


class il_aabd_earned_income_after_exemption_person(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Illinois Aid to the Aged, Blind or Disabled (AABD) earned income after exemption per person"
    reference = (
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-113.120",
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.dhs.aabd.income.exemption
        gross_earned_income = person("il_aabd_gross_earned_income", period)
        expense_exemption = person("il_aabd_expense_exemption_person", period)
        adjusted_income = max_(gross_earned_income - expense_exemption, 0)
        flat_exemption_excess = person(
            "il_aabd_flat_exemption_excess_over_unearned_income", period
        )
        income_after_flat_exemption = max_(
            adjusted_income - flat_exemption_excess, 0
        )

        blind = person("is_blind", period)
        exemption = where(
            blind,
            p.blind.calc(income_after_flat_exemption),
            p.elderly_or_disabled.calc(income_after_flat_exemption),
        )
        return income_after_flat_exemption - exemption
