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
            bracket_tops = p.bracket.thresholds
            bracket_rates = p.bracket.rates
            filing_status = tax_unit("filing_status", period)

            # find the highest bracket that applies to this income level
            highest_rate = 0
            bracket_bottom = 0
            for i in range(1, len(list(bracket_rates.__iter__())) + 1):
                b = str(i)
                bracket_top = bracket_tops[b][filing_status]
                # if income falls in this bracket, this is the marginal rate
                if taxinc > bracket_bottom:
                    highest_rate = bracket_rates[b]
                # if income is below this bracket top, we've found the highest applicable rate
                if taxinc <= bracket_top:
                    break
                bracket_bottom = bracket_top

            return highest_rate

    class reform(Reform):
        def apply(self):
            self.update_variable(ss_credit)
            self.update_variable(highest_tax_rate)
            self.neutralize_variable("additional_senior_deduction")

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
