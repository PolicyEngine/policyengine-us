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
        exemptions_count = tax_unit("ks_count_exemptions", period)
        p = parameters(period).gov.states.ks.tax.income.exemptions
        disabled_veteran_exemption = tax_unit("ks_disabled_veteran_exemptions", period)
        base_exemptions = exemptions_count * p.amount
        return base_exemptions + disabled_veteran_exemption
