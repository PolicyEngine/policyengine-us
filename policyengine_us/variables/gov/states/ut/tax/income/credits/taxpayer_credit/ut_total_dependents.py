from policyengine_us.model_api import *


class ut_total_dependents(Variable):
    value_type = int
    entity = TaxUnit
    label = "Utah total dependents"
    unit = USD
    documentation = "Form TC-40, line 2c"
    definition_period = YEAR
    defined_for = StateCode.UT
    reference = "https://le.utah.gov/xcode/Title59/Chapter10/59-10-S1018.html"

    def formula(tax_unit, period, parameters):
        # Utah Code 59-10-1018(1)(c) counts "qualifying dependents": those
        # "with respect to whom the claimant is allowed to claim a tax credit
        # under Section 24". Under IRC 152(b)(1) a return on which the filer
        # (or, if joint, either spouse) can be claimed as a dependent has no
        # dependents, and so no such credit.
        filer_is_dependent = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        dependents = tax_unit("tax_unit_count_dependents", period)
        return where(filer_is_dependent, 0, dependents)
