from policyengine_us.model_api import *


class partnership_self_employment_net_earnings(Variable):
    value_type = float
    entity = Person
    label = "partnership net earnings from self-employment"
    definition_period = YEAR
    documentation = (
        "Partnership net earnings allocated to self-employment tax and "
        "earned-income calculations, generally from Schedule K-1 Box 14. "
        "This is not an additional gross income source separate from "
        "partnership_income."
    )
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/1402#a_13"
    uprating = "calibration.gov.irs.soi.self_employment_income"
