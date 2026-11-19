from policyengine_us.model_api import *
from policyengine_us.tools.state_itemization import (
    JOINT_METHOD_COUNT,
    joint_itemization_is_enabled,
)


class ny_elects_tuition_credit_when_itemizing(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Elects the New York college tuition credit when itemizing"
    definition_period = YEAR
    defined_for = StateCode.NY
    documentation = (
        "A New York itemizer may claim the tuition credit while itemizing other "
        "deductions. Set this election to the method used on the state return."
    )
    reference = (
        "https://www.nysenate.gov/legislation/laws/TAX/606",  # (t)(6)
        "https://www.nysenate.gov/legislation/laws/TAX/615",  # (d)(4)
        "https://www.tax.ny.gov/forms/html-instructions/2025/it/it272i-2025.htm",
    )

    def formula(tax_unit, period, parameters):
        if joint_itemization_is_enabled(period, parameters):
            return tax_unit("tax_unit_joint_itemization", period) >= JOINT_METHOD_COUNT
        return False
