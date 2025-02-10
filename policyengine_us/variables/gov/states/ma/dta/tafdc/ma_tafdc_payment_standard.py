from policyengine_us.model_api import *


class ma_tafdc_payment_standard(Variable):
    value_type = float
    unit = USD
    entity = TaxUnit
    label = "Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) payment standard"
    definition_period = MONTH
    reference = "https://www.masslegalservices.org/content/75-how-much-will-you-get-each-month"
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        in_public_housing = tax_unit.household("is_in_public_housing", period)
        p = parameters(period).gov.states.ma.dta.tafdc.eligibility.income_limit
        unit_size = tax_unit("tax_unit_size", period)
        capped_unit_size = min_(unit_size, p.max_unit_size)
        additional_people_in_unit = max_(0, unit_size - p.max_unit_size)
        # Calculate the base income limit for non-teen parents
        ps_non_teen_parent = where(
            in_public_housing,
            p.base.public_housing.calc(capped_unit_size),
            p.base.private_housing.calc(capped_unit_size),
        )
        additional_person_ps = p.additional_person * additional_people_in_unit
        return ps_non_teen_parent + additional_person_ps
