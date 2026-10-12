from policyengine_us.model_api import *


class mn_ccap_registration_fee(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    definition_period = MONTH
    label = "Minnesota CCAP registration fee paid on the family's behalf"
    defined_for = StateCode.MN
    reference = (
        # DHS-6443D registration fee maximums; Minnesota CCAP Policy Manual
        # section 9.3.6; Minn. Stat. 142E.17 subd. 1(i).
        "https://www.revisor.mn.gov/statutes/cite/142E.17",
    )
    # Optional input: the registration fee the program pays the provider on the
    # family's behalf. We don't track whether a provider charges a registration
    # fee, so this defaults to $0. The county/city maximum cap and the limit of
    # two fees per child per 12-month period are not modeled at the moment.
