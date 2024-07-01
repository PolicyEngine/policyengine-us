from policyengine_us.model_api import *


class la_school_readiness_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana school readiness tax credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.revenue.louisiana.gov/IndividualIncomeTax/SchoolReadinessTaxCredit"
    defined_for = StateCode.LA

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(
            period
        ).gov.states.la.tax.income.credits.school_readiness
        # determine school readiness credit amount
        child_care_credit = add(
            tax_unit, period, ["la_refundable_cdcc", "la_non_refundable_cdcc"]
        )
        eligible_child = person(
            "la_school_readiness_credit_eligible_child", period
        )
        quality_rating = person(
            "la_quality_rating_of_child_care_facility", period
        )
        child_credit_percent = child_care_credit * p.rate.calc(quality_rating)
        # la_cdcc times the percentage
        amount = eligible_child * child_credit_percent

        return tax_unit.sum(amount)
