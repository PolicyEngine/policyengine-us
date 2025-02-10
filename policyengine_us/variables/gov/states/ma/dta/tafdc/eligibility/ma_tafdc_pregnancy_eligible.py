from policyengine_us.model_api import *


class ma_tafdc_pregnancy_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) due to income"
    definition_period = MONTH
    reference = "https://www.mass.gov/how-to/transitional-aid-to-families-with-dependent-children-tafdc"
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        is_pregnant = person("is_pregnant", period)
        age = person("age", period)
        pregancy_months = person("pregancy_months", period)
        p = parameters(period).gov.states.ma.dta.tafdc.eligibility
        young_pregnancy = age < p.pregnancy_age
        months_eligible = where(
            young_pregnancy, True, pregancy_months >= p.pregnancy_months
        )
        return tax_unit.any(is_pregnant & months_eligible)
