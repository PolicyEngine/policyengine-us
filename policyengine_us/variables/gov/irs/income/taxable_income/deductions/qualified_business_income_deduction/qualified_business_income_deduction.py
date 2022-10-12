from policyengine_us.model_api import *


class qualified_business_income_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Qualified business income deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/199A#b_1"

    def formula(tax_unit, period, parameters):
        max_qbid = tax_unit("maximum_qbid", period)
        limit = tax_unit("qbid_limit", period)
        return min_(max_qbid, limit)
