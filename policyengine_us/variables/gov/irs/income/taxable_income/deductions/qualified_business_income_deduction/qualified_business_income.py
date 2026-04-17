from policyengine_us.model_api import *


class qualified_business_income(Variable):
    value_type = float
    entity = Person
    label = "Qualified business income"
    documentation = (
        "Non-SSTB business income that qualifies for the qualified business "
        "income deduction. Excludes sstb_self_employment_income, which is "
        "tracked separately so the §199A(d)(3) phaseout can apply only to the "
        "SSTB component above the threshold."
    )
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/199A#c"
    defined_for = "business_is_qualified"

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.deductions.qbi
        non_sstb_gross = 0
        for var in p.income_definition:
            non_sstb_gross += person(var, period) * person(
                var + "_would_be_qualified", period
            )
        sstb_gross = person("sstb_self_employment_income", period) * person(
            "sstb_self_employment_income_would_be_qualified", period
        )
        # Pro-rate QBI deductions across positive non-SSTB and SSTB income
        # only, so mixed-sign categories do not generate negative shares.
        positive_non_sstb_gross = max_(0, non_sstb_gross)
        positive_sstb_gross = max_(0, sstb_gross)
        positive_gross_total = positive_non_sstb_gross + positive_sstb_gross
        qbi_deductions = add(person, period, p.deduction_definition)
        non_sstb_share = where(
            positive_gross_total > 0,
            positive_non_sstb_gross / positive_gross_total,
            0,
        )
        return max_(0, non_sstb_gross - qbi_deductions * non_sstb_share)
