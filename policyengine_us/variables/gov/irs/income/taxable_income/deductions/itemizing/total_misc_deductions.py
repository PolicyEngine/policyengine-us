from policyengine_us.model_api import *


class total_misc_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Total miscellaneous deductions subject to the AGI floor"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/67#b"

    def formula(tax_unit, period, parameters):
        sources = parameters(period).gov.irs.deductions.itemized.misc.sources
        # Investment fees belong to the filer's return; preserve the existing
        # aggregation of the other miscellaneous expense sources.
        return tax_unit_non_dep_add(
            tax_unit,
            period,
            sources,
            include_dependents=tuple(
                source for source in sources if source != "investment_expenses"
            ),
        )
