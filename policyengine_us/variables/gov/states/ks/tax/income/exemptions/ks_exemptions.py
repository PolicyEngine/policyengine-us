from policyengine_us.model_api import *


class ks_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kansas exemptions amount"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/kansas/chapter-79/article-32/section-79-32-121/"
    defined_for = StateCode.KS

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ks.tax.income.exemptions
        veteran_exemptions_count = add(
            tax_unit,
            period,
            ["ks_disabled_veteran_exemptions_eligible_person"],
        )
        vetrans_exemption_amount = (
            veteran_exemptions_count * p.disabled_veteran.base
        )
        if p.by_filing_status.in_effect:
            filing_status = tax_unit("filing_status", period)
            base_amount = p.by_filing_status.amount[filing_status]
            dependents = tax_unit("tax_unit_dependents", period)
            dependent_amount = p.by_filing_status.dependent * dependents
            return base_amount + dependent_amount + vetrans_exemption_amount
        exemptions_count = tax_unit("ks_count_exemptions", period)
        return (
            exemptions_count * p.consolidated.amount + vetrans_exemption_amount
        )
