from policyengine_us.model_api import *


class hi_cdcc_qualifying_individuals(Variable):
    value_type = int
    entity = TaxUnit
    label = "Number of qualifying individuals for the Hawaii child and dependent care credit"
    defined_for = StateCode.HI
    definition_period = YEAR
    # PDF pages 46-47: HRS 235-55.6(a)(1) and (b)(1).
    reference = "https://files.hawaii.gov/tax/legal/hrs/hrs_235.pdf#page=46"

    def formula(tax_unit, period, parameters):
        # Hawaii's count departs from the federal one only on a return with
        # a filer who can be claimed as a dependent.
        dependent_filer = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        return where(
            dependent_filer,
            add(tax_unit, period, ["hi_cdcc_qualifying_individual"]),
            tax_unit("count_cdcc_eligible", period),
        )
