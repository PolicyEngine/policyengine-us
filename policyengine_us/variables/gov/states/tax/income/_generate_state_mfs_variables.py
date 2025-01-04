from policyengine_us.model_api import *

# Define the correct individual/joint variable names for each state and type
VAR_NAMES = {
    "ar": {
        "standard_deduction": (
            "ar_standard_deduction_indiv",
            "ar_standard_deduction_joint",
        ),
        "itemized_deductions": (
            "ar_itemized_deductions_indiv",
            "ar_itemized_deductions_joint",
        ),
        "taxable_income": (
            "ar_taxable_income_indiv",
            "ar_taxable_income_joint",
        ),
        "agi": ("ar_agi_indiv", "ar_agi_joint"),
    },
    "de": {
        "standard_deduction": (
            "de_standard_deduction_indv",
            "de_standard_deduction_joint",
        ),
        "itemized_deductions": (
            "de_itemized_deductions_indv",
            "de_itemized_deductions_joint",
        ),
        "taxable_income": (
            "de_taxable_income_indv",
            "de_taxable_income_joint",
        ),
        "agi": ("de_agi_indiv", "de_agi_joint"),
    },
    "ia": {
        "standard_deduction": (
            "ia_standard_deduction_indiv",
            "ia_standard_deduction_joint",
        ),
        "itemized_deductions": (
            "ia_itemized_deductions_indiv",
            "ia_itemized_deductions_joint",
        ),
        "taxable_income": (
            "ia_taxable_income_indiv",
            "ia_taxable_income_joint",
        ),
        "agi": (
            "ia_taxable_income_indiv",
            "ia_taxable_income_joint",
        ),  # Using taxable income for IA
    },
    "ky": {
        "standard_deduction": (
            "ky_standard_deduction_indiv",
            "ky_standard_deduction_joint",
        ),
        "itemized_deductions": (
            "ky_itemized_deductions_indiv",
            "ky_itemized_deductions_joint",
        ),
        "taxable_income": (
            "ky_taxable_income_indiv",
            "ky_taxable_income_joint",
        ),
        "agi": ("ky_agi_indiv", "ky_agi_joint"),
    },
    "ms": {
        "standard_deduction": (
            "ms_standard_deduction_indiv",
            "ms_standard_deduction_joint",
        ),
        "itemized_deductions": (
            "ms_itemized_deductions_indiv",
            "ms_itemized_deductions_joint",
        ),
        "taxable_income": (
            "ms_taxable_income_indiv",
            "ms_taxable_income_joint",
        ),
        "agi": ("ms_agi", "ms_agi"),  # MS doesn't have separate AGI calcs
    },
    "mt": {
        "standard_deduction": (
            "mt_standard_deduction_indiv",
            "mt_standard_deduction_joint",
        ),
        "itemized_deductions": (
            "mt_itemized_deductions_indiv",
            "mt_itemized_deductions_joint",
        ),
        "taxable_income": (
            "mt_taxable_income_indiv",
            "mt_taxable_income_joint",
        ),
        "agi": ("mt_agi", "mt_agi"),  # MT doesn't have separate AGI calcs
    },
}

# Create all state variable classes
for state_code, state_name in [
    ("ar", "Arkansas"),
    ("de", "Delaware"),
    ("ia", "Iowa"),
    ("ky", "Kentucky"),
    ("ms", "Mississippi"),
    ("mt", "Montana"),
]:
    for var_code, var_label in [
        ("standard_deduction", "standard deduction"),
        ("itemized_deductions", "itemized deductions"),
        ("taxable_income", "taxable income"),
        ("agi", "adjusted gross income"),
    ]:
        indiv_var, joint_var = VAR_NAMES[state_code][var_code]

        # Create the class with all attributes
        globals()[f"{state_code}_{var_code}"] = type(
            f"{state_code}_{var_code}",
            (Variable,),
            dict(
                value_type=float,
                entity=TaxUnit,
                label=f"{state_name} {var_label}",
                unit=USD,
                definition_period=YEAR,
                defined_for=getattr(StateCode, state_code.upper()),
                formula=lambda self, tax_unit, period, parameters, indiv=indiv_var, joint=joint_var: where(
                    tax_unit(
                        f"{self.__class__.__name__.split('_')[0]}_files_separately",
                        period,
                    ),
                    add(tax_unit, period, [indiv]),
                    add(tax_unit, period, [joint]),
                ),
            ),
        )
