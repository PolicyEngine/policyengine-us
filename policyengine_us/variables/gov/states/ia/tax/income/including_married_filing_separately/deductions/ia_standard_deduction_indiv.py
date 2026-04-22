from policyengine_us.model_api import *


class ia_standard_deduction_indiv(Variable):
    value_type = float
    entity = Person
    label = "Iowa standard deduction when married couples file separately"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenue.iowa.gov/sites/default/files/2022-01/IA1040%2841-001%29.pdf",
        "https://revenue.iowa.gov/sites/default/files/2023-01/2021%20Expanded%20Instructions_010323.pdf",
        "https://revenue.iowa.gov/sites/default/files/2023-01/2022IA1040%2841001%29.pdf",
        "https://revenue.iowa.gov/sites/default/files/2023-03/2022%20Expanded%20Instructions_022023.pdf",
    )
    defined_for = StateCode.IA

    def formula(person, period, parameters):
        us_filing_status = person.tax_unit("filing_status", period)
        fsvals = us_filing_status.possible_values
        filing_status = select(
            [
                us_filing_status == fsvals.JOINT,
                us_filing_status == fsvals.SINGLE,
                us_filing_status == fsvals.SEPARATE,
                us_filing_status == fsvals.HEAD_OF_HOUSEHOLD,
                us_filing_status == fsvals.SURVIVING_SPOUSE,
            ],
            [
                fsvals.SEPARATE,  # couples are filing separately on Iowa form
                fsvals.SINGLE,
                fsvals.SEPARATE,
                fsvals.HEAD_OF_HOUSEHOLD,
                fsvals.SURVIVING_SPOUSE,
            ],
        )
        p = parameters(period).gov.states.ia.tax.income.deductions.standard

        if p.applies_federal:
            # IA 1040 line 1d: "Standard deduction from federal 1040, line 12e"
            # Each spouse gets half the basic + their own additional (elderly/blind).
            fed_p = parameters(period).gov.irs.deductions
            basic_half = fed_p.standard.amount[filing_status]
            age = person("age", period)
            aged = age >= fed_p.standard.aged_or_blind.age_threshold
            is_blind = person("is_blind", period)
            aged_blind_per_person = aged.astype(int) + is_blind.astype(int)
            additional_per_person = (
                aged_blind_per_person
                * fed_p.standard.aged_or_blind.amount[filing_status]
            )
            deduction = basic_half + additional_per_person
        else:
            deduction = p.amount[filing_status]

        return person("is_tax_unit_head_or_spouse", period) * deduction
