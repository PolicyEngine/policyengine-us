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
        # The deduction comes out of each filer's business income. The statute
        # caps the deduction per return and does not say how a joint cap is
        # divided; as a modeling convention, it is shared in proportion to
        # each filer's positive business income. The split matters only for
        # each spouse's Ohio AGI (joint filing credit qualifying income).
        deduction = person.tax_unit("oh_business_income_deduction", period)
        business_income = max_(person("oh_business_income_person", period), 0)
        total_business_income = person.tax_unit.sum(business_income)
        share = np.zeros_like(total_business_income)
        mask = total_business_income > 0
        share[mask] = business_income[mask] / total_business_income[mask]
        return deduction * share
