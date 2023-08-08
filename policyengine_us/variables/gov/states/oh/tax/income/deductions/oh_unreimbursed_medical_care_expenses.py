from policyengine_us.model_api import *


class oh_unreimbursed_medical_care_expenses(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio Unreimbursed Medical and Health Care Expenses"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-sd100-instruction-booklet.pdf#page=18",
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-sd100-instruction-booklet.pdf#page=27",
    )
    defined_for = StateCode.OH

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        premiums_expenses = tax_unit.sum(
            person("health_insurance_premiums", period)
        )
        medical_expenses = tax_unit.sum(
            person("medical_out_of_pocket_expenses", period)
        )
        # moop
        federal_agi = tax_unit("adjusted_gross_income", period)

        rate = parameters(period).gov.irs.deductions.itemized.medical.floor
        adjusted_moop = max_(0, medical_expenses - federal_agi * rate)

        return premiums_expenses + adjusted_moop
