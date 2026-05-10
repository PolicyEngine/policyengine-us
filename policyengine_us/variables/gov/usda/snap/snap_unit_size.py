from policyengine_us.model_api import *


class snap_unit_size(Variable):
    value_type = int
    entity = SPMUnit
    label = "SNAP unit size"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/uscode/text/7/2014#b",
        "https://www.law.cornell.edu/uscode/text/7/2015#f",
        # 7 CFR 273.11(c)(1), (c)(2), (c)(3), and (d): ineligible
        # members are excluded from SNAP unit size.
        "https://www.law.cornell.edu/cfr/text/7/273.11",
    )

    def formula(spm_unit, period, parameters):
        unit_size = spm_unit("spm_unit_size", period)
        person = spm_unit.members
        ineligible = (
            person("is_snap_ineligible_student", period)
            | person("is_snap_disqualified_prorated", period)
            | person("is_snap_work_requirements_disqualified", period)
        )
        ineligible_count = spm_unit.sum(ineligible)
        return max_(unit_size - ineligible_count, 0)
