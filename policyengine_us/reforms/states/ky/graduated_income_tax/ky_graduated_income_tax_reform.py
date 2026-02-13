from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_ky_graduated_income_tax() -> Reform:
    """
    Creates reform for Kentucky HB 13 and HB 152 graduated income tax.

    Both bills implement a "cliff" design where if income exceeds a threshold,
    the flat rate applies to the ENTIRE income (not just marginal).

    HB 13 (TY 2027+):
    - 3.5% on income up to $250,000
    - 6% on income $250,000-$300,000
    - Flat 6% on ALL income if exceeds $300,000

    HB 152 (TY 2027+):
    - 4% on income up to $100,000
    - 5% on income $100,000-$125,000
    - 6% on income $125,000-$150,000
    - Flat 6% on ALL income if exceeds $150,000
    """

    def calculate_graduated_tax_with_cliff(
        taxable_income, p_hb13, p_hb152, p_baseline
    ):
        """
        Calculate tax using graduated brackets with cliff design.

        If HB 13 is in effect and income > $300k: 6% on entire income
        If HB 152 is in effect and income > $150k: 6% on entire income
        Otherwise: use graduated brackets or baseline
        """
        hb13_active = p_hb13.in_effect
        hb152_active = p_hb152.in_effect

        # HB 13 calculation
        hb13_above_cliff = taxable_income > p_hb13.cliff_threshold
        hb13_graduated_tax = p_hb13.brackets.calc(taxable_income)
        hb13_flat_tax = taxable_income * p_hb13.flat_rate
        hb13_tax = where(hb13_above_cliff, hb13_flat_tax, hb13_graduated_tax)

        # HB 152 calculation
        hb152_above_cliff = taxable_income > p_hb152.cliff_threshold
        hb152_graduated_tax = p_hb152.brackets.calc(taxable_income)
        hb152_flat_tax = taxable_income * p_hb152.flat_rate
        hb152_tax = where(
            hb152_above_cliff, hb152_flat_tax, hb152_graduated_tax
        )

        # Baseline calculation
        baseline_tax = taxable_income * p_baseline.rate

        # Apply appropriate calculation based on which reform is active
        # HB 13 takes precedence if both are somehow active
        return where(
            hb13_active,
            hb13_tax,
            where(hb152_active, hb152_tax, baseline_tax),
        )

    class ky_income_tax_before_non_refundable_credits_indiv(Variable):
        value_type = float
        entity = Person
        label = "Kentucky income tax before non-refundable credits when married couples are filing separately"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.KY

        def formula(person, period, parameters):
            taxable_income = person("ky_taxable_income_indiv", period)
            p_hb13 = parameters(period).gov.contrib.states.ky.hb13
            p_hb152 = parameters(period).gov.contrib.states.ky.hb152
            p_baseline = parameters(period).gov.states.ky.tax.income

            return calculate_graduated_tax_with_cliff(
                taxable_income, p_hb13, p_hb152, p_baseline
            )

    class ky_income_tax_before_non_refundable_credits_joint(Variable):
        value_type = float
        entity = Person
        label = "Kentucky income tax before non-refundable credits when married filing jointly"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.KY

        def formula(person, period, parameters):
            taxable_income = person("ky_taxable_income_joint", period)
            p_hb13 = parameters(period).gov.contrib.states.ky.hb13
            p_hb152 = parameters(period).gov.contrib.states.ky.hb152
            p_baseline = parameters(period).gov.states.ky.tax.income

            return calculate_graduated_tax_with_cliff(
                taxable_income, p_hb13, p_hb152, p_baseline
            )

    class reform(Reform):
        def apply(self):
            self.update_variable(
                ky_income_tax_before_non_refundable_credits_indiv
            )
            self.update_variable(
                ky_income_tax_before_non_refundable_credits_joint
            )

    return reform


def create_ky_graduated_income_tax_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_ky_graduated_income_tax()

    p_hb13 = parameters.gov.contrib.states.ky.hb13
    p_hb152 = parameters.gov.contrib.states.ky.hb152

    reform_active = False
    current_period = period_(period)

    # Check if either reform will be active in the next 5 years
    for i in range(5):
        if (
            p_hb13(current_period).in_effect
            or p_hb152(current_period).in_effect
        ):
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ky_graduated_income_tax()
    else:
        return None


ky_graduated_income_tax = create_ky_graduated_income_tax_reform(
    None, None, bypass=True
)
