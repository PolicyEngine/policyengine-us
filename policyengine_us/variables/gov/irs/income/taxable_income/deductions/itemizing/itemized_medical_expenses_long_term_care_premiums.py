from policyengine_us.model_api import *


class itemized_medical_expenses_long_term_care_premiums(Variable):
    value_type = float
    entity = TaxUnit
    label = "Long-term care premiums included in supplied itemized medical expenses"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/213#d_10",
        "https://www.irs.gov/instructions/i1040sca",
    )
    documentation = (
        "The long-term care insurance premiums that a supplied "
        "itemized_medical_expenses includes, such as eligible premiums "
        "counted on Schedule A line 1 and not taken as the self-employed "
        "health insurance deduction. The computed subtotal counts no "
        "long-term care premiums, so leave this at 0 unless you supply a "
        "subtotal that includes them. States that deduct long-term care "
        "premiums separately remove this amount from the subtotal first. With "
        "a subtotal that leaves out premiums taken as the self-employed "
        "deduction, follow the split itemized_medical_expenses_applied_exclusion "
        "uses, whatever the return itself did: this is the eligible long-term "
        "care premiums less any part of that exclusion above the head's and "
        "spouse's medical insurance premiums."
    )
