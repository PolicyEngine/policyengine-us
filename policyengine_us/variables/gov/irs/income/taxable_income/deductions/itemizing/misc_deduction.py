from policyengine_us.model_api import *


class misc_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Miscellaneous deduction"
    unit = USD
    definition_period = YEAR
    uprating = "calibration.gov.cbo.income_by_source.adjusted_gross_income"
