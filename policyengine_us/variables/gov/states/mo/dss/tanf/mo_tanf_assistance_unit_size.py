from policyengine_us.model_api import *


class mo_tanf_assistance_unit_size(Variable):
    value_type = int
    entity = SPMUnit
    label = "Missouri TANF assistance unit size"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-310",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0200-000-00/",
    )
    defined_for = StateCode.MO

    def formula(spm_unit, period, parameters):
        # Simplified implementation: use SPM unit size as proxy for assistance unit
        # Full implementation would track eligible children, parents, and caretakers
        # per 13 CSR 40-2.310 definitions
        return spm_unit("spm_unit_size", period)
