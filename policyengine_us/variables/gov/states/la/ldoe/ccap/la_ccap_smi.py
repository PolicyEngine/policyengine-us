from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi


class la_ccap_smi(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = "Louisiana CCAP state median income"
    unit = USD
    reference = (
        "https://www.louisianabelieves.com/docs/default-source/early-childhood/ccap-sliding-fee-scale.pdf",
        "https://doe.louisiana.gov/docs/default-source/early-childhood/early-childhood-provider-updates-(february-2025).pdf",
    )
    defined_for = StateCode.LA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.la.ldoe.ccap
        # Each annual scale takes effect in February (per LDOE provider-update
        # memos) and is built from the ACF state median income estimates for
        # the federal fiscal year that began the prior October (scale footer:
        # "Based on ACS [year] SMI Estimates in ACF Resource updated May/June
        # [year]"). Pin the lookup to that October 1 instant: it lands on the
        # SMI table's explicit entries, whereas reading at the February
        # effective date falls past the series end for the newest scale and
        # picks up CBO uprating instead of the published table. January falls
        # under the prior year's scale.
        year = period.start.year
        month = period.start.month
        if month >= 2:
            instant_str = f"{year - 1}-10-01"
        else:
            instant_str = f"{year - 2}-10-01"
        size = spm_unit("spm_unit_size", period.this_year)
        capped_size = clip(size, p.household_size.minimum, p.household_size.maximum)
        state = spm_unit.household("state_code_str", period.this_year)
        return smi(capped_size, state, instant_str, parameters) / MONTHS_IN_YEAR
