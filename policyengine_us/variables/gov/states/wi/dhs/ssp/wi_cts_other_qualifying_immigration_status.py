from policyengine_us.model_api import *


class wi_cts_other_qualifying_immigration_status(Variable):
    value_type = bool
    entity = Person
    label = "Wisconsin CTS child has another qualifying immigration status"
    definition_period = MONTH
    defined_for = StateCode.WI
    # PDF pages 19-20
    reference = "https://www.dhs.wisconsin.gov/publications/p23131-25-01.pdf#page=19"
    documentation = "True for a child with qualifying lawful temporary resident status or verified PRUCOL status under Handbook 3.1.4 items 3 and 4 that the immigration status input does not identify. Temporary protected status alone does not qualify (8 U.S.C. 1254a(f)(1))."
