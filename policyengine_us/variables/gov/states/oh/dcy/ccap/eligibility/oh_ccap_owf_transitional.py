from policyengine_us.model_api import *


class oh_ccap_owf_transitional(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Ohio CCAP caretaker in the transitional period after Ohio Works First"
    defined_for = StateCode.OH
    reference = "https://codes.ohio.gov/assets/laws/administrative-code/authenticated/5180/6/1/5180$6-1-02_20251102.pdf#page=7"
    # 5180:6-1-02(F)(1): the twelve months immediately following the end of
    # Ohio Works First participation. OWF-exit timing is not tracked, so this
    # is a direct caretaker input; per (F)(2) it should not be set for people
    # disqualified from OWF under R.C. 5101.83 or 5107.16.
