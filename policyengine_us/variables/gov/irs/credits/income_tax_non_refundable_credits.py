from policyengine_us.model_api import *


class income_tax_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Income tax non-refundable credits"
    documentation = (
        "Total non-refundable credits used to reduce positive tax liability"
    )
    unit = USD

    formula = sum_of_variables("gov.irs.credits.non_refundable")


c07100 = variable_alias("c07100", income_tax_non_refundable_credits)
