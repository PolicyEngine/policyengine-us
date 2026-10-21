from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class co_leap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Eligible for Colorado LEAP regular heating assistance"
    defined_for = StateCode.CO
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/8624#b_2_B",
        # PDF pages 5,8
        "https://liheapch.acf.gov/docs/2026/state-plans/CO_Plan_2026.pdf#page=5",
        # PDF pages 29,31,46,51-53,55
        "https://drive.google.com/file/d/1G3XKsXyKoPZmsA5-P6NI6w3svP99xOZd/view#page=29",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period)
        size = spm_unit("co_leap_household_size", period)
        income = spm_unit("co_leap_countable_income", period)
        limit = spm_unit("co_leap_income_limit", period)
        person = spm_unit.members
        qualified = person("is_citizen_or_legal_immigrant", period)
        foster = person("is_in_foster_care", period.first_month)
        # The ordinary state chart caps size at 15. Federal protection uses the
        # actual qualified sharing household before that administrative cap.
        actual_size = spm_unit.sum(qualified & ~foster)
        guideline = fpg(
            max_(actual_size, 1),
            spm_unit.household("state_group_str", period),
            period,
            parameters,
            year_lag=p.gov.states.co.cdhs.leap.payment.fpg_year_lag,
        )
        federal_floor = np.round(guideline * p.gov.hhs.liheap.fpg_floor, 2)
        cost = spm_unit("co_leap_heating_cost", period)
        included = spm_unit("heat_expense_included_in_rent", period)
        subsidized = spm_unit("receives_housing_assistance", period)
        fuel = spm_unit("heating_type", period)
        fuels = fuel.possible_values
        dwelling = spm_unit("co_leap_dwelling_type", period)
        hotel = dwelling == dwelling.possible_values.HOTEL_MOTEL
        # Subsidized rent-included heat can qualify with a separate surcharge;
        # that fact is unavailable, so this exception is not represented.
        # Hotels require heat included in rent. Their additional continuous
        # 30-day residence requirement cannot be identified by existing inputs.
        # Application timing, vendor approval and prior receipt are not modeled.
        return (
            (size > 0)
            & ((income <= limit) | (income < federal_floor))
            & (cost > 0)
            & (fuel != fuels.NONE)
            & (fuel != fuels.UNSPECIFIED)
            & ~(included & subsidized)
            & (~hotel | included)
        )
