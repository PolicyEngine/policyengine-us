from policyengine_us.model_api import *


class ks_tanf_assistance_size(Variable):
    value_type = int
    entity = SPMUnit
    label = "Kansas TANF assistance plan size"
    definition_period = YEAR
    defined_for = StateCode.KS
    reference = (
        "https://content.dcf.ks.gov/ees/keesm/current/keesm4113.htm",
        "https://www.law.cornell.edu/regulations/kansas/K-A-R-30-4-100",
    )

    def formula(spm_unit, period, parameters):
        # Per KEESM 4113: SSI recipients are excluded from the TAF assistance
        # plan, "excluded from the benefits and the household size."
        ssi_recipients = spm_unit.sum(spm_unit.members("applicable_ssi", period) > 0)
        return spm_unit("spm_unit_size", period) - ssi_recipients
