from policyengine_us.model_api import *


class qualified_business_income_deduction_person(Variable):
    value_type = float
    entity = Person
    label = "Qualified business income deduction for each person"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/199A#b_1",
        "https://www.irs.gov/pub/irs-prior/p535--2018.pdf",
    )

    def formula(person, period, parameters):
        # Allocate the business income deduction to the head and spouse
        # based on their share of per cap qualified business income deduction
        # amount. The deduction is theirs alone, so a tax unit dependent's
        # share is zero.
        tax_unit = person.tax_unit
        filer = ~person("is_tax_unit_dependent", period)
        qbid_amt = person("qbid_amount", period) * filer
        total_qbid_amount = tax_unit.sum(qbid_amt)
        deduction = tax_unit("qualified_business_income_deduction", period)
        # From 2026 the 199A(i) minimum can give a deduction when every
        # per-person amount is zero, as when the wage limit removes it; share
        # that in proportion to positive qualified business income, or give
        # it to the head.
        qbi = filer * max_(
            0,
            person("qualified_business_income", period)
            + person("sstb_qualified_business_income", period),
        )
        total_qbi = tax_unit.sum(qbi)
        weight = where(
            total_qbid_amount > 0,
            qbid_amt,
            where(total_qbi > 0, qbi, person("is_tax_unit_head", period)),
        )
        total_weight = tax_unit.sum(weight)
        fraction = np.divide(
            weight,
            total_weight,
            out=np.zeros_like(total_weight, dtype=float),
            where=total_weight > 0,
        )
        return fraction * deduction
