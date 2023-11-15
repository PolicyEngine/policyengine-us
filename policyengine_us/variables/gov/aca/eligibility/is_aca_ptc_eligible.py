from policyengine_us.model_api import *


class is_aca_ptc_eligible(Variable):
    value_type = bool
    entity = Person
    label = (
        "Person is eligible for ACA premium tax credit and pays ACA premium"
    )
    definition_period = YEAR

    def formula(person, period, parameters):
        # determine coverage eligibility for ACA plan
        medicaid_coverage = person("is_medicaid_eligible", period)
        eshi_coverage = person("is_aca_eshi_eligible", period)
        medicare_coverage = person("is_medicare_eligible", period)
        is_coverage_eligible = (
            ~medicaid_coverage & ~eshi_coverage & ~medicare_coverage
        )

        # determine income eligibility for ACA PTC
        p = parameters(period).gov.aca
        magi_frac = person.tax_unit("aca_magi_fraction", period)
        is_income_eligible = p.ptc_income_eligibility.calc(magi_frac)

        # determine which people pay an age-based ACA plan premium
        is_aca_adult = person("age", period) > p.max_child_age
        child_pays = person("aca_child_index", period) <= p.max_child_count
        pays_aca_premium = is_aca_adult | child_pays

        return is_coverage_eligible & is_income_eligible & pays_aca_premium
