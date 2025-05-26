from policyengine_us.model_api import *


class qualified_bdc_income(Variable):
    value_type = float
    entity = Person
    label = "Business Development Company dividend income"
    unit = USD
    documentation = "Business Development Company Dividend Income. Part of the QBID calculation."
    definition_period = YEAR
    uprating = "calibration.gov.irs.soi.self_employment_income"  # TODO: Update
