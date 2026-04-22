from policyengine_us.model_api import *


class sc_ccap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for South Carolina CCAP based on income"
    definition_period = MONTH
    defined_for = StateCode.SC
    reference = (
        "https://www.scchildcare.org/media/ubhdm1at/1-13-2025_policy-manual.pdf#page=37",
        "https://www.scchildcare.org/media/cr5dc51w/submitted-version-of-the-ccdf-ffy-2025-2027-for-south-carolina-as-of-7-1-24pdf.pdf#page=17",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.sc.dss.ccap.income
        countable_income = spm_unit("sc_ccap_countable_income", period)
        smi = spm_unit("hhs_smi", period)
        return countable_income <= smi * p.smi_rate
