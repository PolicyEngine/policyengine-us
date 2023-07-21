from policyengine_us.model_api import *


class nm_cdcc_eligible(Variable):
    value_type = float
    entity = TaxUnit
    label = "Eligible for the New Mexico dependent child day care credit"
    defined_for = StateCode.NM
    unit = USD
    definition_period = YEAR
    reference = "https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/856ebf4b-3814-49dd-8631-ebe579d6a42b/Personal%20Income%20Tax.pdf"  # p63

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nm.tax.income.credits.cdcc
        # Filer has to be be gainfully employed to receive credit
        employed = tax_unit("tax_unit_earned_income", period) > 0
        # Filer can not receive tanf to be eligible
        receives_tanf = tax_unit.spm_unit("tanf", period)
        # Filers have to have state agi below $30,160
        nm_agi = tax_unit("nm_agi", period)
        agi_eligible = nm_agi <= p.income_threshold
        eligible = employed & receives_tanf & agi_eligible
        return eligible
