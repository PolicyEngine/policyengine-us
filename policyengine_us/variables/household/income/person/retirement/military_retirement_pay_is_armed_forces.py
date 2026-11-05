from policyengine_us.model_api import *


class military_retirement_pay_is_armed_forces(Variable):
    value_type = bool
    entity = Person
    label = "Military retirement pay is from the armed forces"
    definition_period = YEAR
    default_value = True
    documentation = (
        "Whether this person's military_retirement_pay and "
        "military_retirement_pay_survivors come from service in the armed "
        "forces (the Army, Navy, Air Force, Marine Corps, Space Force and "
        "Coast Guard, 10 U.S.C. 101(a)(4)). Set it to false for retirement "
        "pay or survivor annuities from the commissioned corps of the "
        "National Oceanic and Atmospheric Administration or the Public "
        "Health Service, which are uniformed services (10 U.S.C. 101(a)(5)) "
        "but not armed forces. Some state exclusions cover the armed forces "
        "only."
    )
    reference = ("https://uscode.house.gov/us/usc/t10/s101/",)
