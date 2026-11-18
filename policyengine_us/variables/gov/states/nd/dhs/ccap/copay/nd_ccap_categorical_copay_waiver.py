from policyengine_us.model_api import *


class nd_ccap_categorical_copay_waiver(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "North Dakota CCAP family qualifies for a program co-payment waiver"
    reference = (
        "https://www.nd.gov/dhs/policymanuals/40028/Content/400_28_90_20.htm",
        "https://www.nd.gov/dhs/policymanuals/40028/Content/400_28_45_05.htm",
    )

    def formula_2011_10_01(spm_unit, period, parameters):
        crossroads = spm_unit("nd_ccap_crossroads_enrolled", period)
        diversion = spm_unit("nd_ccap_tanf_diversion_enrolled", period)
        exception = spm_unit("nd_ccap_tanf_copay_exception", period)
        return crossroads | (diversion & ~exception)

    def formula_2021_04_01(spm_unit, period, parameters):
        crossroads = spm_unit("nd_ccap_crossroads_enrolled", period)
        diversion = spm_unit("nd_ccap_tanf_diversion_enrolled", period)
        arsen = spm_unit("nd_ccap_arsen_enrolled", period)
        exception = spm_unit("nd_ccap_tanf_copay_exception", period)
        return crossroads | (diversion & ~exception) | arsen
