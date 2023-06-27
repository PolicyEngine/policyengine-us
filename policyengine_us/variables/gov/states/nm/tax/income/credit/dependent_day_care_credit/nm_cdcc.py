from policyengine_us.model_api import *


class nm_cdcc(Variable):
    # cdcc: child day care credit
    value_type = float
    entity = TaxUnit
    label = "New Mexico dependent child day care credit"
    defined_for = StateCode.NM
    unit = USD
    definition_period = YEAR
    reference = 'https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/856ebf4b-3814-49dd-8631-ebe579d6a42b/Personal%20Income%20Tax.pdf' #p63

    def formula(tax_unit, period, parameters):
       # Get New Mexico CDCC rate
       cdcc_rate = parameters(period).gov.states.nm.tax.income.credits.cdcc.rate
       # Get New Mexico actual compensation
       expenses = tax_unit('cdcc_relevant_expenses', period)
       # Get New Mexico maximum CDCC with limitations
       cdcc_max = tax_unit('nm_cdcc_max', period)
       return min_(cdcc_max, expenses*cdcc_rate)

