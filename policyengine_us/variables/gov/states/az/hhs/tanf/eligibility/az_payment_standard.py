from policyengine_us.model_api import *


class az_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Arizona Cash Assistance Payment Standard"
    definition_period = MONTH
    reference = (
        "https://des.az.gov/services/child-and-family/cash-assistance/cash-assistance-ca-income-eligibility-guidelines"
    )
    defined_for = "az_payment_standard"

def formula(spm_unit, period, parameters):
        monthly_fpg_1992 = spm_unit("spm_unit_fpg", period)
        p = parameters(
            period
        ).gov.states.az.hhs.tanf.eligibility.payment_standard
        shelter_cost = spm_unit("housing_cost", period)
        return where(shelter_cost > 0, np.floor(p.high*monthly_fpg_1992), np.floor(p.low*monthly_fpg_1992))