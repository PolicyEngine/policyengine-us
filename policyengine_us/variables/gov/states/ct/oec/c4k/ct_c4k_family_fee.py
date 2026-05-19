from policyengine_us.model_api import *


class ct_c4k_family_fee(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.CT
    label = "Connecticut Care 4 Kids family fee"
    reference = (
        "https://eregulations.ct.gov/eRegsPortal/Browse/RCSA/Title_17bSubtitle_17b-749Section_17b-749-13/",
        "https://www.ctoec.org/care-4-kids/c4k-policies/",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ct.oec.c4k.family_fee
        countable_income = spm_unit("ct_c4k_countable_income", period)
        smi = spm_unit("hhs_smi", period)
        mask = smi > 0
        smi_ratio = np.divide(
            countable_income,
            smi,
            out=np.zeros_like(countable_income),
            where=mask,
        )
        fee_rate = p.rate.calc(smi_ratio)

        earned_income = add(
            spm_unit,
            period,
            ["employment_income", "self_employment_income", "farm_operations_income"],
        )
        has_earned_income = earned_income > 0
        return where(has_earned_income, countable_income * fee_rate, 0)
