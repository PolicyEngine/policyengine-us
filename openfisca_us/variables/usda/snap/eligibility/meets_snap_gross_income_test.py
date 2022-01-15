from openfisca_us.model_api import *


class meets_snap_gross_income_test(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets SNAP gross income test"
    documentation = "Whether this SPM unit meets the SNAP gross income test"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/7/2017#a",
        "https://www.law.cornell.edu/uscode/text/7/2014#c",
    )

    def formula(spm_unit, period, parameters):
        income_limits = parameters(period).usda.snap.income_limits
        fpg = spm_unit("spm_unit_fpg", period)
        gross_income_limit = income_limits.gross.standard * fpg
        # Get income pre- and post-deductions.
        gross_income = spm_unit("snap_gross_income", period)
        # Households with elderly and disabled people are exempt from the
        # gross income test.
        has_elderly_disabled = spm_unit("has_usda_elderly_disabled", period)
        return has_elderly_disabled | (gross_income < gross_income_limit)
