from policyengine_us.model_api import *


class ms_ccpp_categorically_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Categorically eligible for Mississippi CCPP"
    definition_period = MONTH
    defined_for = StateCode.MS
    reference = "https://www.mdhs.ms.gov/wp-content/uploads/2026/01/CCPP-Policy-Manual_Final_1142025.pdf#page=19"

    def formula(spm_unit, period, parameters):
        # Categorical pathways bypass the income test. We model TANF
        # recipients, homeless children, and children in protective services.
        # Transitional Child Care, Healthy Families Mississippi, and teen-parent
        # pathways are not tracked at the moment.
        is_tanf = spm_unit("is_tanf_enrolled", period)
        is_homeless = spm_unit.household("is_homeless", period.this_year)
        has_protective_child = (
            add(
                spm_unit,
                period.this_year,
                ["receives_or_needs_protective_services"],
            )
            > 0
        )
        return is_tanf | is_homeless | has_protective_child
