from policyengine_us.model_api import *


class mt_elderly_homeowner_or_renter_credit_received(Variable):
    value_type = float
    entity = Person
    label = "Montana elderly homeowner/renter credit received"
    documentation = (
        "Montana elderly homeowner/renter credit refunds received during the "
        "year, normally the credit claimed on the prior year's return. It "
        "counts in the current year's gross household income."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        # ARM 42.4.301(2)(c): "any state refundable tax credits received,
        # including elderly homeowner/renter credit refunds"
        "https://rules.mt.gov/api/policy-library-public/collections/aec52c46-128e-4279-9068-8af5d5432d74/policies/c90ea93a-03a2-4605-a0f8-f2f3760198bf/document/768c8344-24ee-4950-9d5e-9d8fc97ec0f7",
        # 2024 Schedule 2EC, line 8: "including your elderly homeowner/renter
        # credit received in 2024"
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2024_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=47",
    )
    # An input rather than this credit read at period.last_year. This year's
    # credit cannot count without a circular reference. Reading last year's
    # credit would rerun the whole prior-year tax computation, every member's
    # federal refundable credits included, for each record, and it reads 0
    # whenever the inputs cover only one year.
