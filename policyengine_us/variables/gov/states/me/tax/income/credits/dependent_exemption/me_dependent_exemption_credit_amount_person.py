from policyengine_us.model_api import *


class me_dependent_exemption_credit_amount_person(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Maine dependent exemption credit amount for each person"
    reference = (
        "https://www.mainelegislature.org/legis/statutes/36/title36sec5219-SS.html",
        # 2025 Form 1040ME Instructions, line 13a and Schedule A, lines 1
        # and 10. PDF pages 5, 10.
        "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/25_1040me_gen_instr_w_cover_pg.pdf#page=5",
        # 2025 Dependent Exemption Tax Credit Worksheet, lines 1 and 3.
        "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/25_dependent_exemption_tx_cr_fillable.pdf#page=1",
        # 2025 Instructions for Schedule 8812, TIN Required by Due Date of
        # Your Return To Claim the ODC, and Credit for Other Dependents.
        # PDF pages 1-2.
        "https://www.irs.gov/pub/irs-pdf/i1040s8.pdf#page=1",
    )
    definition_period = YEAR
    defined_for = "is_tax_unit_dependent"

    def formula(person, period, parameters):
        # 36 MRSA 5219-SS allows the credit for each "qualifying child and
        # dependent of the taxpayer for whom the taxpayer was eligible to
        # claim the federal child tax credit pursuant to the Code, Section
        # 24". The worksheet counts the dependents on Form 1040ME line 13a,
        # which counts each dependent for whom the filer is eligible to claim
        # "the federal child tax credit or the credit for other dependents".
        # So a dependent counts when either credit is allowed for that person
        # before the phase-out. This applies the federal identification
        # tests: the dependent needs an SSN, ITIN or ATIN, and the filer (on
        # a joint return, each spouse) an SSN or ITIN (IRC 24(e); Schedule
        # 8812 instructions). A child whose filer has no valid SSN still
        # counts through the credit for other dependents (IRC 24(h)(4)(C),
        # 24(h)(7)). A return on which a filer can be claimed as a dependent
        # has no dependents (IRC 152(b)(1)).
        section_24_amount = person("ctc_individual_maximum", period)
        p = parameters(period).gov.states.me.tax.income.credits.dependent_exemption
        age = person("age", period)
        multiplier = p.multiplier.calc(age)
        return (section_24_amount > 0) * multiplier * p.amount
