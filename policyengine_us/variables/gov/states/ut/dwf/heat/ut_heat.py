from policyengine_us.model_api import *


class ut_heat(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Utah Home Energy Assistance Target regular heating benefit"
    defined_for = "ut_heat_eligible"
    reference = (
        "https://jobs.utah.gov/infosource/heatpolicy/Policy/600_Payment_Calculation/602_Percent_of_Poverty.htm",
        "https://jobs.utah.gov/infosource/heatpolicy/Policy/600_Payment_Calculation/603_Energy_Burden.htm",
        "https://jobs.utah.gov/infosource/heatpolicy/Policy/Obsolete_Policy/Obsolete_600/Obsolete_604_(3_1_25_to_9_30_26)_Target_Groups.htm",
        "https://jobs.utah.gov/infosource/heatpolicy/Policy/600_Payment_Calculation/605_Propane_or_Fuel_Oil.htm",
        # PDF pages 8-9.
        "https://liheapch.acf.gov/docs/2026/state-plans/UT_Plan_2026.pdf#page=8",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ut.dwf.heat.benefit
        annual_income = spm_unit("ut_heat_countable_income", period)
        income = annual_income.astype(float) / MONTHS_IN_YEAR
        poverty = np.ceil(
            spm_unit("ut_heat_fpg", period).astype(float) / MONTHS_IN_YEAR
        )
        lower_poverty_percentage = np.floor(
            np.divide(
                income / p.rounding_increment,
                poverty,
                out=np.zeros_like(income),
                where=poverty > 0,
            )
        )
        # Compare integer percentage boundaries at stored annual-income precision.
        poverty_boundary = (
            lower_poverty_percentage * poverty * p.rounding_increment * MONTHS_IN_YEAR
        ).astype(annual_income.dtype)
        # Sections 602/603 require numeric rounding, not merely the stale
        # XLSX's zero-decimal display. Percentage-point size is the policy's
        # rounding increment; 0.5 implements nearest-whole, ties upward.
        income_points = (
            p.income_component
            - lower_poverty_percentage
            - (annual_income > poverty_boundary)
        )
        standard = spm_unit("ut_heat_energy_cost_standard", period) / MONTHS_IN_YEAR
        burden_percentage = np.divide(
            standard / p.rounding_increment,
            income,
            out=np.zeros_like(income),
            where=income > 0,
        )
        burden_points = np.floor(burden_percentage + 0.5)
        capped_burden = min_(burden_points, p.maximum_burden / p.rounding_increment)
        burden_component = where(
            income > 0,
            capped_burden * p.burden_point_amount,
            p.maximum_burden / p.rounding_increment * p.burden_point_amount,
        )
        person = spm_unit.members
        age = person("age", period)
        target_member = person("ut_heat_eligible_person", period) & (
            (age < p.target.child_age)
            | (age >= p.target.elderly_age)
            | person("is_disabled", period)
        )
        target_credit = spm_unit.any(target_member) * p.target.amount
        fuel = spm_unit("heating_type", period)
        fuel_credit = np.isin(fuel.decode_to_str(), p.fuel_credit_types) * p.fuel_credit
        # Kerosene shares propane's cost standard, but section 605 names only
        # propane and fuel oil for this addition. No actual-expense cap applies.
        # Funding-dependent extra supplements and equipment/crisis are excluded.
        amount = income_points + burden_component + target_credit + fuel_credit
        return clip(amount, p.minimum, p.maximum)
