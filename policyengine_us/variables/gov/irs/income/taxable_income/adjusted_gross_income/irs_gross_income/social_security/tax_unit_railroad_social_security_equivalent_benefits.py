from policyengine_us.model_api import *


class tax_unit_railroad_social_security_equivalent_benefits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax unit Railroad Retirement social security equivalent benefits"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/86#d_1_B"

    adds = ["railroad_social_security_equivalent_benefits"]
