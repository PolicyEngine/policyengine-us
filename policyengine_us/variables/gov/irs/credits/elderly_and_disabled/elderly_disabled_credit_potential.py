from policyengine_us.model_api import *


class elderly_disabled_credit_potential(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Potential value of the Elderly or disabled credit"
    documentation = "Schedule R credit for the elderly and the disabled"
    unit = USD
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/22#a",
        "https://www.law.cornell.edu/uscode/text/26/22#e_1",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.credits.elderly_or_disabled
        # Section 22(e)(1): a married individual filing a separate return
        # gets the credit only if the spouses lived apart all year.
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        lived_together = tax_unit("cohabitating_spouses", period)
        allowed = ~(separate & lived_together)
        return allowed * p.rate * tax_unit("section_22_income", period)
