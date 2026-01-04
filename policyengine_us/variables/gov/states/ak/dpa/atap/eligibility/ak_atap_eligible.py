from policyengine_us.model_api import *


class ak_atap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Alaska ATAP eligible"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/alaska/7-AAC-45.470",
        "https://health.alaska.gov/en/services/alaska-temporary-assistance/",
    )
    defined_for = StateCode.AK

    def formula(spm_unit, period, parameters):
        # Demographic: use federal TANF demographic eligibility
        demographic = spm_unit("is_demographic_tanf_eligible", period)

        # Immigration: use federal (state follows federal qualified alien rules)
        immigration = (
            add(spm_unit, period, ["is_citizen_or_legal_immigrant"]) > 0
        )

        # Resources eligibility
        resources_eligible = spm_unit("ak_atap_resources_eligible", period)

        # Gross income test (185% standard)
        gross_income_eligible = spm_unit(
            "ak_atap_gross_income_eligible", period
        )

        # Net income test (need standard)
        net_income_eligible = spm_unit("ak_atap_net_income_eligible", period)

        return (
            demographic
            & immigration
            & resources_eligible
            & gross_income_eligible
            & net_income_eligible
        )
