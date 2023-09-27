from policyengine_us.model_api import *


class id_grocery_credit_enhancement_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the enhancement of the Idaho grocery credit"
    definition_period = YEAR
    defined_for = "id_grocery_credit_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.id.tax.income.credits.gc
        head_aged = tax_unit("head_aged", period) >= p.age_eligibility
        spouse_aged = tax_unit("age_spouse ", period) >= p.age_eligibility

        # determine age head and spouse
        filing_status = tax_unit("filing_status", period)
        joint = filing_status == filing_status.possible_values.JOINT

        joint_threshold = where(
            head_aged & spouse_aged,
            p.income_threshold.two_aged,
            p.income_threshold.one_aged[filing_status],
        )
        joint = filing_status == filing_status.possible_values.JOINT
        final_joint_amount = where(
            joint, joint_threshold, p.income_threshold.one_aged[filing_status]
        )
        income = tax_unit("id_agi", period)

        return income < final_joint_amount
