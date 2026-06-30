from policyengine_us.model_api import *


class ia_ssa_has_full_medicaid(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Iowa SSA receives full Medicaid"
    defined_for = StateCode.IA
    default_value = False
    reference = (
        "https://www.legis.iowa.gov/docs/iac/chapter/01-07-2026.441.51.pdf#page=2"
    )
    # IAC 441—51.6(1) requires SMME recipients to be enrolled in "full
    # Medicaid", which excludes medically-needy/spenddown and MEPD-premium
    # pathways. PolicyEngine's generic `medicaid_enrolled` flag includes
    # those narrower populations, so Iowa SSA takes an explicit input for
    # this flag — users opt in when a household is known to be enrolled in
    # full Medicaid.
