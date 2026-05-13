from policyengine_us.model_api import *


class ct_c4k_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    defined_for = StateCode.CT
    label = "Income eligible for Connecticut Care 4 Kids"
    reference = (
        "https://eregulations.ct.gov/eRegsPortal/Browse/RCSA/Title_17bSubtitle_17b-749Section_17b-749-05/",
        "https://www.cga.ct.gov/2023/rpt/pdf/2023-R-0249.pdf#page=3",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ct.oec.c4k.income
        countable_income = spm_unit("ct_c4k_countable_income", period)
        smi = spm_unit("hhs_smi", period)
        is_enrolled = add(spm_unit, period.this_year, ["is_enrolled_in_ccdf"]) > 0
        smi_limit = where(
            is_enrolled,
            p.continuing_limit_smi,
            p.initial_limit_smi,
        )
        return countable_income < smi * smi_limit
