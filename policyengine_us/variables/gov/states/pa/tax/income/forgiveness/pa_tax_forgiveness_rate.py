from policyengine_us.model_api import *


class pa_tax_forgiveness_rate(Variable):
    value_type = float
    entity = TaxUnit
    label = "PA tax forgiveness on eligibility income"
    unit = "/1"
    definition_period = YEAR
    reference = "https://www.pa.gov/content/dam/copapwp-pagov/en/revenue/documents/formsandpublications/formsforindividuals/pit/documents/2021/2021_pa-40in.pdf#page=39"
    defined_for = StateCode.PA

    def formula(tax_unit, period, parameters):
        eligibility_income = tax_unit("pa_eligibility_income", period)
        person = tax_unit.members
        is_child_dependent = person("is_qualifying_child_dependent", period)
        child_dependents = tax_unit.sum(is_child_dependent)
        # The base doubles for a married claimant, whose eligibility income
        # includes the spouse's. A separate filer who lives apart from the
        # spouse for the last six months of the year (or under a written
        # separation agreement) is not considered married, so a separate
        # filer gets the doubled base only when the tax unit holds a spouse.
        filing_status = tax_unit("filing_status", period)
        filing_statuses = filing_status.possible_values
        joint = filing_status == filing_statuses.JOINT
        separate = filing_status == filing_statuses.SEPARATE
        married_separate = separate & tax_unit("tax_unit_married", period)
        base_multiplier = where(joint | married_separate, 2, 1)
        p = parameters(period).gov.states.pa.tax.income.forgiveness
        base = p.base * base_multiplier
        rate_per_dependent = p.dependent_rate
        eligibility_income_increment = base + (rate_per_dependent * child_dependents)
        excess = eligibility_income - eligibility_income_increment
        forgiveness_increment = p.rate_increment
        increments = np.ceil(excess / forgiveness_increment)
        percent = p.tax_back
        return min_(max_(1 - percent * increments, 0), 1)
