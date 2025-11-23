from policyengine_us.model_api import *


def create_ecpa_only() -> Reform:
    class ecpa_child_benefit(Variable):
        value_type = float
        entity = Person
        definition_period = YEAR
        label = "End Child Poverty Act child benefit"
        unit = USD
        documentation = (
            "Universal child benefit under the End Child Poverty Act"
        )
        reference = "placeholder - bill not yet introduced"

        def formula(person, period, parameters):
            p = parameters(
                period
            ).gov.contrib.congress.tlaib.economic_dignity_for_all_agenda.end_child_poverty_act

            age = person("age", period)
            is_eligible = age < p.child_benefit.age_limit

            # Use FPG additional_person amount (CONTIGUOUS_US for all states), rounded to nearest $10
            p_fpg = parameters(period).gov.hhs.fpg
            fpg_amount = p_fpg.additional_person.CONTIGUOUS_US
            amount = round(fpg_amount / 10) * 10

            return is_eligible * amount

    class ecpa_adult_dependent_credit(Variable):
        value_type = float
        entity = Person
        definition_period = YEAR
        label = "End Child Poverty Act adult dependent credit"
        unit = USD
        documentation = (
            "Credit for adult dependents under the End Child Poverty Act"
        )
        reference = "placeholder - bill not yet introduced"

        def formula(person, period, parameters):
            p = parameters(
                period
            ).gov.contrib.congress.tlaib.economic_dignity_for_all_agenda.end_child_poverty_act

            age = person("age", period)
            is_dependent = person("is_tax_unit_dependent", period)

            is_eligible = (
                age >= p.adult_dependent_credit.min_age
            ) & is_dependent

            return is_eligible * p.adult_dependent_credit.amount

    class ecpa_filer_credit(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        label = "End Child Poverty Act filer credit"
        unit = USD
        documentation = "Filer credit under the End Child Poverty Act for eligible tax filers"
        reference = "placeholder - bill not yet introduced"

        def formula(tax_unit, period, parameters):
            p = parameters(
                period
            ).gov.contrib.congress.tlaib.economic_dignity_for_all_agenda.end_child_poverty_act

            person = tax_unit.members
            age = person("age", period)

            is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)

            is_eligible_age = (age >= p.filer_credit.eligibility.min_age) & (
                age < p.filer_credit.eligibility.max_age
            )
            is_eligible_filer = is_head_or_spouse & is_eligible_age

            has_eligible_filer = tax_unit.any(is_eligible_filer)

            filing_status = tax_unit("filing_status", period)
            amount = p.filer_credit.amount[filing_status]

            agi = tax_unit("adjusted_gross_income", period)
            excess_agi = max_(
                agi - p.filer_credit.phase_out.start[filing_status], 0
            )
            phase_out = excess_agi * p.filer_credit.phase_out.rate

            phased_out_amount = max_(amount - phase_out, 0)

            return has_eligible_filer * phased_out_amount

    class household_benefits(Variable):
        value_type = float
        entity = Household
        label = "benefits"
        unit = USD
        definition_period = YEAR

        def formula(household, period, parameters):
            # Start with baseline benefits from parameters
            BENEFITS = list(
                parameters(period).gov.household.household_benefits
            )

            # Add ECPA child benefit
            BENEFITS.append("ecpa_child_benefit")

            return add(household, period, BENEFITS)

    class spm_unit_benefits(Variable):
        value_type = float
        entity = SPMUnit
        label = "Benefits"
        definition_period = YEAR
        unit = USD

        def formula(spm_unit, period, parameters):
            BENEFITS = [
                "social_security",
                "ssi",
                "ma_state_supplement",
                "ca_cvrp",
                "co_ccap_subsidy",
                "co_state_supplement",
                "co_oap",
                "snap",
                "wic",
                "free_school_meals",
                "reduced_price_school_meals",
                "spm_unit_broadband_subsidy",
                "spm_unit_energy_subsidy",
                "tanf",
                "high_efficiency_electric_home_rebate",
                "residential_efficiency_electrification_rebate",
                "unemployment_compensation",
                "ak_energy_relief",
                "basic_income",
                "ny_drive_clean_rebate",
            ]

            # Add ECPA child benefit
            BENEFITS.append("ecpa_child_benefit")

            if parameters(period).gov.contrib.ubi_center.flat_tax.deduct_ptc:
                BENEFITS.append("aca_ptc")
            if not parameters(period).gov.hud.abolition:
                BENEFITS.append("spm_unit_capped_housing_subsidy")

            return add(spm_unit, period, BENEFITS)

    class income_tax_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        label = "federal refundable income tax credits"
        unit = USD

        def formula(tax_unit, period, parameters):
            # Get standard refundable credits, excluding EITC and refundable CTC (ECPA replaces them)
            standard_credits = parameters(period).gov.irs.credits.refundable

            CREDITS = [
                c
                for c in standard_credits
                if c not in ["eitc", "refundable_ctc"]
            ]

            base_credits = add(tax_unit, period, CREDITS) if CREDITS else 0

            # Add ECPA credits
            ecpa_filer = tax_unit("ecpa_filer_credit", period)
            ecpa_adult_dep = add(
                tax_unit, period, ["ecpa_adult_dependent_credit"]
            )
            return base_credits + ecpa_filer + ecpa_adult_dep

    class income_tax_non_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        label = "federal non-refundable income tax credits"
        unit = USD

        def formula(tax_unit, period, parameters):
            # Get the base list of non-refundable credits from parameters
            p = parameters(period).gov.irs.credits
            base_credits = list(p.non_refundable)

            # ECPA removes non_refundable_ctc from the list
            CREDITS = [c for c in base_credits if c != "non_refundable_ctc"]

            return add(tax_unit, period, CREDITS)

    class reform(Reform):
        def apply(self):
            # Update only ECPA variables
            self.update_variable(ecpa_child_benefit)
            self.update_variable(ecpa_adult_dependent_credit)
            self.update_variable(ecpa_filer_credit)
            self.update_variable(household_benefits)
            self.update_variable(spm_unit_benefits)
            self.update_variable(income_tax_refundable_credits)
            self.update_variable(income_tax_non_refundable_credits)

    return reform


end_child_poverty_act = create_ecpa_only()


def create_end_child_poverty_act_reform(
    parameters, period, bypass: bool = False
):
    """Auto-application function for structural reforms."""
    if bypass:
        return create_ecpa_only()

    from policyengine_core.periods import period as period_

    p = parameters.gov.contrib.congress.tlaib.economic_dignity_for_all_agenda

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).end_child_poverty_act.in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ecpa_only()
    else:
        return None
