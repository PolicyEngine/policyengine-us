from openfisca_us.model_api import *

class snap_deductions(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP income deductions"
    unit = "currency-USD"
    documentation = "Deductions made from gross income for SNAP benefits"
    definition_period = YEAR
    reference = "United States Code, Title 7, Section 2014(e)"

    def formula(spm_unit, period, parameters):
        return sum([spm_unit(variable, period) for variable in [
            "snap_standard_deduction",
            "snap_earnings_deduction",
            "snap_dependent_care_deduction",
            "snap_child_support_deduction",
            "snap_medical_expense_deduction",
            "snap_shelter_deduction",
        ]])

class snap_earnings_deduction(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = "Earnings deduction for calculating SNAP benefit amount"
    label = "SNAP earnings deduction"
    unit = "currency-USD"
    reference = "United States Code, Title 7, Section 2014(e)(2)"

    def formula(spm_unit, period, parameters):
        deduction_rate = parameters(
            period
        ).usda.snap.earnings_deduction
        return spm_unit("snap_gross_income", period) * deduction_rate

class snap_dependent_care_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP dependent care deduction"
    unit = "currency-USD"
    documentation = "Deduction from SNAP gross income for dependent care"
    definition_period = YEAR
    reference = "United States Code, Title 7, Section 2014(e)(3)"

class snap_child_support_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP child support payment deduction"
    unit = "currency-USD"
    documentation = "Deduction from SNAP gross income for child support payments"
    definition_period = YEAR
    reference = "United States Code, Title 7, Section 2014(e)(4)"

class snap_medical_expense_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP excess medical expense deduction"
    unit = "currency-USD"
    documentation = "Deduction from SNAP gross income for excess medical expenses"
    definition_period = YEAR
    reference = "United States Code, Title 7, Section 2014(e)(5)"


class snap_shelter_deduction(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = "Excess shelter deduction for calculating SNAP benefit amount"
    label = "SNAP shelter deduction"

    def formula(spm_unit, period, parameters):
        # TODO: Multiply params by 12.
        # check for member of spm_unit with disability/elderly status
        shelter_deduction = parameters(period).usda.snap.shelter_deduction

        # Calculate uncapped shelter deduction as housing costs in excess of
        # income threshold
        uncapped_ded = max_(
            spm_unit("housing_cost", period)
            - (
                shelter_deduction.income_share_threshold
                * spm_unit("snap_net_income_pre_shelter", period)
            ),
            0,
        )

        # Index maximum shelter deduction by state group.
        state_group = spm_unit.household("state_group_str", period)
        ded_cap = shelter_deduction.amount[state_group]

        has_elderly_disabled = spm_unit("has_elderly_disabled", period)
        # Cap for all but elderly/disabled people.
        return where(
            has_elderly_disabled, uncapped_ded, min_(uncapped_ded, ded_cap)
        )

class snap_homeless_shelter_deduction(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Homeless shelter deduction"
    documentation = "Homeless shelter deduction"
    reference = "https://www.law.cornell.edu/cfr/text/7/273.9"

    def formula(spm_unit, period, parameters):

        is_homeless = spm_unit.household("is_homeless", period)
        return (
            is_homeless
            * parameters(period).usda.snap.homeless_shelter_deduction
        ) * 12
