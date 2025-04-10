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
        p = parameters(period).gov.states.il.dhs.aabd
        gross_earned_income = person("il_aabd_gross_earned_income", period)
        # Determine demographic status
        elderly = person("is_ssi_aged", period)
        blind = person("is_blind", period)
        disabled = person("is_ssi_disabled", period)
        elderly_or_disabled = elderly | disabled
        income_after_flat_exemption = max_(
            gross_earned_income - p.income.exemption.flat, 0
        )
        return select(
            [blind, elderly_or_disabled],
            [
                income_after_flat_exemption
                - p.income.exemption.blind.calc(income_after_flat_exemption),
                income_after_flat_exemption
                - p.income.exemption.elderly_or_disabled.calc(
                    income_after_flat_exemption
                ),
            ],
            default=0,
        )
