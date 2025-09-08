from policyengine_us.model_api import *


def create_boost_act() -> Reform:
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
            "boost_payment",
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
                "boost_payment",
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
        adds = [
            "income_tax_before_refundable_credits",
            "income_tax_refundable_credits",
            "income_tax_non_refundable_credits",
            "boost_tax",
        ]

    class reform(Reform):
        def apply(self):
            self.update_variable(boost_payment)
            self.update_variable(boost_tax)
            self.update_variable(household_benefits)
            self.update_variable(spm_unit_benefits)
            self.update_variable(income_tax)

    return reform


def create_boost_act_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_boost_act()

    p = parameters(
        period
    ).gov.contrib.congress.tlaib.income_security_package.boost_act

    if p.in_effect:
        return create_boost_act()
    else:
        return None


boost_act = create_boost_act_reform(None, None, bypass=True)
