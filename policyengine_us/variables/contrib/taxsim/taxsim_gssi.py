from policyengine_us.model_api import *


class taxsim_gssi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Gross Social Security Income"
    unit = USD
    documentation = (
        "Social Security benefits and the social security equivalent part of "
        "tier 1 railroad retirement benefits, which section 86(d)(1) counts "
        "together, so taxsim_v12 runs section 86 on both."
    )
    reference = "https://www.law.cornell.edu/uscode/text/26/86#d_1"
    definition_period = YEAR

    adds = ["social_security", "railroad_social_security_equivalent_benefits"]
