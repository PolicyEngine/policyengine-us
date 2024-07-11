from policyengine_us.model_api import *


class nm_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico EITC"
    unit = USD
    definition_period = YEAR
    reference = "https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/856ebf4b-3814-49dd-8631-ebe579d6a42b/Personal%20Income%20Tax.pdf"  # 7-2-18.15
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        eligible = tax_unit("nm_eitc_eligible", period)
        maximum = tax_unit("eitc_maximum", period)
        phased_in = tax_unit("eitc_phased_in", period)
        reduction = tax_unit("eitc_reduction", period)
        limitation = max_(0, maximum - reduction)
        eitc = eligible * min_(phased_in, limitation)
        rate = parameters(period).gov.states.nm.tax.income.credits.eitc.match
        return eitc * rate
