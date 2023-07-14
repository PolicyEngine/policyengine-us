from policyengine_us.model_api import *


class nm_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico dependent child day care credit"
    defined_for = StateCode.NM
    unit = USD
    definition_period = YEAR
    reference = "https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/856ebf4b-3814-49dd-8631-ebe579d6a42b/Personal%20Income%20Tax.pdf"  # p63

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nm.tax.income.credits.cdcc
        # Maximum New Mexico CDCC amount
        nm_cdcc_max = tax_unit("nm_cdcc_max_amount", period)
        # Federal child and dependent care credit
        fed_cdcc = tax_unit("cdcc", period)
        # Filer has to be be gainfully employed to receive credit
        employed = tax_unit("earned_income", period) > 0
        # Filer can not receive tanf to be eligible 
        tanf = tax_unit("tanf", period) == 0
        # Filers have to have state agi below $30,160
        nm_agi = tax_unit("nm_agi"), period
        agi_eligible = nm_agi <= p.income_threshold
        eligible = employed & tanf & agi_eligible
        # The maximum nm amount is subtracted from the federal cdcc amount
        nm_cdcc = max_(fed_cdcc - nm_cdcc_max, 0)
        return eligible * nm_cdcc




