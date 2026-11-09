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
        # Utah Code 59-10-1018(1)(g) multiplies the exemption by "the number
        # of the claimant's qualifying dependents", those for whom the
        # claimant is allowed an IRC 24 credit (ut_qualifying_dependent).
        person = tax_unit.members
        return tax_unit.sum(person("ut_qualifying_dependent", period))
