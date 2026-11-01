from policyengine_us.model_api import *


class head_or_spouse_is_dependent_elsewhere_without_filing_exception(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Either filer claimable elsewhere without the claimant filing exception"
    documentation = (
        "Whether a tax-unit head or spouse is claimable on another return "
        "without the claimant filing exception. Symmetric Dependent Taxpayer "
        "Test gate; other claimability rules use the ordinary helper."
    )
    reference = (
        "https://www.irs.gov/pub/irs-prior/p596--2025.pdf#page=18",
        "https://www.irs.gov/pub/irs-prior/p501--2025.pdf#page=11",
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        dependent = person("is_dependent_elsewhere_without_filing_exception", period)
        filer = person("is_tax_unit_head_or_spouse", period)
        return tax_unit.any(dependent & filer)
