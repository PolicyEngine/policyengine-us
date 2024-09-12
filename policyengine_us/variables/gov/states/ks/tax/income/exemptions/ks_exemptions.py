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
        exemptions_count = tax_unit("ks_count_exemptions", period)
        base_exemptions = exemptions_count * p.amount.base
        veteran_exemptions_count = add(
            tax_unit,
            period,
            ["ks_disabled_veteran_exemptions_eligible_person"],
        )
        additional_exemptions = veteran_exemptions_count * p.amount.disabled_veteran

        return base_exemptions + additional_exemptions
