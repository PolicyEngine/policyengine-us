from policyengine_us.model_api import *


class ca_dependent_care_assistance_addition(Variable):
    value_type = float
    entity = TaxUnit
    label = "California addition for dependent care benefits excluded federally"
    documentation = (
        "The federal IRC 129 exclusion above California's own exclusion. "
        "Federal AGI leaves out the whole federal exclusion, but California "
        "kept its $5,000 ($2,500) cap when the federal cap rose for 2021 and "
        "from 2026, so the difference goes back into California AGI "
        "(Schedule CA (540), Part I, line 1, column C)."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ftb.ca.gov/forms/2021/2021-540-ca-instructions.html",
        "https://www.ftb.ca.gov/about-ftb/data-reports-plans/Summary-of-Federal-Income-Tax-Changes/index.html#PL-119-21-70404",
    )
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        federal = tax_unit("dependent_care_assistance_exclusion", period)
        california = tax_unit("ca_dependent_care_assistance_exclusion", period)
        return max_(federal - california, 0)
