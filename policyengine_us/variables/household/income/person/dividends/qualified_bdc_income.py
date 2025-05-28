from policyengine_us.model_api import *


class qualified_bdc_income(Variable):
    value_type = float
    entity = Person
    label = "Business Development Company dividend income"
    unit = USD
    documentation = "Business Development Company Dividend Income. Part of the QBID calculation."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/1#h_11"
    uprating = "calibration.gov.irs.soi.qualified_dividend_income"
