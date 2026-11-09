from policyengine_us.model_api import *


class nj_other_additions(Variable):
    value_type = float
    entity = Person
    label = "New Jersey other additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NJ
    documentation = (
        "Income taxable in New Jersey that belongs on Form NJ-1040 lines 15-26 "
        "(not lines 16b or 20b) and that PolicyEngine does not otherwise include "
        "in New Jersey gross income, entered as a positive amount. Do not include "
        "miscellaneous income or estate and trust income, which PolicyEngine already reports on line 26."
    )
    reference = "https://www.nj.gov/treasury/taxation/pdf/current/1040i.pdf#page=21"
