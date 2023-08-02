from policyengine_us.model_api import *


class ky_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky cdcc"
    unit = USD
    definition_period = YEAR
    reference = "https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=29058"  # (d)
    defined_for = StateCode.KY

    def formula(tax_unit, period, parameters):
        dependent_care_credit = tax_unit("cdcc", period)
        rate = parameters(
            period
        ).gov.states.ky.tax.income.credits.dependent_care_service.match
        return dependent_care_credit * rate
