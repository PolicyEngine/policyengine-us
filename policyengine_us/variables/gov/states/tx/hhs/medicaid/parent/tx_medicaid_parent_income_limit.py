from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class tx_medicaid_parent_income_limit(Variable):
    value_type = float
    entity = Person
    label = "Texas Medicaid one-parent income limit"
    unit = "/1"
    definition_period = YEAR
    defined_for = StateCode.TX
    reference = (
        "https://fhb.hhs.texas.gov/handbooks/texas-works-handbook/c-130-medical-programs",
        "https://fhb.hhs.texas.gov/handbooks/texas-works-handbook/a-1340-income-limits",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.tx.hhs.medicaid.parent.income_limit
        size = person("medicaid_household_size", period)
        capped_size = min_(size, p.max_household_size).astype(int)
        additional_people = max_(size - p.max_household_size, 0)
        monthly_standard = (
            p.amount[capped_size] + additional_people * p.additional_person
        )
        state_group = person.household("state_group_str", period)
        annual_fpg = fpg(size, state_group, period, parameters)
        # C-131.2 publishes separate one-parent and two-parent columns. The
        # parent router applies this helper only to its verified one-adult,
        # one-identified-parent subset; other households retain their route.
        # Add the five-point disregard once. The shared financial helper keeps
        # its existing whole-dollar approximation, not Texas cent precision.
        # YEAR calculations retain current-year FPG rather than reproducing
        # Texas's within-year March adoption of the new guidelines.
        return monthly_standard * MONTHS_IN_YEAR / annual_fpg + p.fpl_disregard
