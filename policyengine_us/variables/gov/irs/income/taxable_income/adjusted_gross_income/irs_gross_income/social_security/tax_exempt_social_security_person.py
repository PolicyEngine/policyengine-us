from policyengine_us.model_api import *


class tax_exempt_social_security_person(Variable):
    value_type = float
    entity = Person
    label = "Tax-exempt Social Security for each person"
    unit = USD
    documentation = (
        "The person's own Social Security benefits less the part of them in "
        "the tax unit's AGI (taxable_social_security). The head's and "
        "spouse's amounts add up to filer_tax_exempt_social_security. A tax "
        "unit dependent's benefits stay off the claimant's return, so their "
        "taxable_social_security is zero and this is their whole benefit; "
        "per-person AGIs built from gov.irs.gross_income.sources likewise "
        "leave a dependent's benefits out, so adding this amount counts "
        "each person's benefits once."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/86",
        "https://www.law.cornell.edu/uscode/text/26/36B#d_2_B_iii",
    )

    adds = ["social_security"]
    subtracts = ["taxable_social_security"]
