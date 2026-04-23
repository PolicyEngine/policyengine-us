from policyengine_us.model_api import *


class meets_snap_work_requirements(Variable):
    value_type = bool
    entity = SPMUnit
    label = "SPM Unit is eligible for SNAP benefits via work requirements"
    definition_period = MONTH
    reference = (
        "https://www.fns.usda.gov/snap/work-requirements",
        # 7 CFR 273.7(f)(1) — general work requirement; individual
        # disqualification is the default rule.
        "https://www.law.cornell.edu/cfr/text/7/273.7",
        # 7 CFR 273.24(b) — ABAWD time limit; always individual.
        "https://www.law.cornell.edu/cfr/text/7/273.24",
    )

    def formula(spm_unit, period, parameters):
        # Per 7 CFR 273.7(f)(1) and 273.24(b), a non-compliant member is
        # individually disqualified and excluded from the SNAP unit.
        # Remaining members continue to receive SNAP. The unit remains
        # eligible on the work-requirement dimension so long as at least
        # one member meets requirements or is exempt.
        #
        # The narrow 7 CFR 273.7(f)(5) state option — elected by 8
        # jurisdictions (AZ, FL, MA, MN, MS, TX, VA, VI) — permitting
        # household-wide disqualification when the head of household
        # fails the general work requirement, bounded to at most 180
        # days, is not yet parameterized here.
        person = spm_unit.members
        disqualified = person("is_snap_work_requirements_disqualified", period)
        return spm_unit.any(~disqualified)
