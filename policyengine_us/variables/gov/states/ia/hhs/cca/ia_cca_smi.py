from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi


class ia_cca_smi(Variable):
    value_type = float
    entity = SPMUnit
    label = "Iowa CCA 85% median family income income cap"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.IA
    reference = "https://www.legis.iowa.gov/docs/iac/chapter/441.170.pdf#page=3"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ia.hhs.cca.income
        # IAC 441-170.2(1)"a"(1)"3" caps income at 85% of Iowa's "median
        # family income (MFI)." Iowa publishes no standalone MFI figure, so we
        # use the federal CCDF State Median Income (SMI) table as a proxy for
        # the statutory MFI standard. The 0.85 share is taken directly from
        # the regulation.
        year = period.start.year
        month = period.start.month
        # The federal SMI table is published on a fiscal-year basis
        # beginning each October 1.
        if month >= 10:
            instant_str = f"{year}-10-01"
        else:
            instant_str = f"{year - 1}-10-01"
        size = spm_unit("spm_unit_size", period.this_year)
        state = spm_unit.household("state_code_str", period.this_year)
        annual_smi = smi(size, state, instant_str, parameters)
        return annual_smi * p.smi_rate / MONTHS_IN_YEAR
