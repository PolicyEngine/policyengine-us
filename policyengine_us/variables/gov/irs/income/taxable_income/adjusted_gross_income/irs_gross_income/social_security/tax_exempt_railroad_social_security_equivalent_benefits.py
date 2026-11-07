from policyengine_us.model_api import *


class tax_exempt_railroad_social_security_equivalent_benefits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax-exempt Railroad Retirement social security equivalent benefits"
    unit = USD
    documentation = (
        "Tier 1 railroad retirement benefits that section 86 leaves out of "
        "AGI, the counterpart of tax_exempt_social_security."
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/86#d_1_B"

    adds = ["tax_unit_railroad_social_security_equivalent_benefits"]
    subtracts = ["tax_unit_taxable_railroad_social_security_equivalent_benefits"]
