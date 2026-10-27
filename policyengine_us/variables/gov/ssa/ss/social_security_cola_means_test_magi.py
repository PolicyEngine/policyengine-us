from policyengine_us.model_api import *


class social_security_cola_means_test_magi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Social Security COLA means-test MAGI excluding Social Security"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Income for the contributed COLA means test in this tax year. The "
        "OACT A9-linked proposal uses the IRMAA MAGI definition in Social "
        "Security Act section 1839(i)(4): AGI with sections 135, 911, 931 "
        "and 933 exclusions added back, plus tax-exempt interest. This "
        "reform excludes taxable Social Security from that measure. Income "
        "and deductions follow the filer's return, leaving out dependents' "
        "own amounts; parent-owned savings bond exclusions recorded on a "
        "dependent retain the model's filer-amount convention. The COLA "
        "decision reads this variable for the prior tax year, so benefit "
        "dependencies move strictly backward in time. Supplying this "
        "variable for each tax year overrides the calculation and provides "
        "an explicit income history. Dataset extension supplies a "
        "same-record prior-year proxy in static population cross-sections, "
        "which is not an observed longitudinal income history."
    )
    reference = (
        "https://www.ssa.gov/OACT/solvency/provisions/cola.html",
        "https://www.ssa.gov/OACT/solvency/SJohnson_20161208.pdf#page=8",
        "https://www.congress.gov/bill/114th-congress/house-bill/6489/text",
        "https://www.ssa.gov/OP_Home/ssact/title18/1839.htm",
    )

    def formula(tax_unit, period, parameters):
        agi_with_exclusions = tax_unit(
            "agi_plus_section_911_931_933_exclusions", period
        )
        p = parameters(period).gov.irs.ald
        other_addbacks = tax_unit_non_dep_add(
            tax_unit,
            period,
            ["tax_exempt_interest_income", "us_bonds_for_higher_ed"],
            include_dependents=p.filer_amounts_recorded_on_dependents,
        )
        taxable_social_security = tax_unit("tax_unit_taxable_social_security", period)
        return agi_with_exclusions + other_addbacks - taxable_social_security
