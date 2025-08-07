from policyengine_us.model_api import *


def create_boost_middle_class_tax_credit() -> Reform:
    class boost_middle_class_tax_credit(Variable):
        value_type = float
        entity = TaxUnit
        label = "BOOST Middle Class Tax Credit"
        unit = USD
        definition_period = YEAR
        reference = "https://d12t4t5x3vyizu.cloudfront.net/tlaib.house.indigov.us/uploads/2022/05/TLAIB_046_xml.pdf"

        def formula(tax_unit, period, parameters):
            p = parameters(
                period
            ).gov.contrib.harris.lift.middle_class_tax_credit
            filing_status = tax_unit("filing_status", period)
            joint = filing_status == filing_status.possible_values.JOINT
            amount = where(joint, p.cap * p.joint_multiplier, p.cap)
            agi = tax_unit("adjusted_gross_income", period)

            excess = max_(0, agi - p.phase_out.start[filing_status])
            phase_out_rate = min_(1, excess / p.phase_out.width[filing_status])
            reduction = amount * phase_out_rate
            age = tax_unit.members("age", period)
            age_eligible = age >= p.age_threshold
            eligible = tax_unit.any(age_eligible)
            return max_(0, amount - reduction) * eligible

    class income_tax_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        label = "federal refundable income tax credits"
        unit = USD

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.irs.credits
            previous_credits = add(tax_unit, period, p.refundable)
            middle_class_credit = tax_unit(
                "boost_middle_class_tax_credit", period
            )
            p_boost = parameters(
                period
            ).gov.contrib.congress.tlaib.boost.middle_class_tax_credit
            if p_boost.administered_through_ssa:
                return previous_credits
            return middle_class_credit + previous_credits

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
            ]
            previous_benefits = add(household, period, BENEFITS)
            middle_class_credit = add(
                household, period, ["boost_middle_class_tax_credit"]
            )
            p = parameters(
                period
            ).gov.contrib.congress.tlaib.boost.middle_class_tax_credit
            if p.administered_through_ssa is False:
                return previous_benefits
            return middle_class_credit + previous_benefits

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
            ]
            if parameters(period).gov.contrib.ubi_center.flat_tax.deduct_ptc:
                BENEFITS.append("aca_ptc")
            if not parameters(period).gov.hud.abolition:
                BENEFITS.append("spm_unit_capped_housing_subsidy")
            p = parameters(
                period
            ).gov.contrib.congress.tlaib.boost.middle_class_tax_credit
            middle_class_tax_credit = add(
                spm_unit, period, ["boost_middle_class_tax_credit"]
            )
            previous_benefits = add(spm_unit, period, BENEFITS)
            if p.administered_through_ssa is False:
                return previous_benefits
            return add(spm_unit, period, BENEFITS) + middle_class_tax_credit

    class reform(Reform):
        def apply(self):
            self.update_variable(boost_middle_class_tax_credit)
            self.update_variable(income_tax_refundable_credits)
            self.update_variable(household_benefits)
            self.update_variable(spm_unit_benefits)

    return reform


def create_boost_middle_class_tax_credit_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_boost_middle_class_tax_credit()

    p = parameters(period).gov.contrib.harris.lift.middle_class_tax_credit

    if p.in_effect:
        return create_boost_middle_class_tax_credit()
    else:
        return None


boost_middle_class_tax_credit = create_boost_middle_class_tax_credit_reform(
    None, None, bypass=True
)
