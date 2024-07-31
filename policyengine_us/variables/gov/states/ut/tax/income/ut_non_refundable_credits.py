from policyengine_us.model_api import *


class ut_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah non-refundable tax credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.UT

    adds = "gov.states.ut.tax.income.credits.non_refundable"
