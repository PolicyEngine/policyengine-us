from policyengine_us.model_api import *


class oh_529_plan_deduction_carryforward(Variable):
    value_type = float
    entity = Person
    label = "Ohio 529 plan contributions carried forward for this beneficiary"
    unit = USD
    documentation = (
        "Contributions the head and spouse of this person's tax unit made in "
        "earlier years to 529 plans for which this person is the beneficiary, "
        "above Ohio's limit per beneficiary and not yet deducted. Ohio "
        "deducts them in later years, within the same limit."
    )
    definition_period = YEAR
    reference = (
        # R.C. 5747.70(A): "If the combined annual contributions and purchases
        # for a beneficiary exceed four thousand dollars, the excess may be
        # carried forward".
        "https://codes.ohio.gov/assets/laws/revised-code/authenticated/57/5747/5747.70/4-3-2023/5747.70-4-3-2023.pdf#page=1",
        "https://dam.assets.ohio.gov/image/upload/v1767095693/tax.ohio.gov/forms/ohio_individual/individual/2025/it1040-booklet.pdf#page=25",
    )
    defined_for = StateCode.OH
