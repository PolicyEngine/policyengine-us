from policyengine_us.model_api import *


class ut_qualifying_dependent(Variable):
    value_type = bool
    entity = Person
    label = "Utah qualifying dependent"
    documentation = (
        "A dependent with respect to whom the claimant is allowed a federal "
        "child tax credit or credit for other dependents under IRC 24."
    )
    definition_period = YEAR
    defined_for = StateCode.UT
    reference = "https://le.utah.gov/xcode/Title59/Chapter10/C59-10-S1018_2026050620260506.pdf#page=1"  # (1)(c)

    def formula(person, period, parameters):
        # Utah Code 59-10-1018(1)(c): a qualifying dependent is "an individual
        # with respect to whom the claimant is allowed to claim a tax credit
        # under Section 24". ctc_individual_maximum is that IRC 24 amount
        # before the phase-out. It is zero for a dependent with no child or
        # other-dependent credit, such as one with no taxpayer identification
        # number. It is also zero on a return where a filer can be claimed as
        # a dependent (IRC 152(b)(1)), unless the filing exception applies.
        return person("ctc_individual_maximum", period) > 0
