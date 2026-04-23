from policyengine_us.model_api import *


class sstb_qualified_business_income(Variable):
    value_type = float
    entity = Person
    label = "SSTB qualified business income"
    documentation = (
        "Qualified business income from a specified service trade or business "
        "(SSTB) under IRC §199A(d)(2). Tracked separately from non-SSTB QBI so "
        "the §199A(d)(3) applicable-percentage phaseout above the threshold can "
        "reduce only the SSTB component."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/199A#c",
        "https://www.law.cornell.edu/uscode/text/26/199A#d_2",
    )

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
        # Pro-rate QBI deductions across positive non-SSTB and SSTB income so
        # that mixed-sign categories do not generate negative shares.
        positive_non_sstb_gross = max_(0, non_sstb_gross)
        positive_sstb_gross = max_(0, sstb_gross)
        positive_gross_total = positive_non_sstb_gross + positive_sstb_gross
        qbi_deductions = add(person, period, p.deduction_definition)
        sstb_share = where(
            positive_gross_total > 0,
            positive_sstb_gross / positive_gross_total,
            0,
        )
        return max_(0, sstb_gross - qbi_deductions * sstb_share)
