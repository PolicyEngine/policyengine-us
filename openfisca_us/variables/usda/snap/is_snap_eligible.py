from openfisca_us.model_api import *


class is_snap_eligible(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP eligible"
    unit = "currency-USD"
    documentation = "Whether this SPM unit is eligible for SNAP benefits"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/7/2017#a; https://www.law.cornell.edu/uscode/text/7/2014#c"
    default_value = True

    def formula(spm_unit, period, parameters):

        # per the law, this test is applied before any of the deductions are applied to snap gross income
        # we are currently not modeling the possibility of permanently disabled individuals forming a second
        # sub-household
        gross_limit = parameters(period).usda.snap.income_limits.gross.standard
        net_limit = parameters(period).usda.snap.income_limits.net

        gross_income = spm_unit("snap_gross_income", period)
        net_income = spm_unit("snap_net_income", period)

        has_elderly_disabled = spm_unit("has_elderly_disabled", period)

        meets_net_income_limit = net_income < net_limit
        meets_gross_income_limit = gross_income < gross_limit

        exempt_from_gross_income_limit = has_elderly_disabled

        return meets_net_income_limit & (
            meets_gross_income_limit | exempt_from_gross_income_limit
        )
