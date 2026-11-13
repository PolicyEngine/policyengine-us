from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class fl_medicaid_parent_income_limit(Variable):
    value_type = float
    entity = Person
    label = "Florida Medicaid parent income limit"
    unit = "/1"
    definition_period = YEAR
    defined_for = StateCode.FL
    reference = (
        "https://ffic.myflfamilies.com/manual/essfiles/30446.pdf",
        "https://ffic.myflfamilies.com/manual/2600.pdf#page=37",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.fl.dcf.medicaid.parent.income_limit
        size = person("medicaid_household_size", period)
        capped_size = min_(size, p.max_household_size).astype(int)
        additional_people = max_(size - p.max_household_size, 0)
        monthly_standard = (
            p.amount[capped_size] + additional_people * p.additional_person
        )
        state_group = person.household("state_group_str", period)
        monthly_fpg = fpg(size, state_group, period, parameters) / MONTHS_IN_YEAR
        # A-7 defines MNIL as the adult standard plus the standard disregard.
        # Its separate MAGI disregard applies once for full Medicaid coverage.
        # Annual calculations retain the model's current-year FPG convention;
        # Florida's April FPG adoption is not reproduced within the year.
        monthly_limit = np.ceil(
            np.round(monthly_standard + p.fpl_disregard * monthly_fpg, 2)
        )
        return monthly_limit / monthly_fpg
