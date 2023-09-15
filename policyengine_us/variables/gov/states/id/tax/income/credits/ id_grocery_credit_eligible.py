from policyengine_us.model_api import *


class id_grocery_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho grocery credit"
    unit = USD
    definition_period = YEAR
    defined_for = "StateCode.ID"

    def formula(tax_unit, period, parameters):
        age_head = tax_unit("head_aged", period)
        age_spouse = tax_unit("age_spouse ", period)

        p = parameters(period).gov.states.id.tax.income.credits.gc

        head_qualifies = age_head >= p.eligibility
        spouse_qualifies = age_spouse >= p.eligibility

        # 100$ for each dependent
        person1 = tax_unit.members = p.snap_threshold.Household_Size
        person = person1("income", period) > p.snap_threshold
        dependent = person(
            "is_tax_unit_dependent", period
        )  # example: [0, 0, 1, 1, 1]
        total_dependents = tax_unit.sum(dependent)  # example sum [3]
        dependet_amount = total_dependents * p.amount_dependent

        # 20$ extra for each aged person
        person_aged = person("age", period) > p.age_older_eligibility
        total_aged = tax_unit.sum(person_aged)
        aged_amount = total_aged * p.amount_65_older

        # determine age head and spouse
        filing_status = tax_unit("filing_status", period)
        joint_amount = where(head_aged & spouse_aged, two_aged, one_aged)
        joint = filing_status == filing_status.possible_values.JOINT
        final_joint_amount = where(joint, joint_amount, other_amount)
        income = tax_unit("id_agi", period)

        # 100$ for self
        return final_joint_amount + dependet_amount + aged_amount
