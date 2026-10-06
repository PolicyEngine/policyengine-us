from policyengine_us.model_api import *


class ky_tuition_tax_credit_eligible(Variable):
    value_type = float
    entity = TaxUnit
    label = "Eligible for the Kentucky tuition tax credit"  # Form 8863-K
    unit = USD
    definition_period = YEAR
    reference = "https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=29060"  # KRS 141.069(4)
    defined_for = StateCode.KY

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("ky_filing_status", period)
        # A taxpayer who is married under IRC 7703 is ineligible when filing a
        # separate return (Filing Status 4).
        return filing_status != filing_status.possible_values.SEPARATE
