from policyengine_us.model_api import *


class snap_expected_contribution(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    documentation = "Expected food contribution from SNAP net income"
    label = "SNAP expected food contribution"
    unit = USD
    reference = (
        "https://www.law.cornell.edu/uscode/text/7/2017#a",
        "https://www.law.cornell.edu/cfr/text/7/273.10#e_8_ii_A",
        "https://www.law.cornell.edu/cfr/text/7/273.10#e_2_ii_A_1",
    )

    def formula(spm_unit, period, parameters):
        expected_food_contribution = parameters(
            period
        ).gov.usda.snap.expected_contribution
        # 7 CFR 273.10(e)(1)(ii)(A): net income is rounded to the nearest
        # dollar (1-49 cents down, 50-99 cents up), so use half-up rounding
        # rather than np.round's round-half-to-even.
        net_income = np.floor(spm_unit("snap_net_income", period) + 0.5)
        # 7 CFR 273.10(e)(2)(ii)(A)(1): 30 percent of net income is rounded
        # up to the next higher dollar, which is equivalent to rounding the
        # allotment down to the nearest lower whole dollar (7 USC 2017(a)).
        # Round to cents first so float noise (e.g. 50 * 0.3 = 15.0000001)
        # does not push an exact dollar amount up to the next dollar.
        contribution = np.round(net_income * expected_food_contribution, 2)
        return np.ceil(contribution)
