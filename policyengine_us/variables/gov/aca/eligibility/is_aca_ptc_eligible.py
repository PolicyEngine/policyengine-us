from policyengine_us.model_api import *


class is_aca_ptc_eligible(Variable):
    value_type = bool
    entity = Person
    label = (
        "Person is eligible for ACA premium tax credit and pays ACA premium"
    )
    definition_period = YEAR

    def formula(person, period, parameters):
        # determine status eligibility for ACA PTC
        fstatus = person.tax_unit("filing_status", period)
        separate = fstatus == fstatus.possible_values.SEPARATE
        immigration_eligible = person(
            "is_aca_ptc_immigration_status_eligible", period
        )
        taxpayer_has_itin = person.tax_unit("taxpayer_has_itin", period)
        is_status_eligible = (
            taxpayer_has_itin & ~separate & immigration_eligible
        )

        # determine coverage eligibility for ACA plan
        INELIGIBLE_COVERAGE = [
            "is_medicaid_eligible",
            "is_chip_eligible",
            "is_aca_eshi_eligible",
            "is_medicare_eligible",
        ]
        is_coverage_eligible = add(person, period, INELIGIBLE_COVERAGE) == 0

        # determine income eligibility for ACA PTC
        p = parameters(period).gov.aca
        magi_frac = person.tax_unit("aca_magi_fraction", period)
        is_income_eligible = p.ptc_income_eligibility.calc(magi_frac)

        # determine which people pay an age-based ACA plan premium
        is_aca_adult = person("age", period) > p.slcsp.max_child_age
        child_pays = person("aca_child_index", period) <= p.max_child_count
        pays_aca_premium = is_aca_adult | child_pays

        return (
            is_status_eligible
            & is_coverage_eligible
            & is_income_eligible
            & pays_aca_premium
        )
