from policyengine_us.model_api import *


class pa_tax_forgiveness_rate(Variable):
    value_type = float
    entity = TaxUnit
    label = "PA tax forgiveness on eligibility income"
    unit = "/1"
    definition_period = YEAR
    reference = (
        "https://www.pa.gov/content/dam/copapwp-pagov/en/revenue/documents/formsandpublications/formsforindividuals/pit/documents/2021/2021_pa-40in.pdf#page=39",
        "https://www.legis.state.pa.us/WU01/LI/LI/US/PDF/1971/0/0002..PDF#page=113",
        "https://www.law.cornell.edu/uscode/text/26/152#b_1",
    )
    defined_for = StateCode.PA

    def formula(tax_unit, period, parameters):
        eligibility_income = tax_unit("pa_eligibility_income", period)
        person = tax_unit.members
        is_child_dependent = person("is_qualifying_child_dependent", period)
        # A dependent child must be "the dependent of a claimant for purposes
        # of section 151" (Tax Reform Code section 301(e.1)), and a return on
        # which the filer (or, if joint, either spouse) can be claimed as a
        # dependent has no dependents (IRC 152(b)(1)).
        filer_is_dependent = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        child_dependents = where(
            filer_is_dependent, 0, tax_unit.sum(is_child_dependent)
        )
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
        eligibility_income_increment = base + (rate_per_dependent * child_dependents)
        excess = eligibility_income - eligibility_income_increment
        forgiveness_increment = p.rate_increment
        increments = np.ceil(excess / forgiveness_increment)
        percent = p.tax_back
        return min_(max_(1 - percent * increments, 0), 1)
