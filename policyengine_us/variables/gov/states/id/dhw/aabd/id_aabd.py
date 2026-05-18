from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.id.dhw.aabd.id_aabd_living_arrangement import (
    IDAAbdLivingArrangement,
)


class id_aabd(Variable):
    value_type = float
    entity = Person
    label = "Idaho AABD cash payment"
    unit = USD
    definition_period = MONTH
    defined_for = "id_aabd_eligible"
    reference = (
        "https://adminrules.idaho.gov/rules/current/16/160305.pdf#page=41",
        "https://www.law.cornell.edu/regulations/idaho/IDAPA-16.03.05.514",
    )

    def formula(person, period, parameters):
        la = person("id_aabd_living_arrangement", period)
        p = parameters(period).gov.states.id.dhw.aabd.payment
        LA = IDAAbdLivingArrangement

        basic_allowance = p.basic_allowance[la]
        max_payment = p.amount[la]

        # Couples: regulation defines combined amounts (Section 501.02)
        # Both spouses are AABD participants, each gets half
        is_couple = la == LA.COUPLE
        per_person_allowance = where(is_couple, basic_allowance / 2, basic_allowance)
        per_person_max = where(is_couple, max_payment / 2, max_payment)

        # AABD cash = basic allowance - countable income, capped at max
        # (Section 514). Idaho mirrors SSI disregards (Sections 540-546).
        countable_income = person("ssi_countable_income", period)
        financial_need = max_(0, per_person_allowance - countable_income)
        return min_(financial_need, per_person_max)
