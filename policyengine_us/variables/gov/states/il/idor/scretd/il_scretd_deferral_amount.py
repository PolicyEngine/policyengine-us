from policyengine_us.model_api import *


class il_scretd_deferral_amount(Variable):
    value_type = float
    entity = TaxUnit
    label = "Illinois Senior Citizens Real Estate Tax Deferral amount"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.IL
    reference = (
        "https://www.ilga.gov/legislation/ilcs/documents/032000300K3.htm",
        "https://tax.illinois.gov/research/publications/pio-64.html",
    )

    def formula(tax_unit, period, parameters):
        # Note: This is a loan, not a benefit. The deferred amount accrues
        # interest (3% simple for 2023+, 6% prior) and must be repaid upon
        # sale, transfer, or death. Interest accumulation is not modeled.
        p = parameters(period).gov.states.il.idor.scretd
        eligible = tax_unit("il_scretd_eligible", period)
        real_estate_taxes = add(tax_unit, period, ["real_estate_taxes"])
        capped_deferral = min_(real_estate_taxes, p.max_annual_deferral)
        return where(eligible, capped_deferral, 0)
