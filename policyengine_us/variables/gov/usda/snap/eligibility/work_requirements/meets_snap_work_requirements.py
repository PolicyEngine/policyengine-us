from policyengine_us.model_api import *


class meets_snap_work_requirements(Variable):
    value_type = bool
    entity = SPMUnit
    label = "SPM Unit is eligible for SNAP benefits via work requirements"
    definition_period = MONTH
    reference = (
        "https://www.fns.usda.gov/snap/work-requirements",
        "https://www.law.cornell.edu/cfr/text/7/273.7#f_1",
        "https://www.law.cornell.edu/cfr/text/7/273.24#b",
    )

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        return spm_unit.any(person("meets_snap_work_requirements_person", period))
