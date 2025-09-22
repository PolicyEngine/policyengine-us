from policyengine_us.model_api import *


def create_income_security_package() -> Reform:
    class baby_bonus(Variable):
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

            if not p.in_effect:
                return 0

            age = person("age", period)
            is_eligible_child = age < p.max_child_age

            return is_eligible_child * p.amount

    class boost_payment(Variable):
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

            if not p.in_effect:
                return 0

            age = person("age", period)
            is_eligible = (age >= p.min_age) & (age <= p.max_age)

            annual_amount = p.amount * MONTHS_IN_YEAR

            return is_eligible * annual_amount

    class boost_tax(Variable):
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

            if not p.in_effect:
                return 0

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

            if not p.in_effect:
                return 0

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

            if not p.in_effect:
                return 0

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

            if not p.in_effect:
                return 0

            person = tax_unit.members
            age = person("age", period)

            is_head = person("is_tax_unit_head", period)
            is_spouse = person("is_tax_unit_spouse", period)
            is_filer = is_head | is_spouse

            is_eligible_age = (age >= p.filer_credit.eligibility.min_age) & (
                age < p.filer_credit.eligibility.max_age
            )
            is_eligible_filer = is_filer & is_eligible_age

            has_eligible_filer = tax_unit.any(is_eligible_filer)

            filing_status = tax_unit("filing_status", period)
            amount = p.filer_credit.amount[filing_status]

            agi = tax_unit("adjusted_gross_income", period)
            excess_agi = max_(
                agi - p.filer_credit.phase_out.start[filing_status], 0
            )
            phase_out = excess_agi * p.filer_credit.phase_out.rate

            credit = max_(amount - phase_out, 0)

            return has_eligible_filer * credit

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

            # Base benefits list
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

            # Add benefits based on what's in effect
            if p.baby_bonus_act.in_effect:
                BENEFITS.append("baby_bonus")
            if p.boost_act.in_effect:
                BENEFITS.append("boost_payment")
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

            # Add benefits based on what's in effect
            if p.baby_bonus_act.in_effect:
                BENEFITS.append("baby_bonus")
            if p.boost_act.in_effect:
                BENEFITS.append("boost_payment")
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

            COMPONENTS = [
                "income_tax_before_refundable_credits",
                "income_tax_refundable_credits",
                "income_tax_non_refundable_credits",
            ]

            # Only add boost_tax if BOOST Act is in effect
            if p.boost_act.in_effect:
                COMPONENTS.append("boost_tax")

            return add(tax_unit, period, COMPONENTS)

    class income_tax_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        label = "federal refundable income tax credits"
        unit = USD

        def formula(tax_unit, period, parameters):
            p = parameters(
                period
            ).gov.contrib.congress.tlaib.income_security_package

            CREDITS = [
                "american_opportunity_credit_refundable",
                "premium_tax_credit",
                "lifetime_learning_credit_refundable",
                "cdcc_refundable",
                "recovery_rebate_credit",
                "qualified_sick_leave_self_employed_credit",
                "qualified_family_leave_equivalent_credit",
                "local_income_tax_refundable_credits",
            ]

            # Add EITC and refundable CTC only if ECPA is NOT in effect
            if not p.end_child_poverty_act.in_effect:
                CREDITS.extend(["eitc", "refundable_ctc"])

            # Add ECPA credits if in effect
            if p.end_child_poverty_act.in_effect:
                CREDITS.append("ecpa_filer_credit")

            return add(tax_unit, period, CREDITS)

    class income_tax_non_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        label = "federal non-refundable income tax credits"
        unit = USD

        def formula(tax_unit, period, parameters):
            p = parameters(
                period
            ).gov.contrib.congress.tlaib.income_security_package

            CREDITS = [
                "foreign_tax_credit",
                "retirement_savings_credit",
                "residential_clean_energy_credit",
                "american_opportunity_credit_non_refundable",
                "lifetime_learning_credit_non_refundable",
                "non_refundable_ctc",
                "other_dependent_credit",
                "cdcc",
                "electric_vehicle_credit",
                "district_of_columbia_non_refundable_credits",
                "education_credit_phase_out",
            ]

            # Remove non_refundable_ctc if ECPA is in effect
            if p.end_child_poverty_act.in_effect:
                CREDITS.remove("non_refundable_ctc")

            return add(tax_unit, period, CREDITS)

    class reform(Reform):
        def apply(self):
            # Variables are always updated, but their formulas check in_effect
            self.update_variable(baby_bonus)
            self.update_variable(boost_payment)
            self.update_variable(boost_tax)
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

    if parameters is None or period is None:
        return None

    # Check if any of the three acts are in effect
    p = parameters(period).gov.contrib.congress.tlaib.income_security_package

    baby_bonus_in_effect = p.baby_bonus_act.in_effect
    boost_in_effect = p.boost_act.in_effect
    ecpa_in_effect = p.end_child_poverty_act.in_effect

    if baby_bonus_in_effect or boost_in_effect or ecpa_in_effect:
        return create_income_security_package()
    else:
        return None


income_security_package = create_income_security_package_reform(
    None, None, bypass=True
)
