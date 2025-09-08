from policyengine_us.model_api import *


def create_end_child_poverty_act() -> Reform:
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

    class household_benefits(Variable):
        value_type = float
        entity = Household
        label = "benefits"
        unit = USD
        definition_period = YEAR
        adds = [
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
            "ecpa_child_benefit",
        ]

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
                "ecpa_child_benefit",
            ]
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
            self.update_variable(ecpa_adult_dependent_credit)
            self.update_variable(ecpa_filer_credit)
            self.update_variable(income_tax_refundable_credits)
            self.update_variable(ecpa_child_benefit)
            self.update_variable(household_benefits)
            self.update_variable(spm_unit_benefits)
            # Don't neutralize EITC and CTC - they're excluded from federal credits
            # but remain available for state conformity calculations

    return reform


def create_end_child_poverty_act_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_end_child_poverty_act()

    p = parameters(
        period
    ).gov.contrib.congress.tlaib.income_security_package.end_child_poverty_act

    if p.in_effect:
        return create_end_child_poverty_act()
    else:
        return None


end_child_poverty_act = create_end_child_poverty_act_reform(
    None, None, bypass=True
)
