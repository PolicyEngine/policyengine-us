from policyengine_us.model_api import *


class pr_earned_income_credit(Variable):
    value_type = float
    unit = USD
    entity = TaxUnit
    label = "Puerto Rico earned income credit"
    definition_period = YEAR
    reference = "https://hacienda.pr.gov/sites/default/files/schedule_ct_rev._jul_5_23_informative_-_instructions.pdf#page=2"
    defined_for = "pr_earned_income_credit_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.territories.pr.tax.income.credits.earned_income

        child_count = tax_unit("eitc_child_count", period)
        filing_status = tax_unit("filing_status", period)
        person = tax_unit.members
        # only sum up gross income of tax unit head or spouses
        gross_income = tax_unit.sum(
            person("pr_gross_income_person", period)
            * (person("is_tax_unit_head_or_spouse", period))
        )

        # compute credit
        phase_in = min_(
            gross_income * p.phase_in_rate.calc(child_count),
            p.max_amount.calc(child_count),
        )

        phase_out_rate = p.phase_out.rate.calc(child_count)
        phase_out_threshold = select(
            [
                filing_status == filing_status.possible_values.SINGLE,
                filing_status == filing_status.possible_values.JOINT,
            ],
            [
                p.phase_out.threshold.single.calc(child_count),
                p.phase_out.threshold.joint.calc(child_count),
            ],
        )
        # could be negative if gross income not over threshold, so make the minimum value 0
        phase_out = max_(
            0, (gross_income - phase_out_threshold) * phase_out_rate
        )
        # minimum value 0 in case person isn't eligible for any amount of credit
        return max_(0, phase_in - phase_out)
