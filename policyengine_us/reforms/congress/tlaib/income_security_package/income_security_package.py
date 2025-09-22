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

            age = person("age", period)
            max_age = p.max_child_age
            is_eligible_child = age < max_age

            amount = p.amount

            return is_eligible_child * amount

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

            age = person("age", period)
            min_age = p.min_age
            max_age = p.max_age

            is_eligible = (age >= min_age) & (age <= max_age)

            monthly_amount = p.amount
            annual_amount = monthly_amount * MONTHS_IN_YEAR

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

            agi = tax_unit("adjusted_gross_income", period)
            filing_status = tax_unit("filing_status", period)

            threshold = p.tax.threshold[filing_status]
            rate = p.tax.rate

            excess_agi = max_(agi - threshold, 0)

            return excess_agi * rate

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
            age_limit = p.child_benefit.age_limit
            is_eligible = age < age_limit

            annual_amount = p.child_benefit.amount

            return is_eligible * annual_amount

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
            min_age = p.adult_dependent_credit.min_age
            is_dependent = person("is_tax_unit_dependent", period)

            is_eligible = (age >= min_age) & is_dependent

            amount = p.adult_dependent_credit.amount

            return is_eligible * amount

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
            min_age = p.filer_credit.eligibility.min_age
            max_age = p.filer_credit.eligibility.max_age

            is_head = person("is_tax_unit_head", period)
            is_spouse = person("is_tax_unit_spouse", period)
            is_filer = is_head | is_spouse

            is_eligible_age = (age >= min_age) & (age < max_age)
            is_eligible_filer = is_filer & is_eligible_age

            has_eligible_filer = tax_unit.any(is_eligible_filer)

            filing_status = tax_unit("filing_status", period)
            amount = p.filer_credit.amount[filing_status]

            agi = tax_unit("adjusted_gross_income", period)
            phase_out_start = p.filer_credit.phase_out.start[filing_status]
            phase_out_rate = p.filer_credit.phase_out.rate

            excess_agi = max_(agi - phase_out_start, 0)
            phase_out = excess_agi * phase_out_rate

            credit = max_(amount - phase_out, 0)

            return has_eligible_filer * credit

    class household_benefits(Variable):
        value_type = float
        entity = Household
        label = "benefits"
        unit = USD
        definition_period = YEAR

        def formula(household, period, parameters):
            existing = household(
                "household_benefits", period, baseline_variables_only=True
            )
            baby_bonus_amount = add(household, period, ["baby_bonus"])
            boost_payment_amount = add(household, period, ["boost_payment"])
            ecpa_child_benefit_amount = add(
                household, period, ["ecpa_child_benefit"]
            )

            return (
                existing
                + baby_bonus_amount
                + boost_payment_amount
                + ecpa_child_benefit_amount
            )

    class spm_unit_benefits(Variable):
        value_type = float
        entity = SPMUnit
        label = "Benefits"
        definition_period = YEAR
        unit = USD

        def formula(spm_unit, period, parameters):
            existing = spm_unit(
                "spm_unit_benefits", period, baseline_variables_only=True
            )
            baby_bonus_amount = add(spm_unit, period, ["baby_bonus"])
            boost_payment_amount = add(spm_unit, period, ["boost_payment"])
            ecpa_child_benefit_amount = add(
                spm_unit, period, ["ecpa_child_benefit"]
            )

            return (
                existing
                + baby_bonus_amount
                + boost_payment_amount
                + ecpa_child_benefit_amount
            )

    class income_tax(Variable):
        value_type = float
        entity = TaxUnit
        label = "federal income tax"
        unit = USD
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            existing = tax_unit(
                "income_tax", period, baseline_variables_only=True
            )
            boost_tax_amount = tax_unit("boost_tax", period)
            return existing + boost_tax_amount

    class income_tax_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        label = "federal refundable income tax credits"
        unit = USD

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.irs.credits
            # Get list of refundable credits, but exclude EITC and CTC
            refundable_credits = [
                credit
                for credit in p.refundable
                if credit not in ["eitc", "refundable_ctc"]
            ]
            other_credits = add(tax_unit, period, refundable_credits)
            filer_credit = tax_unit("ecpa_filer_credit", period)
            # Sum person-level adult dependent credits
            person = tax_unit.members
            adult_dependent_credit = tax_unit.sum(
                person("ecpa_adult_dependent_credit", period)
            )
            return filer_credit + adult_dependent_credit + other_credits

    class reform(Reform):
        def apply(self):
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

    return reform


def create_income_security_package_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_income_security_package()

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
