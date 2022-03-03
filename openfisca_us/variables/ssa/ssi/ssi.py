from openfisca_us.model_api import *


class ssi(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = "Supplemental Security Income"
    label = "Supplemental Security Income"
    unit = USD

    def formula(person, period, parameters):
        abd = person("is_ssi_aged_blind_disabled", period)
        # If the spouse is aged, blind, or disabled, calculate as a couple.
        spouse_abd = person("is_spouse_ssi_aged_blind_disabled", period)
        amounts = parameters(period).ssi.amount
        amount = where(spouse_abd, amounts.couple, amounts.individual)
        countable_income = person("ssi_countable_income", period)
        amount_if_eligible = max_(amount - countable_income, 0)
        # Split with spouse if receiving as a couple.
        amount_if_eligible /= where(is_spouse_eligible, 2, 1)
        return eligible * amount_if_eligible
