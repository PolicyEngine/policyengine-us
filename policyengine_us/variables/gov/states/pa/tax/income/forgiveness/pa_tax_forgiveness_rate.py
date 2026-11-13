from policyengine_us.model_api import *


class pa_tax_forgiveness_rate(Variable):
    value_type = float
    entity = TaxUnit
    label = "PA tax forgiveness on eligibility income"
    unit = "/1"
    definition_period = YEAR
    reference = (
        "https://www.palegis.us/statutes/unconsolidated/law-information/view-statute?txtType=PDF&SessYr=1971&SessInd=0&ActNum=0002.&chpt=003.&subchpt=000.&sctn=004.&subsctn=000.",  # 72 P.S. 7304(d)(1)
        "https://www.pa.gov/content/dam/copapwp-pagov/en/revenue/documents/formsandpublications/formsforindividuals/pit/documents/2025/2025_pa-40in.pdf#page=36",
        "https://www.pa.gov/content/dam/copapwp-pagov/en/revenue/documents/formsandpublications/formsforindividuals/pit/documents/2021/2021_pa-40in.pdf#page=39",
        "https://www.legis.state.pa.us/WU01/LI/LI/US/PDF/1971/0/0002..PDF#page=113",
        "https://www.law.cornell.edu/uscode/text/26/152#b_1",
    )
    defined_for = StateCode.PA

    def formula(tax_unit, period, parameters):
        own_eligibility_income = tax_unit("pa_eligibility_income", period)
        person = tax_unit.members
        is_child_dependent = person("is_qualifying_child_dependent", period)
        # A dependent child must be "the dependent of a claimant for purposes
        # of section 151" (Tax Reform Code section 301(e.1)), and a return on
        # which the filer (or, if joint, either spouse) can be claimed as a
        # dependent has no dependents (IRC 152(b)(1)).
        # Publication 501 excepts a return whose would-be claimant files only
        # for a refund.
        filer_is_dependent = tax_unit(
            "head_or_spouse_is_dependent_elsewhere_without_filing_exception", period
        )
        child_dependents = where(
            filer_is_dependent, 0, tax_unit.sum(is_child_dependent)
        )
        # 72 P.S. 7304(d)(1)(i)-(ii): a claimant who files a separate return
        # and lives apart from the spouse for all of the last six months of
        # the year (or under a written separation agreement) is not
        # considered married, and uses the single base on their own income
        # (Eligibility Income Table 1). Every other married claimant, joint
        # or separate, uses the doubled base on the joint eligibility income
        # of both spouses (Table 2).
        filing_status = tax_unit("filing_status", period)
        filing_statuses = filing_status.possible_values
        joint = filing_status == filing_statuses.JOINT
        separate = filing_status == filing_statuses.SEPARATE
        spouse_in_unit = tax_unit("tax_unit_married", period)
        lived_apart = tax_unit("eitc_spouses_lived_apart_last_six_months", period)
        unmarried_separate = separate & ~spouse_in_unit & lived_apart
        married_claimant = (joint | separate) & ~unmarried_separate
        # A married separate filer whose spouse files in another tax unit
        # adds that unit's eligibility income, found through the marital unit.
        is_head = person("is_tax_unit_head", period)
        head_unit_income = person.tax_unit("pa_eligibility_income", period) * is_head
        couple_income = person.marital_unit.sum(head_unit_income)
        joint_eligibility_income = tax_unit.sum(is_head * couple_income)
        eligibility_income = where(
            married_claimant & ~spouse_in_unit,
            joint_eligibility_income,
            own_eligibility_income,
        )
        base_multiplier = where(married_claimant, 2, 1)
        p = parameters(period).gov.states.pa.tax.income.forgiveness
        base = p.base * base_multiplier
        rate_per_dependent = p.dependent_rate
        eligibility_income_increment = base + (rate_per_dependent * child_dependents)
        excess = eligibility_income - eligibility_income_increment
        forgiveness_increment = p.rate_increment
        increments = np.ceil(excess / forgiveness_increment)
        percent = p.tax_back
        return min_(max_(1 - percent * increments, 0), 1)
