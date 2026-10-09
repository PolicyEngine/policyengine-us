from policyengine_us.model_api import *


class total_misc_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Total miscellaneous deductions subject to the AGI floor"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/67#b"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.deductions.itemized.misc
        # The head's and spouse's own expenses; a dependent's job expenses
        # and return preparation fees belong on the dependent's return.
        return tax_unit_non_dep_add(tax_unit, period, p.sources)
