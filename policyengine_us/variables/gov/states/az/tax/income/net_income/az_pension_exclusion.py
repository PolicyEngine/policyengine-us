from policyengine_us.model_api import *


class az_pension_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "Exclusion Arizona State or Local Government Pensions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://azdor.gov/sites/default/files/2023-03/FORMS_INDIVIDUAL_2022_140BOOKLET.pdf#page=18"
        "https://azdor.gov/sites/default/files/2023-03/FORMS_INDIVIDUAL_2021_140BOOKLET.pdf#page=23"
        "https://www.azleg.gov/ars/43/01022.htm"
    )
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.az.tax.income.pension_exclusion
        person = tax_unit.members
        filing_status = tax_unit("filing_status", period)
        is_joint = filing_status == filing_status.possible_values.JOINT

        # calculate the total allowed pension
        # need to double check if this meets the requirements
        total_allowed_pension_exclusion = min_(
            p.maximum_amount, person("taxable_public_pension_income", period)
        )

        is_head = person("is_tax_unit_head", period)
        is_spouse = person("is_tax_unit_spouse", period)

        return where(
            is_joint,
            tax_unit.sum(
                where(is_head | is_spouse, total_allowed_pension_exclusion, 0)
            ),
            tax_unit.sum(where(is_head, total_allowed_pension_exclusion, 0)),
        )
