from policyengine_us.model_api import *


class nc_lieap_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "North Carolina LIEAP countable household income"
    defined_for = StateCode.NC
    reference = (
        # Section 300.09 income and deductions (pages 10-13) and Section 300.10
        # households with an ineligible alien (pages 15-17).
        "https://policies.ncdhhs.gov/wp-content/uploads/EP-300-5.1.2026.pdf#page=10",
    )

    def formula(spm_unit, period, parameters):
        # The FY2026 state plan (item 1.8, page 5) reports gross income, while
        # Section 300.09 B (pages 11-13) nets out the deductions below. The model
        # follows the manual.
        p = parameters(period).gov.states.nc.ncdhhs.lieap
        person = spm_unit.members
        included = person("is_citizen_or_legal_immigrant", period)
        size = spm_unit("nc_lieap_household_size", period)
        fraction = size / max_(spm_unit("spm_unit_size", period), 1)
        share = where(included, 1, spm_unit.project(fraction))
        earned = person("nc_lieap_earned_income", period) * share
        monthly = earned / MONTHS_IN_YEAR
        table_deduction = where(
            monthly > p.earned_income_deduction_threshold,
            monthly * p.earned_income_deduction_rate,
            p.earned_income_deduction.calc(monthly, right=True),
        )
        # The lowest band's standard deduction can exceed very small monthly
        # earnings. Cap the deduction at the earnings so that it cannot offset
        # unearned income.
        work_deduction = min_(table_deduction, monthly) * MONTHS_IN_YEAR
        specified = (person("age", period) >= p.elderly_age) | person(
            "is_usda_disabled", period
        )
        medical = specified * included * p.medical_deduction * MONTHS_IN_YEAR
        support = max_(person("child_support_expense", period), 0) * share
        care = max_(person("care_expenses", period), 0) * share
        person_income = person("nc_lieap_gross_income_person", period) * share
        # Work First Family Assistance is unearned income in the FNS 300.02 chart
        # (page 26) and is checked in the plan's item 1.9 list.
        tanf = spm_unit("tanf", period)
        # Childcare expenses already exclude modeled subsidies. The payer and
        # additional transport costs cannot be identified, so childcare paid by an
        # excluded member is not prorated. Adult care uses its reported person.
        # Section 300.09 B.1.b (page 11) verifies childcare costs for each member
        # with earned income, while B.1.a allows out-of-pocket childcare without
        # that condition. The care deductions are not tied to earnings here.
        childcare = max_(spm_unit("childcare_expenses", period), 0)
        # Annual income approximates the prior application month; terminated-income
        # exceptions and room/board transfers within the unit are not modeled.
        return max_(
            spm_unit.sum(person_income - work_deduction - medical - support - care)
            + tanf
            - childcare,
            0,
        )
