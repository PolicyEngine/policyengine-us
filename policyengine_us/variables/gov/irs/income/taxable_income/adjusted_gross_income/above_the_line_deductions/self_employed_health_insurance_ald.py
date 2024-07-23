from policyengine_us.model_api import *


class self_employed_health_insurance_ald(Variable):
    value_type = float
    entity = TaxUnit
    label = "Self-employed health insurance ALD"
    unit = USD
    documentation = "Above-the-line deduction for self-employed health insurance contributions."
    definition_period = YEAR
    uprating = "calibration.gov.cbo.income_by_source.adjusted_gross_income"
    reference = "https://www.law.cornell.edu/uscode/text/26/162#l"

    adds = ["self_employed_health_insurance_ald_person"]
