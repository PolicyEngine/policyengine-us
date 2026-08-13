from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi


class tn_ccap_smi(Variable):
    value_type = float
    entity = SPMUnit
    label = "Tennessee CCAP monthly state median income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.TN
    reference = (
        "https://www.tn.gov/content/dam/tn/human-services/documents/Income%20Eligibility%20Limits%20and%20CoPay%20Chart%2010.1.25.pdf#page=1",
        "https://www.tn.gov/content/dam/tn/human-services/documents/CCDF%20State%20Plan%20FFY%202025-2027%20Tennessee.pdf#page=36",
    )

    def formula(spm_unit, period, parameters):
        # The published income charts use the federal fiscal year SMI, which
        # takes effect on October 1. Pin the SMI to the FFY covering the month.
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
