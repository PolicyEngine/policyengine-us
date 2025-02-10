from policyengine_us.model_api import *


class ga_additional_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia additional standard deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://apps.dor.ga.gov/FillableForms/PDFViewer/Index?form=2022GA500"
    )
    defined_for = StateCode.GA

    def formula(tax_unit, period, parameters):
        # person = tax_unit.members
        p = parameters(period).gov.states.ga.tax.income.deductions.standard
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        # Head gets extra standard deduction if aged and/or blind.
        age_head = tax_unit("age_head", period)
        eligible_aged_head = age_head >= p.aged.age_threshold
        blind_head = tax_unit("blind_head", period)
        extra_head = (
            blind_head * p.blind.head + eligible_aged_head * p.aged.amount.head
        )

        # Spouse gets extra standard deduction if aged and/or blind and filing jointly.
        age_spouse = tax_unit("age_spouse", period)
        eligible_aged_spouse = age_spouse >= p.aged.age_threshold
        blind_spouse = tax_unit("blind_spouse", period)
        extra_spouse = where(
            filing_status == status.JOINT,
            (
                blind_spouse * p.blind.spouse
                + eligible_aged_spouse * p.aged.amount.spouse
            ),
            0,
        )
        # total extra deduction
        return extra_head + extra_spouse
