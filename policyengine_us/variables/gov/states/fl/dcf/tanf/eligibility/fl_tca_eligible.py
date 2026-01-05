from policyengine_us.model_api import *


class fl_tca_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Florida TCA eligible"
    definition_period = MONTH
    reference = (
        "https://www.leg.state.fl.us/statutes/index.cfm?App_mode=Display_Statute&URL=0400-0499/0414/Sections/0414.095.html",
        "https://www.myflfamilies.com/services/public-assistance/temporary-cash-assistance",
    )
    defined_for = StateCode.FL

    def formula(spm_unit, period, parameters):
        # Use federal demographic eligibility (minor child with deprived parent)
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)

        # Use federal immigration eligibility (at least one citizen or qualified immigrant)
        immigration_eligible = (
            add(spm_unit, period, ["is_citizen_or_legal_immigrant"]) > 0
        )

        # Must pass both income tests
        gross_income_eligible = spm_unit(
            "fl_tca_gross_income_eligible", period
        )
        net_income_eligible = spm_unit("fl_tca_net_income_eligible", period)

        # Must pass resource test
        resource_eligible = spm_unit("fl_tca_resources_eligible", period)

        return (
            demographic_eligible
            & immigration_eligible
            & gross_income_eligible
            & net_income_eligible
            & resource_eligible
        )
