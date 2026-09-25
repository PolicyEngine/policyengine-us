from policyengine_us.model_api import *


class ny_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York AGI additions"
    unit = USD
    documentation = "Additions to NY AGI over federal AGI."
    definition_period = YEAR
    dict(
        title="N.Y. Comp. Codes R. & Regs. tit. 20 § 112.2",
        href="https://www.law.cornell.edu/regulations/new-york/20-NYCRR-112.2",
    )
    defined_for = StateCode.NY

    # No additions modeled in PolicyEngine US.
