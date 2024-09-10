from policyengine_us.model_api import *


class ks_disabled_veteran_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kansas disabled veteran exemptions"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/kansas/chapter-79/article-32/section-79-32-121/"
    defined_for = StateCode.KS

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ks.tax.income.exemptions
        return p.veterans_matched * adds(tax_unit, period, ["ks_disabled_veteran_exemptions_person"])
        