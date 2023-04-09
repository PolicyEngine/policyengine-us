from policyengine_us.model_api import *


class mn_wfc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Minnesota working family credit eligibilty status"
    definition_period = YEAR
    reference = (
        "https://www.revisor.mn.gov/statutes/2021/cite/290.0671"
        "https://www.revisor.mn.gov/statutes/cite/290.0671"
    )
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        eitc = parameters(period).gov.irs.credits.eitc
        wfc = parameters(period).gov.states.mn.tax.income.credits.wfc
        person = tax_unit.members
        # determine demographic eligibility using WFC rules
        has_child = tax_unit("tax_unit_children", period) > 0
        age = person("age", period)
        min_age = wfc.eligible.childless_adult_age.minimum
        max_age = wfc.eligible.childless_adult_age.maximum
        in_age_range = (age >= min_age) & (age <= max_age)
        age_eligible = in_age_range & ~person("is_tax_unit_dependent", period)
        demographic_eligible = has_child | tax_unit.any(age_eligible)
        # the MN WFC has no investment income eligibility rules
        # determine if tax unit has separate filing status
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        # determine WFC eligibility
        return demographic_eligible & ~separate
