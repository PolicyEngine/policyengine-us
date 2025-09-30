from policyengine_us.model_api import *


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

            # Payment only in the birth year for those born 2026+
            is_eligible = birth_year >= p.min_birth_year

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

            return is_eligible * p.child_benefit.amount

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

            is_head = person("is_tax_unit_head", period)
            is_spouse = person("is_tax_unit_spouse", period)
            is_head_or_spouse = is_head | is_spouse

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
                "baby_bonus_act_payment",
                "boost_act_payment",
                "ecpa_child_benefit",
            ]

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
                "baby_bonus_act_payment",
                "boost_act_payment",
                "ecpa_child_benefit",
            ]

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

            # Add BOOST tax
            reduced_tax = base_tax - refundable_credits
            boost_tax = tax_unit("boost_act_tax", period)
            return reduced_tax + boost_tax

    class income_tax_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        label = "federal refundable income tax credits"
        unit = USD

        def formula(tax_unit, period, parameters):
            # Get standard refundable credits, excluding EITC and refundable CTC (replaced by ECPA)
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
            # Exclude non_refundable_ctc as it's replaced by ECPA
            CREDITS = [
                "foreign_tax_credit",
                "retirement_savings_credit",
                "residential_clean_energy_credit",
                "american_opportunity_credit_non_refundable",
                "lifetime_learning_credit_non_refundable",
                "other_dependent_credit",
                "cdcc",
                "electric_vehicle_credit",
                "district_of_columbia_non_refundable_credits",
                "education_credit_phase_out",
            ]

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
    # Always return the reform - individual provisions will be 0 if parameters don't allow them
    return create_income_security_package()


income_security_package = create_income_security_package_reform(
    None, None, bypass=True
)
