from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.id.dhw.aabd.id_aabd_living_arrangement import (
    IDAAbdLivingArrangement,
)
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._ssi_countable_income_without_loss_offset import (
    ssi_countable_income_without_loss_offset,
)


class id_aabd(Variable):
    value_type = float
    entity = Person
    label = "Idaho AABD cash payment"
    unit = USD
    definition_period = MONTH
    defined_for = "id_aabd_eligible"
    reference = (
        # PDF pages 34, 41
        "https://adminrules.idaho.gov/rules/current/16/160305.pdf#page=34",
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
        # IDAPA 16.03.05.403.06 disallows "Loss of Farm Income Subtracted
        # From Other Income", so a net farm loss counts as zero. Other
        # self-employment losses still net against other income as in SSI.
        countable_income = ssi_countable_income_without_loss_offset(
            person, period, parameters, ["farm_operations_income"]
        )
        financial_need = max_(0, per_person_allowance - countable_income)
        return min_(financial_need, per_person_max)
