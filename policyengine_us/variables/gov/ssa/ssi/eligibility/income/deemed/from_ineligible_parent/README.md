# SSI parent-to-child deeming

This module implements Supplemental Security Income (SSI) deeming of an ineligible parent's income to an eligible child under [20 CFR 416.1165](https://www.ecfr.gov/current/title-20/section-416.1165), following POMS [SI 01320.500](https://secure.ssa.gov/poms.nsf/lnx/0501320500).

## Who deems to whom

- **Ineligible parents** (416.1160(d)): the child's natural or adoptive parents who live with the child, and the co-resident spouse of each, who are not eligible for SSI. Parent ids (`parent_1_id`, `parent_2_id`) name the parents. Without ids, the unlinked parents in the child's tax unit who live with the child, and their spouses, stand in, as the parent-link contract in `household/demographic/person/_parent_links.py` allows. `resources/deemed/_ssi_parents.py` resolves these people for both income and resource deeming. A stepparent deems only through a spouse who lives in the household (POMS SI 01320.500 A.1), so a child living with a stepparent alone is not deemed income.
- **Eligible child** (`is_ssi_income_deeming_child`; POMS SI 01310.115 A.2, 416.1856): under 18, not married, not the head of a household, aged, blind or disabled and a citizen or qualified noncitizen, and living with at least one ineligible parent. A parent who meets the same status conditions is treated as eligible for SSI, so their income is not deemed (416.1165(g)(1)).
- **Ineligible children** (`ssi_parental_deeming_child_allocations`; 416.1160(d), POMS SI 01310.115 A.3, SI 01310.140 A, SI 00501.010 B.2): the child's own children and the children of any of the child's co-resident parents or parents' spouses who live in the household and are not eligible for SSI, that is, siblings, half-siblings and step-siblings. Cousins and grandchildren are not allocated. A stepparent who has left the household (a spouse in the parent's marital unit who lives elsewhere) keeps the allocation for his children at home (SI 00501.010 B.2.d). Without ids, the members of the tax unit of the child, of one of their parents or of such an absent stepparent stand in, in a household with links only when one of those people is a parent some of whose children no id names.

## Steps

1. Total the ineligible parents' earned and unearned income (416.1165(a)).
2. Deduct the ineligible child allocations, `ssi_ineligible_child_allocation` (416.1163(b)), from unearned income first, then from earned income (416.1165(b), Example 4).
3. Apply the $20 general exclusion and the $65 and one-half earned income exclusion (416.1165(d)(1)-(2)).
4. Subtract the living allowance, `ssi_parental_deeming_parent_allocation`: the individual rate for one parent, the couple rate for two, and the couple rate plus the individual rate for two natural parents and a stepparent (416.1165(d)(3), POMS SI 01320.500 B.4).
5. Divide what remains equally among the eligible children who share those parents (416.1165(e)(2)).

## Medicaid

`medicaid_optional_senior_or_disabled_unearned_income_deemed_from_ineligible_parent` applies the same steps with each state's income disregards. A disabled child need not meet the SSI citizenship or qualified-noncitizen condition, since Medicaid applies its own immigration rules; a disabled child who shares the deemed income takes no ineligible-child allocation. Missouri deems only natural or adoptive parents, never a stepparent, and allocates for every child under 18 in the home ([DSS Manual 0805.020.15](https://dssmanuals.mo.gov/mo-healthnet-for-the-aged-blind-and-disabled/0805-000-00/0805-020-00/0805-020-15/)).

## Not modeled

- 416.1166: an eligible parent living with an ineligible spouse and an eligible child. The ineligible spouse's income is deemed both to the parent, through spousal deeming, and to the child, through these rules. 416.1166 deems to the child only what is left after the parent's benefit reaches zero.
- 416.1165(e)(3): the cap on a child's share at the amount that reduces their benefit to zero, and the redistribution of the rest.
- 416.1165(d) and 416.1161(a)(2)-(3): parents receiving public income-maintenance payments, and income used to compute such payments.
- 416.1165(g)(6) and (i): the $30 medical-facility rate and the home-care waiver.
- Parent ids name natural, adoptive or step parents alike. A stepparent named by an id therefore deems even after the natural parent has left. Name only the natural or adoptive parents and let the spouse test add the stepparent.
