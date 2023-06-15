from policyengine_us.model_api import *


class nm_working_families_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico working families credit"
    unit = USD
    definition_period = YEAR
    reference = "https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/856ebf4b-3814-49dd-8631-ebe579d6a42b/Personal%20Income%20Tax.pdf"  # 7-2-18.15
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        eitc = tax_unit("earned_income_tax_credit", period)
        rate = parameters(
            period
        ).gov.states.nm.tax.income.credits.working_families_tax.match
        return eitc * rate
