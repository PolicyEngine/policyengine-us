from policyengine_us.model_api import *


class snap_farm_rent_income(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "SNAP farm rental income"
    reference = (
        "https://www.law.cornell.edu/uscode/text/7/2014#d_9",
        "https://www.law.cornell.edu/cfr/text/7/273.9#b_1_ii",
        "https://www.law.cornell.edu/cfr/text/7/273.9#b_2_ii",
        "https://www.law.cornell.edu/cfr/text/7/273.11#a_2_ii",
    )
    unit = USD

    def formula(person, period, parameters):
        # farm_rent_income is Form 4835 rent from a landowner who does not
        # materially participate in the farm. 7 CFR 273.9(b)(1)(ii) makes
        # owning rental property a self-employment enterprise, and 7 U.S.C.
        # 2014(d)(9) and 7 CFR 273.11(a)(2)(ii) offset self-employment
        # losses against other household income only for self-employed
        # farmers, so a farm rent loss is floored at zero.
        return max_(person("farm_rent_income", period), 0)
