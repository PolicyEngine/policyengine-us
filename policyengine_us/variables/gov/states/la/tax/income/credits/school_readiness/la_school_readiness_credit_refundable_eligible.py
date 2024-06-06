from policyengine_us.model_api import *


class la_school_readiness_credit_refundable_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Louisiana refundable school readiness tax credit eligibility"
    definition_period = YEAR
    reference = "https://www.revenue.louisiana.gov/IndividualIncomeTax/SchoolReadinessTaxCredit"
    defined_for = StateCode.LA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.la.tax.income.credits.cdcc.refundable
        # determine if it is nonrefundable or refundable
        us_agi = tax_unit("adjusted_gross_income", period)
        top_threshold = p.match.thresholds[-1]
        return us_agi <= top_threshold
