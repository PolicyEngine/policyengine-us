from policyengine_us.model_api import *


class snap_gross_self_employment_income_person(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "SNAP gross self-employment income per person"
    reference = (
        "https://www.law.cornell.edu/cfr/text/7/273.9#b_1",
        "https://www.law.cornell.edu/cfr/text/7/273.11#a_2_ii",
    )
    unit = USD

    def formula(person, period, parameters):
        # 7 CFR 273.11(a)(2)(ii) offsets losses against other household
        # income only for farming operations. The self-employment income
        # modeled here is non-farm, so each enterprise's loss is floored
        # at zero rather than netted against other members' income.
        regular = person("self_employment_income_before_lsr", period)
        sstb = person("sstb_self_employment_income_before_lsr", period)
        return max_(regular, 0) + max_(sstb, 0)
