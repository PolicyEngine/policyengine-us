from policyengine_us.model_api import *


class meets_snap_gross_income_test(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets SNAP gross income test"
    documentation = "Whether this SPM unit meets the SNAP gross income test"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/uscode/text/7/2017#a",
        "https://www.law.cornell.edu/uscode/text/7/2014#c",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.usda.snap.income.limit
        # The gross test uses state-specific income counting for certain
        # ineligible aliens (7 CFR 273.11(c)(3)(i)).
        ratio = spm_unit("snap_gross_test_income_fpg_ratio", period)
        # Households with an elderly or disabled unit member are exempt
        # from the gross income test; excluded members are not household
        # members under the 7 CFR 271.2 definition, so they do not confer
        # this status.
        has_elderly_disabled = spm_unit("has_snap_elderly_disabled_member", period)
        return has_elderly_disabled | (ratio <= p.gross)
