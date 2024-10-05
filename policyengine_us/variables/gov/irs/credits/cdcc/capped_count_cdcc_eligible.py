from policyengine_us.model_api import *


class capped_count_cdcc_eligible(Variable):
    value_type = int
    entity = TaxUnit
    label = "Capped child/dependent care eligiable count"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/21#c",
        "https://www.law.cornell.edu/uscode/text/26/21#d_1",
    )

    def formula(tax_unit, period, parameters):
        cdcc = parameters(period).gov.irs.credits.cdcc
        eligible_people = tax_unit("count_cdcc_eligible", period)
        return min_(cdcc.eligibility.max, eligible_people)
