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
        p = parameters(period).gov.states.il.dhs.aabd.income
        gross_earned_income = person("il_aabd_gross_earned_income", period)
        # Determine demographic status
        age = person("monthly_age", period)
        elderly = age >= p.elderly_age_threshold
        blind = person("is_blind", period)
        disabled = person("is_ssi_disabled", period)
        elderly_or_disabled = elderly | disabled
        income_after_flat_exemption = max_(
            gross_earned_income - p.exemption.flat, 0
        )
        return select(
            [elderly_or_disabled, blind],
            [
                p.exemption.elderly_or_disabled.calc(
                    income_after_flat_exemption
                ),
                p.exemption.blind.calc(income_after_flat_exemption),
            ],
            default=0,
        )
