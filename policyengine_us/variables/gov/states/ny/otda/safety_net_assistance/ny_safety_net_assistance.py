from policyengine_us.model_api import *


class ny_safety_net_assistance(Variable):
    value_type = float
    entity = SPMUnit
    label = "New York Safety Net Assistance payments"
    definition_period = MONTH
    set_input = set_input_divide_by_period
    calculate_output = calculate_output_add
    default_value = 0
    unit = USD
    defined_for = StateCode.NY
    documentation = (
        "Records Safety Net Assistance payments received by the SPM unit "
        "during the month. New York counts these payments as public "
        "assistance income for child care under 18 NYCRR 404.5(b)(5)(vi). "
        "Record a parent's or caretaker relative's receipt separately with "
        "ny_safety_net_assistance_received for CCAP categorical routes."
    )
    reference = (
        "https://ocfs.ny.gov/programs/childcare/regulations/404-Eligibility.pdf#page=10"
    )
