from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class medicaid_income_level(Variable):
    value_type = float
    entity = Person
    label = "Medicaid/CHIP-related income level"
    unit = "/1"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/42/435.603",
        "https://www.medicaid.gov/state-resource-center/mac-learning-collaboratives/downloads/household-composition-and-income-training.pdf",
        # Missouri applies its MAGI limits as the Appendix A monthly-dollar
        # maximums, each FPL percentage converted to monthly dollars and
        # rounded up to the next whole dollar.
        "https://dssmanuals.mo.gov/family-mo-healthnet-magi/1805-000-00/1805-030-00/1805-030-20/1805-030-20-20/1805-030-20-20-05/",
        "https://dssmanuals.mo.gov/wp-content/uploads/2019/03/MAGIappendix-a.pdf#page=1",
    )

    def formula(person, period, parameters):
        income = person("medicaid_household_income", period)
        size = person("medicaid_household_size", period)
        state_group = person.household("state_group_str", period)
        state_code = person.household("state_code", period)
        # Missouri finds monthly income at or below the Appendix A dollar
        # maximum eligible, and that maximum is the exact FPL threshold rounded
        # up to the next whole dollar. Income m passes such a limit exactly
        # when the whole dollar just below m (ceil(m) - 1) is strictly under
        # the exact threshold, so Missouri's level is measured from that
        # dollar figure and the downstream FPL-ratio comparisons reproduce the
        # published dollar boundaries. When the exact threshold is itself a
        # whole dollar (no rounding), income $1 above it measures at exactly
        # the limit, which the "at or below" categories accept and the
        # strict-less-than categories also accept once the float32 level is
        # compared with the float64 parameter, so that single dollar of
        # income remains eligible; the whole-dollar case is rare (in 2026
        # only the size-4 and size-9 adult thresholds, $3,795 and $7,061).
        monthly_income = np.round(income / MONTHS_IN_YEAR, 2)
        mo_income = max_(np.ceil(monthly_income) - 1, 0) * MONTHS_IN_YEAR
        countable_income = where(state_code == StateCode.MO, mo_income, income)
        return countable_income / fpg(size, state_group, period, parameters)
