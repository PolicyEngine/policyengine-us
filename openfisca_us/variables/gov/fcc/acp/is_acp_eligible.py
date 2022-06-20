from openfisca_us.model_api import *


class is_acp_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Affordable Connectivity Program"
    documentation = "Eligible for Affordable Connectivity Program"
    definition_period = YEAR
    # 47 U.S.C §1752(a)(6).
    reference = "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title47-section1752&edition=prelim"

    def formula(spm_unit, period, parameters):
        fcc = parameters(period).gov.fcc
        categorically_eligible = np.any(
            [
                aggr(spm_unit, period, [program])
                for program in fcc.acp.categorical_eligibility
            ],
            axis=0,
        )
        # ACP categorical eligibility points includes Lifeline categorical eligibility.
        lifeline_categorically_eligible = np.any(
            [
                aggr(spm_unit, period, [program])
                for program in fcc.lifeline.categorical_eligibility
            ],
            axis=0,
        )
        fpg_eligible = spm_unit("fcc_fpg_ratio", period) <= fcc.acp.fpg_limit
        # Cannot be simultaneously enrolled in Emergency Broadband Benefit.
        ebb_enrolled = spm_unit("ebb", period) > 0
        return (
            categorically_eligible
            | fpg_eligible
            | lifeline_categorically_eligible
        ) & ~ebb_enrolled
