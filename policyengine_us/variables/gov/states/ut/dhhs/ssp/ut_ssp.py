from policyengine_us.model_api import *


class ut_ssp(Variable):
    value_type = float
    entity = Person
    label = "Utah State Supplemental Payment"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.UT
    # The Department of Workforce Services supplement excludes residents of
    # institutions where Medicaid pays more than half the cost of care
    # (DWS Eligibility Manual 205-10), who may receive the DHHS payment
    # instead. Both payments key on the federal MEDICAL_TREATMENT_FACILITY
    # arrangement, so no one receives both.
    # NOTE: Not in the HUD income list, because ut_dhhs_ssp depends on Medicaid
    # enrollment. The HUD list carries ut_dws_ssp directly.
    reference = (
        "https://www.law.cornell.edu/regulations/utah/Utah-Admin-Code-R414-306-6",
        "https://oepmanuals.dhhs.utah.gov/600_Program_Benefits/661_Fifteen_Dollar_State_Supplemental_Payment_%28SSP%29.htm",
        "https://jobs.utah.gov/infosource/eligibilitymanual/200_Program_Eligibility_Requirements/205-10_State_Supplemental_Payments_to_SSI_Recipients_-_General_Information.htm",
    )
    adds = ["ut_dhhs_ssp", "ut_dws_ssp"]
