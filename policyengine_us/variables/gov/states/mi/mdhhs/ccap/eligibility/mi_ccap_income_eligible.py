from policyengine_us.model_api import *


class mi_ccap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Michigan CDC based on income"
    definition_period = MONTH
    defined_for = StateCode.MI
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/EX/RF/Public/RFT/270.pdf#page=3"
    )

    def formula(spm_unit, period, parameters):
        # RFT 270 Table 1 / BEM 703 p.17-18: gross monthly program-group income
        # must be at or below the entry limit at application and at or below the
        # exit limit ongoing. Income-waived groups bypass this test.
        p = parameters(period).gov.states.mi.mdhhs.ccap.income.scale
        countable_income = spm_unit("mi_ccap_countable_income", period)
        size = spm_unit("mi_ccap_program_group_size", period)
        enrolled = spm_unit("mi_ccap_enrolled", period)
        income_limit = where(
            enrolled,
            p.exit_limit[size],
            p.entry_limit[size],
        )
        return countable_income <= income_limit
