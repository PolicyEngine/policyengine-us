from policyengine_us.model_api import *


class wy_ssp_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Wyoming State Supplemental Payment"
    definition_period = MONTH
    defined_for = StateCode.WY
    reference = (
        "https://ecom.wyo.gov/m1800-other-programs/m1804-state-supplemental-payments",
        "https://wyoleg.gov/statutes/compress/title42.pdf#page=7",
    )

    def formula(person, period, parameters):
        receives_ssi = (person("ssi", period) > 0) | person("receives_ssi", period)
        p = parameters(period).gov.ssa.ssi.income.sources
        # W.S. 42-2-103(d) requires no other income in the month. The test
        # precedes SSI exclusions, and only positive amounts count, so a loss
        # in one source cannot offset a positive payment from another source.
        # NOTE: noncash support and income sources absent from the federal SSI
        # income model are not separately evaluated.
        sources = list(p.earned) + list(p.unearned)
        has_other_income = np.zeros_like(receives_ssi)
        for source in sources:
            has_other_income = has_other_income | (person(source, period) > 0)
        return receives_ssi & ~has_other_income
