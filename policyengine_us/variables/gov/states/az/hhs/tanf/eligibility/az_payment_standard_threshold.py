from policyengine_us.model_api import *


class az_payment_standard_threshold(Variable):
    value_type = float
    entity = SPMUnit
    label = "Arizona Cash Assistance Payment Standard"
    definition_period = MONTH
    reference = "https://des.az.gov/services/child-and-family/cash-assistance/cash-assistance-ca-income-eligibility-guidelines"


def formula(spm_unit, period, parameters):
    fpg_year = f"1992-01-01"
    household_size = spm_unit("az_countable_household_size", period)
    state_group = spm_unit.household("state_group_str", period)
    p_fpg = parameters(fpg_year).gov.hhs.fpg
    p1 = p_fpg.first_person[state_group]
    pn = p_fpg.additional_person[state_group]
    fpg_baseline = p1 + pn * (household_size - 1)
    monthly_fpg_baseline=fpg_baseline/MONTH
    p = parameters(
        period
    ).gov.states.az.hhs.tanf.eligibility.payment_standard
    high_threshold = np.floor(p.high * monthly_fpg_baseline)
    low_threshold = np.floor(p.low * monthly_fpg_baseline)
    shelter_cost = spm_unit("housing_cost", period)

    return where(
        shelter_cost > 0,
        high_threshold,
        low_threshold,
    )
