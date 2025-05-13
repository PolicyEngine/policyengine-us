from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_aca_ptc_add_immigration_requirement() -> Reform:
    class aca_ptc(Variable):
        value_type = float
        entity = TaxUnit
        label = "ACA premium tax credit for tax unit"
        unit = USD
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/uscode/text/26/36B"
        defined_for = "is_aca_ptc_eligible"

        def formula(tax_unit, period, parameters):
            plan_cost = tax_unit("slcsp", period)
            income = tax_unit("aca_magi", period)
            applicable_figure = tax_unit("aca_ptc_phase_out_rate", period)
            return max_(0, plan_cost - income * applicable_figure)

    class is_aca_ptc_eligible(Variable):
        value_type = bool
        entity = Person
        label = "Person is eligible for ACA premium tax credit and pays ACA premium"
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

            # determine coverage eligibility for ACA PTC
            INELIGIBLE_COVERAGE = [
                "is_medicaid_eligible",
                "is_chip_eligible",
                "is_aca_eshi_eligible",
                "is_medicare_eligible",
            ]
            is_coverage_eligible = (
                add(person, period, INELIGIBLE_COVERAGE) == 0
            )

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

    class is_aca_ptc_immigration_status_eligible(Variable):
        value_type = bool
        entity = Person
        label = "Person is eligible for ACA premium tax credit and pays ACA premium due to immigration status"
        definition_period = YEAR

        def formula(person, period, parameters):
            p = parameters(period).gov.contrib.aca
            immigration_status = person("immigration_status", period)
            immigration_status_str = immigration_status.decode_to_str()
            ineligible_immigration_status = np.isin(
                immigration_status_str, p.ineligible_immigration_status
            )
            return ~ineligible_immigration_status

    class reform(Reform):
        def apply(self):
            self.update_variable(aca_ptc)
            self.update_variable(is_aca_ptc_eligible)
            self.update_variable(is_aca_ptc_immigration_status_eligible)

    return reform


def create_aca_ptc_add_immigration_requirement_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_aca_ptc_add_immigration_requirement()

    p = parameters.gov.contrib.aca

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_aca_ptc_add_immigration_requirement()
    else:
        return None


aca_ptc_add_immigration_requirement = (
    create_aca_ptc_add_immigration_requirement_reform(None, None, bypass=True)
)
