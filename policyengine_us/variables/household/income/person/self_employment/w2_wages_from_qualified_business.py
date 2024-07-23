from policyengine_us.model_api import *


class w2_wages_from_qualified_business(Variable):
    value_type = float
    entity = Person
    label = "W2 wages"
    unit = USD
    documentation = "Share of wages paid by this person to employees as part of a pass-through qualified business or trade."
    definition_period = YEAR
    uprating = "calibration.gov.cbo.income_by_source.adjusted_gross_income"
    reference = "https://www.law.cornell.edu/uscode/text/26/199A#b_4"
