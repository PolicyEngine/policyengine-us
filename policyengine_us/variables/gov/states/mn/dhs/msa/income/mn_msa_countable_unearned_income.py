from policyengine_us.model_api import *


class mn_msa_countable_unearned_income(Variable):
    value_type = float
    entity = Person
    label = "Minnesota Supplemental Aid countable unearned income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MN
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256D.44",
        "https://www.house.mn.gov/hrd/pubs/pap_MSA.pdf#page=3",
    )

    def formula(person, period, parameters):
        gross_unearned = add(
            person,
            period,
            [
                "ssi_unearned_income",
                "ssi_unearned_income_deemed_from_ineligible_spouse",
                "ssi_unearned_income_deemed_from_ineligible_parent",
            ],
        )
        general = parameters(period).gov.states.mn.dhs.msa.disregard.general
        arrangement = person("mn_msa_payment_category", period)
        LA = arrangement.possible_values
        is_couple = (arrangement == LA.COUPLE_LIVING_ALONE) | (
            arrangement == LA.COUPLE_LIVING_WITH_OTHERS
        )
        # Couples: aggregate at marital unit, apply $20 once, split 50/50.
        couple_countable = (
            max_(person.marital_unit.sum(gross_unearned) - general, 0) / 2
        )
        individual_countable = max_(gross_unearned - general, 0)
        return where(is_couple, couple_countable, individual_countable)
