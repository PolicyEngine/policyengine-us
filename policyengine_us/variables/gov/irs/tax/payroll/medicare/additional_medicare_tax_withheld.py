from policyengine_us.model_api import *


class additional_medicare_tax_withheld(Variable):
    value_type = float
    entity = Person
    label = "Additional Medicare Tax withheld from wages"
    documentation = "Additional Medicare Tax an employer withholds from the employee's wages. This can differ from the tax unit's additional_medicare_tax liability, which is reconciled on Form 8959."
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/3102#f_1",
        "https://www.law.cornell.edu/cfr/text/26/31.3102-4#a",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.payroll.medicare.additional
        # Employers withhold on wages above the threshold without regard to
        # filing status, a spouse's wages or wages from other employers.
        # Wages are not split by employer, so this treats them as paid by one.
        wages = person("payroll_tax_gross_wages", period)
        return p.rate * max_(wages - p.withholding_threshold, 0)
