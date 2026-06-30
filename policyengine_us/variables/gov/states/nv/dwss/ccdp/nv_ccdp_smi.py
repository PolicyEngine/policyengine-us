from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi


class nv_ccdp_smi(Variable):
    value_type = float
    entity = SPMUnit
    label = "Nevada CCDP monthly 100% State Median Income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.NV
    reference = "https://www.dss.nv.gov/siteassets/dwss.nv.gov/content/care/ACF-118_CCDF_FFY_2025-2027_For_Nevada__3.pdf#page=36"

    def formula(spm_unit, period, parameters):
        # Nevada keys income eligibility and copays to State Median Income (not
        # the federal poverty guideline). The income chart updates annually on
        # October 1, so select the SMI table in effect for that program year.
        year = period.start.year
        month = period.start.month
        if month >= 10:
            instant_str = f"{year}-10-01"
        else:
            instant_str = f"{year - 1}-10-01"
        size = spm_unit("spm_unit_size", period.this_year)
        state = spm_unit.household("state_code_str", period.this_year)
        annual_smi = smi(size, state, instant_str, parameters)
        return annual_smi / MONTHS_IN_YEAR
