from policyengine_us.model_api import *


class mn_wfc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Minnesota working family credit eligibilty status"
    definition_period = YEAR
    reference = (
        "https://www.revisor.mn.gov/statutes/2021/cite/290.0671",
        "https://www.revisor.mn.gov/statutes/cite/290.0671",
        "https://www.law.cornell.edu/uscode/text/26/32#c_1_A_ii",
    )
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mn.tax.income.credits.cwfc
        person = tax_unit.members
        # determine demographic eligibility using WFC rules
        has_child = tax_unit("tax_unit_children", period) > 0
        age = person("age", period)
        min_age = p.wfc.eligible.childless_adult_age.minimum
        max_age = p.wfc.eligible.childless_adult_age.maximum
        in_age_range = (age >= min_age) & (age <= max_age)
        age_eligible = in_age_range & ~person("is_tax_unit_dependent", period)
        # Minn. Stat. 290.0671 subd. 1 allows the credit to an individual
        # eligible for the federal credit under IRC 32, whose childless route
        # requires that the filer "is not a dependent for whom a deduction
        # under section 151 is allowable to another taxpayer"; on a joint
        # return, neither spouse may be (IRS Publication 596).
        dependent_elsewhere = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        childless_eligible = tax_unit.any(age_eligible) & ~dependent_elsewhere
        demographic_eligible = has_child | childless_eligible
        # determine investment income eligibility using federal EITC rules
        invinc_eligible = tax_unit("eitc_investment_income_eligible", period)
        # determine if tax unit has separate filing status
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        # determine WFC eligibility
        return demographic_eligible & invinc_eligible & ~separate
