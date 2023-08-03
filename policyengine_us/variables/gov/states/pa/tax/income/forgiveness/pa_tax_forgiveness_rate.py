from policyengine_us.model_api import *


class pa_tax_forgiveness_rate(Variable):
    value_type = float
    entity = TaxUnit
    label = "PA tax forgiveness on eligibility income"
    unit = "/1"
    definition_period = YEAR
    reference = "https://www.revenue.pa.gov/FormsandPublications/FormsforIndividuals/PIT/Documents/2021/2021_pa-40in.pdf#page=39"
    defined_for = StateCode.PA

    def formula(tax_unit, period, parameters):
        eligibility_income = tax_unit("pa_eligibility_income", period)
        person = tax_unit.members
        is_child_dependent = person("is_child_of_tax_head", period) & person(
            "is_tax_unit_dependent", period
        )
        child_dependents = tax_unit.sum(is_child_dependent)
        # filing status affects the base, where it doubles for married claimants
        filing_status = tax_unit("filing_status", period)
        filing_statuses = filing_status.possible_values
        joint_separate = (filing_status == filing_statuses.JOINT) | (
            filing_status == filing_statuses.SEPARATE
        )
        base_multiplier = where(joint_separate, 2, 1)
        p = parameters(period).gov.states.pa.tax.income.forgiveness
        base = p.base * base_multiplier
        rate_per_dependent = p.dependent_rate
        eligibility_income_increment = base + (
            rate_per_dependent * child_dependents
        )
        excess = eligibility_income - eligibility_income_increment
        forgiveness_increment = p.rate_increment
        increments = np.ceil(excess / forgiveness_increment)
        percent = p.tax_back
        return min_(max_(1 - percent * increments, 0), 1)
