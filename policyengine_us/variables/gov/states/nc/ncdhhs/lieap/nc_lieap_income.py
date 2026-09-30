from policyengine_us.model_api import *


class nc_lieap_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "North Carolina LIEAP countable household income"
    defined_for = StateCode.NC
    reference = "https://policies.ncdhhs.gov/wp-content/uploads/EP-300-5.1.2026.pdf#page=10,11,12,13,15,16,17"

    def formula_2026(spm_unit, period, parameters):
        p = parameters(period).gov.states.nc.ncdhhs.lieap
        person = spm_unit.members
        included = person("is_citizen_or_legal_immigrant", period)
        size = spm_unit("nc_lieap_household_size", period)
        fraction = size / max_(spm_unit("spm_unit_size", period), 1)
        share = where(included, 1, spm_unit.project(fraction))
        earned = person("nc_lieap_earned_income", period) * share
        monthly = earned / MONTHS_IN_YEAR
        work_deduction = (
            where(
                monthly > p.earned_income_deduction_threshold,
                monthly * p.earned_income_deduction_rate,
                p.earned_income_deduction.calc(monthly, right=True),
            )
            * MONTHS_IN_YEAR
        )
        specified = (person("age", period) >= p.elderly_age) | person(
            "is_usda_disabled", period
        )
        medical = specified * included * p.medical_deduction * MONTHS_IN_YEAR
        support = max_(person("child_support_expense", period), 0) * share
        care = max_(person("care_expenses", period), 0) * share
        person_income = person("nc_lieap_gross_income_person", period) * share
        unit_sources = parameters(period).gov.usda.snap.income.sources.unearned_spm_unit
        unit_income = add(spm_unit, period, unit_sources)
        # Childcare expenses already exclude modeled subsidies. The payer and
        # additional transport costs cannot be identified, so childcare paid by an
        # excluded member is not prorated. Adult care uses its reported person.
        childcare = max_(spm_unit("childcare_expenses", period), 0)
        # Annual income approximates the prior application month; terminated-income
        # exceptions and room/board transfers within the unit are not modeled.
        return max_(
            spm_unit.sum(person_income - work_deduction - medical - support - care)
            + unit_income
            - childcare,
            0,
        )
