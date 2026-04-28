from policyengine_us.model_api import *


class is_aca_ptc_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Person is eligible for ACA premium tax credit and pays ACA premium"
    definition_period = YEAR

    def formula(person, period, parameters):
        fstatus = person.tax_unit("filing_status", period)
        separate = fstatus == fstatus.possible_values.SEPARATE

        # determine income eligibility for ACA PTC
        p = parameters(period).gov.aca
        magi_frac = person.tax_unit("aca_magi_fraction", period)
        is_income_eligible = p.ptc_income_eligibility.calc(magi_frac)

        return person("pays_aca_premium", period) & ~separate & is_income_eligible
