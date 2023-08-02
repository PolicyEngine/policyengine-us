from policyengine_us.model_api import *
import numpy as np


class la_cdcc_non_refundable(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana non refundable cdcc"
    unit = USD
    definition_period = YEAR
    reference = "http://legis.la.gov/Legis/Law.aspx?d=101769"
    defined_for = StateCode.LA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.la.tax.income.credits
        # determine AGI eligibility
        us_agi = tax_unit("adjusted_gross_income", period)
        agi_eligible = us_agi > p.cdcc.agi_threshold
        # determine LA nonrefundable cdcc amount
        us_cdcc = tax_unit("cdcc", period)
        la_non_refundable_cdcc = us_cdcc * p.cdcc.non_refundable.rate.calc(
            us_agi
        )
        la_non_refundable_cdcc = np.where(
            us_agi > p.cdcc.non_refundable.upper_bracket.income_threshold,
            np.minimum(
                p.cdcc.non_refundable.upper_bracket.max_amount,
                la_non_refundable_cdcc,
            ),
            la_non_refundable_cdcc,
        )

        return agi_eligible * la_non_refundable_cdcc
