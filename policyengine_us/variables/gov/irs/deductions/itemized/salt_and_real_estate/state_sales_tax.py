from policyengine_us.model_api import *

# Dynamically create the Enum class for state sales tax
def create_state_sales_tax_enum(yaml_data):
    enum_members = {}
    for state, state_data in yaml_data.items():
        for family_size, income_data in state_data.items():
            for income_bracket, tax_value in income_data.items():
                key = f"{state}_{family_size}_{income_bracket}"  # Create unique key for the Enum
                enum_members[key] = float(tax_value)  # Store tax value as float
    return Enum("StateSalesTax", enum_members)

class state_sales_tax(Variable):
    value_type = Enum
    entity = TaxUnit
    label = "State Sales Tax"
    definition_period = YEAR

    def formula(spm_unit, person, period, parameters):
        p = parameters(period).gov.irs.deductions.itemized.salt_and_real_estate.state_sales_tax.yaml

        # Dynamically create the StateSalesTax Enum
        StateSalesTax = create_state_sales_tax_enum(p)

        # Retrieve input values
        state = person.household("state_code_str", period)
        family_size =  spm_unit("spm_unit_size", period)
        income = household("household_net_income", period)

        # Determine the income bracket
        income_brackets = [0, 20_000, 30_000, 40_000, 50_000, 60_000, 70_000,
                           80_000, 90_000, 100_000, 120_000, 140_000, 160_000,
                           180_000, 200_000, 225_000, 250_000, 275_000, 300_000]
        income_bracket = len(income_brackets)  # Default to the highest bracket
        for i, threshold in enumerate(income_brackets[1:], start=1):
            if income < threshold:
                income_bracket = i
                break

        effective_family_size = min(family_size, 6)

        # Generate the Enum key
        enum_key = f"{state}_{effective_family_size}_{income_bracket}"

        # Return the sales tax from the Enum
        return StateSalesTax[enum_key].value