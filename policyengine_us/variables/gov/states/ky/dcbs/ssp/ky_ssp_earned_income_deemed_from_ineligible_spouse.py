from policyengine_us.model_api import *


class ky_ssp_earned_income_deemed_from_ineligible_spouse(Variable):
    value_type = float
    entity = Person
    label = "Kentucky SSP earned income deemed from an ineligible spouse"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.KY
    reference = (
        "https://apps.legislature.ky.gov/law/kar/titles/921/002/015/",
        "https://www.chfs.ky.gov/agencies/dcbs/dfs/Documents/OMVOLIVA.pdf#page=188",
        "https://www.law.cornell.edu/cfr/text/20/416.1163",
    )
    documentation = (
        "Retain SSI's child-allocation arithmetic using the ineligible spouse's "
        "own Kentucky earned income. MS 2450 B.4, C.7 and C.8(b), incorporated "
        "by 921 KAR 2:015 section 8(1), count each business's profit without "
        "offsetting other earnings with losses. Neither spouse's business "
        "loss therefore reduces the ineligible spouse's deemed earnings."
    )

    def formula(person, period, parameters):
        ineligible_spouse = person("is_ssi_ineligible_spouse", period)
        unearned = person("ssi_unearned_income", period)
        earned = person("ky_ssp_earned_income", period)
        marital_unit = person.marital_unit
        spouse_unearned = (
            marital_unit.sum(ineligible_spouse * unearned)
            - ineligible_spouse * unearned
        )
        spouse_earned = (
            marital_unit.sum(ineligible_spouse * earned) - ineligible_spouse * earned
        )
        child_allocations = add(
            person.tax_unit, period, ["ssi_ineligible_child_allocation"]
        ) * person("is_ssi_aged_blind_disabled", period)
        remaining_allocations = max_(child_allocations - spouse_unearned, 0)
        return max_(spouse_earned - remaining_allocations, 0)
