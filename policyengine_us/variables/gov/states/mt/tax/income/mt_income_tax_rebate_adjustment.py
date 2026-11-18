from policyengine_us.model_api import *


class mt_income_tax_rebate_adjustment(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana income tax rebate adjustment"
    documentation = (
        "Sum of the individual 2021 rebates included in mt_refundable_credits. "
        "The existing separate-versus-joint election is held fixed, consistent "
        "with mt_income_tax_before_2021_rebate."
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT
    adds = ["mt_income_tax_rebate"]
