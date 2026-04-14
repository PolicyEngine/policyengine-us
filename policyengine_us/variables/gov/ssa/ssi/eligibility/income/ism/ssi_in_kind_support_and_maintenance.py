from policyengine_us.model_api import *


class ssi_in_kind_support_and_maintenance(Variable):
    value_type = float
    entity = Person
    label = "SSI in-kind support and maintenance"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/20/416.1130",
        "https://www.law.cornell.edu/cfr/text/20/416.1140",
    )

    def formula(person, period, parameters):
        # ISM is counted as unearned income for own-household recipients
        # who receive shelter (or food, pre-10/2024) support.
        # The PMV rule caps ISM at the presumed maximum value.
        # If the recipient provides an actual shelter value (rebuttal),
        # ISM is the lesser of the actual value and the PMV.
        # Another person's household: VTR FBR adjustment, not here.
        # Child in parental household: deeming replaces ISM.
        # Medical treatment facility: ISM not countable ($30 rate).
        pmv_applies = person("ssi_pmv_applies", period)
        pmv_amount = person("ssi_pmv_amount", period)
        actual_value = person("ssi_shelter_support_value", period)
        has_actual = actual_value > 0
        ism_value = where(has_actual, min_(pmv_amount, actual_value), pmv_amount)
        return pmv_applies * ism_value
