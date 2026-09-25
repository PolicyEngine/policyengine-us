from policyengine_us.model_api import *


class snap_net_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    documentation = "Final net income, after all deductions"
    label = "SNAP net income"
    unit = USD
    reference = (
        "https://www.law.cornell.edu/uscode/text/7/2014",
        # 7 CFR 273.10(e)(1)(ii)(A).
        "https://www.ecfr.gov/current/title-7/section-273.10#p-273.10(e)(1)(ii)(A)",
    )

    def formula(spm_unit, period):
        gross_income = spm_unit("snap_gross_income", period)
        deductions = spm_unit("snap_deductions", period)
        net_income = max_(0, gross_income - deductions)
        # 7 CFR 273.10(e)(1)(ii)(A): round net income to the nearest dollar
        # (1-49 cents down, 50-99 cents up), so use half-up rounding rather
        # than np.round's round-half-to-even. This is the rounding option
        # PolicyEngine applies for all states; states may instead elect
        # their TANF rounding procedure under 273.10(e)(1)(ii)(B).
        return np.floor(net_income + 0.5)
