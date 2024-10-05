from policyengine_us.model_api import *


class va_child_dependent_care_deduction_cdcc_limit(Variable):
    value_type = float
    entity = TaxUnit
    label = (
        "Federal CDCC-relevant care expense limit for Virginia tax purposes"
    )
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2021-760-instructions.pdf#page=29"
    defined_for = StateCode.VA

    def formula(tax_unit, period, parameters):
        if period.start.year == 2021:
            instant_str = f"2020-01-01"
        else:
            instant_str = period
        p = parameters(instant_str).gov.irs.credits.cdcc
        capped_count_cdcc_eligible = tax_unit(
            "capped_count_cdcc_eligible", period
        )
        return p.max * capped_count_cdcc_eligible
