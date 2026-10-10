from policyengine_us.model_api import *


class is_snap_sua_hr1_in_effect(Variable):
    value_type = bool
    entity = SPMUnit
    label = "HR1 limit on energy-assistance qualification for the SNAP SUA is in effect"
    definition_period = MONTH
    reference = (
        "https://www.congress.gov/119/plaws/publ21/PLAW-119publ21.pdf#page=13",
        "https://www.cdss.ca.gov/Portals/9/Additional-Resources/Letters-and-Notices/ACLs/2025/25-68.pdf#page=7",
    )

    def formula(spm_unit, period, parameters):
        # Only California is modelled. P.L. 119-21 section 10103 applies in
        # every state, but each state that deems the SUA sets its own
        # implementation date, and none other than California has been
        # sourced. Other states return false, which leaves their current
        # behaviour unchanged. Add a state here with its own hr1_in_effect
        # parameter once its date is sourced, as for the ABAWD gate.
        state_code = spm_unit.household("state_code", period.this_year)
        ca = parameters(
            period
        ).gov.states.ca.cdss.snap.income.deductions.utility.hr1_in_effect
        return (state_code == StateCode.CA) & ca
