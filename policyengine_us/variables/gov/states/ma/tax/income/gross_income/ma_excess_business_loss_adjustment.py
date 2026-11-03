from policyengine_us.model_api import *


class ma_excess_business_loss_adjustment(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA excess business loss adjustment"
    documentation = (
        "Massachusetts Schedule X, line 6: the excess business loss under "
        "Section 461(l) as Massachusetts adopts it, added back to 5.0% income."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.mass.gov/doc/2024-form-1-instructions/download#page=20",
        "https://www.mass.gov/doc/2025-form-1-instructions/download#page=21",
        "https://www.mass.gov/technical-information-release/tir-26-4-massachusetts-conformity-to-certain-provisions-in-public-law-no-119-21",
    )
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ma.tax.income.excess_business_loss
        filing_status = tax_unit("filing_status", period)
        # Through 2025 this is the federal excess business loss (Form 1040,
        # Schedule 1, line 8p). Massachusetts does not adopt the OBBBA
        # threshold reset from 2026, so the loss is measured against the
        # Massachusetts threshold.
        net_business_loss = tax_unit("net_business_loss", period)
        excess_business_loss = max_(0, net_business_loss - p.threshold[filing_status])
        return p.in_effect * excess_business_loss
