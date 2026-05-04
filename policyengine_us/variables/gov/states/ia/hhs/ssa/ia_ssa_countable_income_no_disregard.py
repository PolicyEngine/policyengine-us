from policyengine_us.model_api import *


class ia_ssa_countable_income_no_disregard(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Iowa SSA monthly countable income, without the SSI $20 general income disregard"
    unit = USD
    defined_for = StateCode.IA
    reference = (
        "https://hhs.iowa.gov/media/15607/download",
        "https://www.legis.iowa.gov/docs/iac/chapter/01-07-2026.441.52.pdf#page=2",
        "https://www.legis.iowa.gov/docs/iac/chapter/01-07-2026.441.177.pdf#page=2",
    )

    def formula(person, period, parameters):
        # GL 6-B-46 pp. 30, 36–38, 54–58: Iowa RCF, FLH-eligibility, and IHHRC
        # do not allow the SSI $20 general income disregard. ssi_countable_income
        # already applies that exclusion (in _apply_ssi_exclusions), so add back
        # the amount that was actually applied.
        #
        # When both spouses are SSI-eligible (couple computation applies), SSI
        # applies the $20 once to combined unearned and then splits the result
        # evenly across the two spouses; the per-person add-back is then half
        # of min(combined_unearned, $20). Otherwise the $20 applies to this
        # person's own unearned income.
        p = parameters(period).gov.ssa.ssi.income.exclusions
        countable_monthly = (
            person("ssi_countable_income", period.this_year) / MONTHS_IN_YEAR
        )
        own_unearned_monthly = (
            person("ssi_unearned_income", period.this_year) / MONTHS_IN_YEAR
        )
        couple = person("ssi_couple_computation_applies", period.this_year)
        combined_unearned_monthly = person.marital_unit.sum(own_unearned_monthly)
        addback = where(
            couple,
            min_(combined_unearned_monthly, p.general)
            / person.marital_unit.nb_persons(),
            min_(own_unearned_monthly, p.general),
        )
        return countable_monthly + addback
