from policyengine_us.model_api import *


class federal_scholarship_state_tax_credit(Variable):
    value_type = float
    entity = Person
    label = "State tax credit attributable to qualified scholarship contributions"
    unit = USD
    definition_period = YEAR
    documentation = (
        "State credit allowed for federal_scholarship_qualified_contributions, "
        "including state carryable credit attributed to the contribution year. "
        "Supply the qualified portion after allocating state credit first to "
        "nonqualified gifts under proposed 1.25F-2(c)(2). This amount offsets the "
        "federal credit; it does not itself reduce state income tax."
    )
    reference = (
        "https://uscode.house.gov/us/usc/t26/s25F/",
        "https://www.govinfo.gov/content/pkg/FR-2026-10-02/html/2026-20277.htm",
    )
