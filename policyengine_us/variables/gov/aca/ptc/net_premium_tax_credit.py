from policyengine_us.model_api import *


class net_premium_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Net premium tax credit reported on the federal return"
    unit = USD
    definition_period = YEAR
    default_value = 0
    documentation = (
        "Actual net premium tax credit after advance-payment reconciliation: "
        "max(Form 8962 line 24 minus line 25, 0), reported on line 26. This "
        "return-amount input is distinct from assigned_aca_ptc, which does not "
        "reconcile advance payments."
    )
    reference = "https://www.irs.gov/pub/irs-prior/f8962--2025.pdf#page=1"
