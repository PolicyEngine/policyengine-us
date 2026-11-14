from policyengine_us.model_api import *


class in_ccdf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Indiana CCDF income eligible"
    definition_period = MONTH
    defined_for = StateCode.IN
    reference = (
        "https://www.in.gov/fssa/carefinder/files/CCDF-Policy-Manual.pdf#page=5",
        "https://www.in.gov/dA/3271c7180e/Income-Get-on-CCDF.pdf",
        # PDF pages 1-2
        "https://www.in.gov/dA/7fc32972de/CCDFSlidingFeeSchedule_withCopays_2026.pdf#page=1",
        "https://www.in.gov/dA/6307709ae5/ACF-118CCDFFFY2025-2027IndianaAmendment.pdf?language_id=1#page=22",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states["in"].fssa.ccdf.income
        countable_income = spm_unit("in_ccdf_countable_income", period)
        enrolled = spm_unit("is_in_ccdf_enrolled", period)
        # Initial applicants are tested against the get-on share of the
        # federal poverty guideline (127% through Jul 2023, 150% from Aug
        # 2023, 135% from Apr 2026); enrolled recipients are tested at 85%
        # of the state median income. The plan allows no limit above 85% of
        # the state median income, and FSSA's charts cap the get-on limit there
        # for the largest families ($13,028 a month for 19 people from April
        # 2026). The charts print the get-on limit to the nearest dollar, with
        # half a dollar going up ($3,073.50 prints as $3,074), and round the 85%
        # limit up to the next dollar ($7,618.48 prints as $7,619 for four).
        # Round to cents first so floating-point noise can't move a tie.
        fpg_limit = np.floor(
            np.round(spm_unit("in_ccdf_fpg", period) * p.get_on_fpg_rate, 2) + 0.5
        )
        smi_limit = np.ceil(
            np.round(spm_unit("in_ccdf_smi", period) * p.stay_on_smi_rate, 2)
        )
        income_limit = where(enrolled, smi_limit, min_(fpg_limit, smi_limit))
        return countable_income <= income_limit
