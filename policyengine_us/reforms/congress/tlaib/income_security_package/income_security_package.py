from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_income_security_package() -> Reform:
    class baby_bonus_act_payment(Variable):
        value_type = float
        entity = Person
        definition_period = YEAR
        label = "Baby Bonus Act payment"
        unit = USD
        documentation = (
            "One-time payment for newborns under the Baby Bonus Act"
        )
        reference = "placeholder - bill not yet introduced"

        def formula(person, period, parameters):
            p = parameters(
                period
            ).gov.contrib.congress.tlaib.income_security_package.baby_bonus_act

            # Baby bonus is for those born in 2026 and after, paid in their birth year
            birth_year = person("birth_year", period)

            age = person("age", period)

            # Payment only in the birth year for those born 2026+
            is_eligible = (birth_year >= p.min_birth_year) & (
                age < p.age_limit
            )

            return is_eligible * p.amount

    class boost_act_payment(Variable):
        value_type = float
        entity = Person
        definition_period = YEAR
        label = "BOOST Act payment"
        unit = USD
        documentation = (
            "Monthly payments under the BOOST Act for eligible adults"
        )
        reference = "placeholder - bill not yet introduced"

        def formula(person, period, parameters):
            p = parameters(
                period
            ).gov.contrib.congress.tlaib.income_security_package.boost_act

            age = person("age", period)
            is_eligible = (age >= p.min_age) & (age <= p.max_age)

            annual_amount = p.amount * MONTHS_IN_YEAR

            return is_eligible * annual_amount

    class boost_act_tax(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        label = "BOOST Act supplemental tax"
        unit = USD
        documentation = "Supplemental tax on AGI to fund the BOOST Act"
        reference = "placeholder - bill not yet introduced"

        def formula(tax_unit, period, parameters):
            p = parameters(
                period
            ).gov.contrib.congress.tlaib.income_security_package.boost_act

            agi = tax_unit("adjusted_gross_income", period)
            filing_status = tax_unit("filing_status", period)

            excess_agi = max_(agi - p.tax.threshold[filing_status], 0)

            return excess_agi * p.tax.rate

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
            ).gov.contrib.congress.tlaib.income_security_package.end_child_poverty_act

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
            ).gov.contrib.congress.tlaib.income_security_package.end_child_poverty_act

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
            ).gov.contrib.congress.tlaib.income_security_package.end_child_poverty_act

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
            p = parameters(
                period
            ).gov.contrib.congress.tlaib.income_security_package

            BENEFITS = [
                "social_security",
                "ssi",
                "snap",
                "wic",
                "free_school_meals",
                "reduced_price_school_meals",
                "spm_unit_broadband_subsidy",
                "tanf",
                "high_efficiency_electric_home_rebate",
                "residential_efficiency_electrification_rebate",
                "unemployment_compensation",
                # Contributed.
                "basic_income",
                "spm_unit_capped_housing_subsidy",
                "household_state_benefits",
            ]

            # Add Income Security Package benefits if active
            if p.baby_bonus_act.in_effect:
                BENEFITS.append("baby_bonus_act_payment")
            if p.boost_act.in_effect:
                BENEFITS.append("boost_act_payment")
            if p.end_child_poverty_act.in_effect:
                BENEFITS.append("ecpa_child_benefit")

            return add(household, period, BENEFITS)

    class spm_unit_benefits(Variable):
        value_type = float
        entity = SPMUnit
        label = "Benefits"
        definition_period = YEAR
        unit = USD

        def formula(spm_unit, period, parameters):
            p = parameters(
                period
            ).gov.contrib.congress.tlaib.income_security_package

            BENEFITS = [
                "social_security",
                "ssi",
                "ma_state_supplement",  # Massachusetts benefits
                # California programs.
                "ca_cvrp",  # California Clean Vehicle Rebate Project.
                # Colorado programs.
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
                # Contributed.
                "basic_income",
                "ny_drive_clean_rebate",
            ]

            # Add Income Security Package benefits if active
            if p.baby_bonus_act.in_effect:
                BENEFITS.append("baby_bonus_act_payment")
            if p.boost_act.in_effect:
                BENEFITS.append("boost_act_payment")
            if p.end_child_poverty_act.in_effect:
                BENEFITS.append("ecpa_child_benefit")

            if parameters(period).gov.contrib.ubi_center.flat_tax.deduct_ptc:
                BENEFITS.append("aca_ptc")
            if not parameters(period).gov.hud.abolition:
                BENEFITS.append("spm_unit_capped_housing_subsidy")

            return add(spm_unit, period, BENEFITS)

    class income_tax(Variable):
        value_type = float
        entity = TaxUnit
        label = "federal income tax"
        unit = USD
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            p = parameters(
                period
            ).gov.contrib.congress.tlaib.income_security_package

            # Start with income tax after non-refundable credits
            base_tax = tax_unit("income_tax_before_refundable_credits", period)

            # Subtract refundable credits
            refundable_credits = tax_unit(
                "income_tax_refundable_credits", period
            )

            reduced_tax = base_tax - refundable_credits

            # Add BOOST tax only if active
            if p.boost_act.in_effect:
                boost_tax = tax_unit("boost_act_tax", period)
                return reduced_tax + boost_tax
            else:
                return reduced_tax

    class income_tax_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        label = "federal refundable income tax credits"
        unit = USD

        def formula(tax_unit, period, parameters):
            p = parameters(
                period
            ).gov.contrib.congress.tlaib.income_security_package.end_child_poverty_act

            # Get standard refundable credits, excluding EITC and refundable CTC if ECPA is active
            standard_credits = parameters(period).gov.irs.credits.refundable

            if p.in_effect:
                # ECPA replaces EITC and refundable CTC
                CREDITS = [
                    c
                    for c in standard_credits
                    if c not in ["eitc", "refundable_ctc"]
                ]
            else:
                # Use all standard credits
                CREDITS = list(standard_credits)

            base_credits = add(tax_unit, period, CREDITS) if CREDITS else 0

            # Add ECPA credits only if active
            if p.in_effect:
                ecpa_filer = tax_unit("ecpa_filer_credit", period)
                ecpa_adult_dep = add(
                    tax_unit, period, ["ecpa_adult_dependent_credit"]
                )
                return base_credits + ecpa_filer + ecpa_adult_dep
            else:
                return base_credits

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

            # Check if ECPA is active
            ecpa_params = parameters(
                period
            ).gov.contrib.congress.tlaib.income_security_package.end_child_poverty_act
            ecpa_active = ecpa_params.in_effect

            # If ECPA is active, remove non_refundable_ctc from the list
            if ecpa_active:
                CREDITS = [
                    c for c in base_credits if c != "non_refundable_ctc"
                ]
            else:
                CREDITS = base_credits

            return add(tax_unit, period, CREDITS)

    class reform(Reform):
        def apply(self):
            # Update all variables for the Income Security Package
            self.update_variable(baby_bonus_act_payment)
            self.update_variable(boost_act_payment)
            self.update_variable(boost_act_tax)
            self.update_variable(ecpa_child_benefit)
            self.update_variable(ecpa_adult_dependent_credit)
            self.update_variable(ecpa_filer_credit)
            self.update_variable(household_benefits)
            self.update_variable(spm_unit_benefits)
            self.update_variable(income_tax)
            self.update_variable(income_tax_refundable_credits)
            self.update_variable(income_tax_non_refundable_credits)

    return reform


def create_income_security_package_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_income_security_package()

    p = parameters.gov.contrib.congress.tlaib.income_security_package

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if (
            p(current_period).baby_bonus_act.in_effect
            or p(current_period).boost_act.in_effect
            or p(current_period).end_child_poverty_act.in_effect
        ):
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_income_security_package()
    else:
        return None


income_security_package = create_income_security_package_reform(
    None, None, bypass=True
)
