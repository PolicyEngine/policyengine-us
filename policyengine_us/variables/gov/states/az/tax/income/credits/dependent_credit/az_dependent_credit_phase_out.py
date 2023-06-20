from policyengine_us.model_api import *


class az_dependent_credit_phase_out(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona dependent care credit phase out"
    unit = USD
    documentation = "https://azdor.gov/file/12346/download?token=7FAdFbnT"
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        income = tax_unit("adjusted_gross_income", period)
        p = parameters(
            period
        ).gov.states.az.tax.income.credits.dependent_credit.reduction
        filing_status = tax_unit("filing_status", period)
        threshold = max_(income - p.start[filing_status], 0)
        return p.rate.calc(threshold)
