from policyengine_us.model_api import *


class tax_unit_section_86_benefits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax unit social security benefits under section 86"
    unit = USD
    documentation = (
        "The head's and spouse's social security benefits as IRC 86(d)(1) "
        "defines them: title II benefits and tier 1 railroad retirement "
        "benefits (the social security equivalent benefit). Section 86 figures "
        "one taxable amount on their total."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/86#d_1",
        # IRS Pub. 915 (2024), Worksheet A line A: box 5 of all Forms
        # SSA-1099 and RRB-1099.
        "https://www.irs.gov/pub/irs-prior/p915--2024.pdf#page=4",
    )

    adds = [
        "tax_unit_social_security_for_taxability",
        "tax_unit_railroad_social_security_equivalent_benefits_for_taxability",
    ]
