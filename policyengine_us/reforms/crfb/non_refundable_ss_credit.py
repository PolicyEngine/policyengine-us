from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def non_refundable_ss_credit_reform() -> Reform:
    class ss_credit(Variable):
        value_type = float
        entity = Person
        label = "Social Security credit"
        definition_period = YEAR
        unit = USD

        def formula(person, period, parameters):
            taxable_social_security = person("taxable_social_security", period)
            highest_tax_rate = person.tax_unit("highest_tax_rate", period)
            ss_tax = taxable_social_security * highest_tax_rate
            p = parameters(period).gov.contrib.crfb.ss_credit
            filing_status = person.tax_unit("filing_status", period)
            return min_(ss_tax, p.amount[filing_status])

    class highest_tax_rate(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        label = "Highest tax rate faced by tax unit"
        reference = "https://www.law.cornell.edu/uscode/text/26/1"
        unit = "/1"

        def formula(tax_unit, period, parameters):
            # compute taxable income that is taxed at the main rates
            full_taxable_income = tax_unit("taxable_income", period)
            cg_exclusion = tax_unit(
                "capital_gains_excluded_from_taxable_income", period
            )
            taxinc = max_(0, full_taxable_income - cg_exclusion)

            # get bracket rates and thresholds
            p = parameters(period).gov.irs.income
            filing_status = tax_unit("filing_status", period)

            # Vectorized approach: determine the highest applicable rate for each household
            # We'll check each bracket and keep the rate if income falls within it

            # Start with the base rate (10%)
            highest_rate = p.bracket.rates["1"]

            # Get all bracket numbers
            bracket_numbers = list(p.bracket.rates.__iter__())

            # Process each bracket from lowest to highest
            # The threshold is the upper bound of each bracket
            prev_threshold = np.zeros_like(taxinc)

            for bracket_num in bracket_numbers:
                b = str(bracket_num)
                rate = p.bracket.rates[b]

                # Get the upper threshold for this bracket based on filing status
                if b == "7":
                    # The top bracket has no upper limit
                    threshold = np.inf * np.ones_like(taxinc)
                else:
                    threshold = p.bracket.thresholds[b][filing_status]

                # Update the rate for households with income in this bracket
                # Income is in this bracket if it's > prev_threshold and <= threshold
                in_bracket = (taxinc > prev_threshold) & (taxinc <= threshold)
                highest_rate = where(in_bracket, rate, highest_rate)

                # Store this threshold as the previous for next iteration
                prev_threshold = where(
                    threshold != np.inf, threshold, prev_threshold
                )

            return highest_rate

    def modify_parameters(parameters):
        parameters.gov.irs.credits.non_refundable.update(
            start=instant("2026-01-01"),
            stop=instant("2035-12-31"),
            value=[
                "foreign_tax_credit",
                "cdcc",
                "non_refundable_american_opportunity_credit",
                "lifetime_learning_credit",
                "savers_credit",
                "residential_clean_energy_credit",
                "energy_efficient_home_improvement_credit",
                "elderly_disabled_credit",
                "new_clean_vehicle_credit",
                "used_clean_vehicle_credit",
                "non_refundable_ctc",
                "ss_credit",
            ],
        )
        return parameters

    class reform(Reform):
        def apply(self):
            self.update_variable(ss_credit)
            self.update_variable(highest_tax_rate)
            self.modify_parameters(modify_parameters)

    return reform


def create_non_refundable_ss_credit_reform(
    parameters, period, bypass: bool = False
):
    # Create a create_{reform name} function that initializes the reform object
    # There are two sufficient conditions for this function to return
    # the reform

    # 1. If bypass is set to true
    if bypass is True:
        return non_refundable_ss_credit_reform()

    # 2. If boolean in in_effect.yaml is set to true
    parameter = parameters.gov.contrib.crfb.ss_credit
    current_period = period_(period)
    reform_active = False

    for i in range(5):
        if parameter(current_period).in_effect:
            # If in any of the next five years, the boolean is true,
            # set the boolean reform_active to true, and stop the check,
            # i.e., assume the reform is active in all subsequent years.
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    # if the loop set reform_active to true, return the reform.
    if reform_active:
        return non_refundable_ss_credit_reform()
    else:
        return None


# Create a reform object to by setting bypass to true,
# for the purpose of running tests
non_refundable_ss_credit_reform_object = (
    create_non_refundable_ss_credit_reform(None, None, bypass=True)
)
