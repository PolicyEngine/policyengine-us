from policyengine_us.model_api import *


class filer_tax_exempt_social_security(Variable):
    value_type = float
    entity = TaxUnit
    label = "Filer's tax-exempt Social Security"
    unit = USD
    documentation = (
        "Social Security benefits of the head and spouse that section 86 "
        "leaves out of this return's AGI. A tax unit dependent's benefits are "
        "the dependent's own income, as in "
        "tax_unit_social_security_for_taxability. Unlike "
        "tax_exempt_social_security, this leaves dependents' benefits out."
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/86"

    adds = ["tax_unit_social_security_for_taxability"]
    subtracts = ["tax_unit_taxable_social_security"]
