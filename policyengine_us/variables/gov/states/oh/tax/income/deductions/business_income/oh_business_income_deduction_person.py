from policyengine_us.model_api import *


class oh_business_income_deduction_person(Variable):
    value_type = float
    entity = Person
    label = "Ohio business income deduction for each filer"
    unit = USD
    definition_period = YEAR
    reference = (
        # R.C. 5747.01(A)(28): deducted "from the portion of an individual's
        # federal adjusted gross income that is business income".
        "https://codes.ohio.gov/ohio-revised-code/section-5747.01",
        "https://dam.assets.ohio.gov/image/upload/tax.ohio.gov/forms/ohio_individual/individual/2024/1040-bundle-original-fi.pdf#page=5",
    )
    defined_for = StateCode.OH

    def formula(person, period, parameters):
        # The deduction comes out of the business income of the filer who
        # earned it, in proportion to each filer's positive business income.
        deduction = person.tax_unit("oh_business_income_deduction", period)
        business_income = max_(person("oh_business_income_person", period), 0)
        total_business_income = person.tax_unit.sum(business_income)
        share = np.zeros_like(total_business_income)
        mask = total_business_income > 0
        share[mask] = business_income[mask] / total_business_income[mask]
        return deduction * share
