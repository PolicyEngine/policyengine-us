from openfisca_us.model_api import *


class is_snap_eligible(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP eligible"
    unit = "currency-USD"
    documentation = "Whether this SPM unit is eligible for SNAP benefits"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/7/2017#a",
        "https://www.law.cornell.edu/uscode/text/7/2014#c",
    )

    def formula(spm_unit, period, parameters):
        income_limits = parameters(period).usda.snap.income_limits
        fpg = spm_unit("spm_unit_fpg", period)
        net_income_limit = income_limits.net * fpg
        gross_income_limit = income_limits.gross.standard * fpg
        # Get income pre- and post-deductions.
        gross_income = spm_unit("snap_gross_income", period)
        net_income = spm_unit("snap_net_income", period)
        # Households with elderly and disabled people are exempt from the
        # gross income test.
        has_elderly_disabled = spm_unit("has_elderly_disabled", period)
        meets_net_income_test = net_income < net_income_limit
        meets_gross_income_test = gross_income < gross_income_limit
        exempt_from_gross_income_limit = has_elderly_disabled
        meets_asset_test = spm_unit("meets_snap_asset_test", period)
        meets_normal_gross_income_test = (
            meets_gross_income_test | exempt_from_gross_income_limit
        )
        # Broad based categorical eligibility overrides asset and gross income
        # tests.
        bbce = spm_unit("is_tanf_non_cash_eligible", period)
        return meets_net_income_test & (
            bbce | (meets_asset_test & meets_normal_gross_income_test)
        )
