"""Form 8815 inputs. The interest must already be in taxable_interest_income
(Series EE and I bond interest, deferred or not, is reported when the
simulator recognizes it)."""

from policyengine_us.model_api import *

_REF = (
    "https://www.law.cornell.edu/uscode/text/26/135",
    "https://www.irs.gov/pub/irs-pdf/f8815.pdf",
)


def _money(name, label, documentation):
    globals()[name] = type(
        name,
        (Variable,),
        dict(
            value_type=float,
            entity=TaxUnit,
            definition_period=YEAR,
            unit=USD,
            label=label,
            documentation=documentation,
            reference=_REF,
            __module__=__name__,
        ),
    )


_money(
    "savings_bond_education_qualified_expenses",
    "Qualified higher education expenses for the savings bond exclusion",
    "Tuition and fees for the filer, spouse or dependents (Form 8815 line 2); excludes room and board.",
)
_money(
    "savings_bond_education_nontaxable_benefits",
    "Nontaxable educational benefits for the savings bond exclusion",
    "Scholarships, employer assistance, and expenses used for other education benefits (Form 8815 line 3).",
)
_money(
    "savings_bond_redemption_proceeds",
    "Proceeds of post-1989 Series EE and I bonds cashed this year",
    "Principal and interest (Form 8815 line 5), for bonds issued after 1989 to an owner at least 24 years old at issue.",
)
_money(
    "savings_bond_redemption_interest",
    "Interest included in post-1989 Series EE and I bond proceeds",
    "Interest part of the proceeds (Form 8815 line 6).",
)
_money(
    "savings_bond_education_exclusion_magi_override",
    "Modified AGI for the savings bond exclusion, if supplied",
    "Exact Form 8815 line 9 modified AGI; 0 uses PolicyEngine's computation.",
)
