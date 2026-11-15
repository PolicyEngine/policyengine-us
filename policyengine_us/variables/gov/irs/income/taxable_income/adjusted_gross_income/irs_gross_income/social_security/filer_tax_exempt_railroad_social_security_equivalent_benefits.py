from policyengine_us.model_api import *


class filer_tax_exempt_railroad_social_security_equivalent_benefits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Filer's tax-exempt Railroad Retirement social security equivalent benefits"
    unit = USD
    documentation = (
        "Tier 1 railroad retirement benefits of the head and spouse that "
        "section 86 leaves out of this return's AGI, the counterpart of "
        "filer_tax_exempt_social_security. Unlike "
        "tax_exempt_railroad_social_security_equivalent_benefits, this leaves "
        "dependents' benefits out."
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/86#d_1_B"

    adds = ["tax_unit_railroad_social_security_equivalent_benefits_for_taxability"]
    subtracts = ["tax_unit_taxable_railroad_social_security_equivalent_benefits"]
