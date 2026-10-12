"""Invariants of SSI parent-to-child income deeming (20 CFR 416.1165).

An eligible child's ineligible parents are 'a natural or adoptive parent, or
the spouse ... of a natural or adoptive parent, who lives with you and is not
eligible for SSI benefits' (416.1160(d)). Their income, less an allocation for
each ineligible child ('the natural or adopted child of your parent or of your
parent's spouse ... who lives in the same household with you'), the $20 and
earned income exclusions and the parents' living allowance, is divided among
the parents' eligible children (416.1165(b)-(e)).

Each Hypothesis example builds a batch of random households: a mother, a
father who may live elsewhere or be absent, a stepparent married to the
mother, an aunt and a grandparent, and children of every relationship (full,
half and step siblings, cousins, unrelated children), some disabled, some
without qualifying immigration status, some living elsewhere, filed in
assorted tax units, with parent ids on everyone, no one or some people. Half
the households are in Missouri, half in the District of Columbia. It checks:

1. Differential: is_ssi_income_deeming_child, is_ssi_ineligible_parent,
   ssi_parental_deeming_child_allocations,
   ssi_parental_deeming_parent_allocation and
   ssi_unearned_income_deemed_from_ineligible_parent equal an oracle written
   here from the regulation and the parent-link contract in
   household/demographic/person/_parent_links.py, without the model. With
   ids the oracle is the regulation itself; without ids it is the documented
   tax-unit proxy.
2. Medicaid: the Medicaid copy equals the same oracle, with Missouri's
   natural-parent-only deemors and every-minor allocation (DSS Manual
   0805.020.15) in Missouri, and the SSI rules in the District, whose $20
   disregard and SSI-order exclusions make it equal the SSI variable.
3. Conservation: the shares deemed to the eligible children of one set of
   parents add up to the parents' net deemable income.
4. Order: listing each household's people in reverse gives the same values.
5. Monotonicity: more income for every child never lowers deemed income
   (allocations shrink, 416.1163(b)(2)); more income for every adult never
   lowers it.
6. Bounds: deemed income is never negative or above the parents' gross
   income.

YAML covers the worked cases. This file routes to the Rest/core group.
"""

import numpy as np
from hypothesis import given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

YEAR = 2026
INDIVIDUAL = 994  # 2026 Federal benefit rates
COUPLE = 1_491
MONTHLY_ALLOCATION = COUPLE - INDIVIDUAL  # 416.1163(b)(1)
GENERAL_EXCLUSION = 20  # 416.1124(c)(12); DC and MO Medicaid disregards
EARNED_EXCLUSION = 65  # 416.1112(c)(5)
CHILD_AGE = 18
STUDENT_AGE = 22
ABSENT_PARENT_ID = 999_999
HOUSEHOLDS_PER_EXAMPLE = 30
TOLERANCE = 1e-6

INCOME = st.sampled_from((0, 300, 1_200, 3_000))
ADULT = st.fixed_dictionaries(
    {
        "earned": INCOME,
        "unearned": st.sampled_from((0, 150, 900)),
        "disabled": st.sampled_from((False, False, False, True)),
        "citizen": st.sampled_from((True, True, True, False)),
    }
)
CHILD_KINDS = (
    "full",
    "maternal",
    "paternal",
    "step",
    "half_step",
    "paternal_step",
    "cousin",
    "unrelated",
)
CHILD = st.fixed_dictionaries(
    {
        "kind": st.sampled_from(CHILD_KINDS),
        "age": st.integers(0, 20),
        "disabled": st.booleans(),
        "citizen": st.sampled_from((True, True, True, False)),
        "student": st.booleans(),
        "unearned": st.sampled_from((0, 150, 600)),
        # About one in five lives in another household.
        "away": st.sampled_from((False, False, False, False, True)),
        "tax_unit": st.sampled_from(("family", "father", "aunt", "grandparent", "own")),
        "has_ids": st.booleans(),
    }
)
HOUSEHOLD = st.fixed_dictionaries(
    {
        "mother": ADULT,
        "father": ADULT,
        "father_status": st.sampled_from(("married", "unmarried", "away", "absent")),
        "stepparent": st.one_of(st.none(), ADULT),
        "stepparent_files_separately": st.booleans(),
        # A stepparent who has left still has an allocation for his children
        # at home (POMS SI 00501.010 B.2.d).
        "stepparent_away": st.sampled_from((False, False, True)),
        # The wife of a father who is not married to the mother.
        "stepmother": st.one_of(st.none(), ADULT),
        "aunt": st.one_of(st.none(), ADULT),
        "grandparent": st.one_of(st.none(), ADULT),
        "children": st.lists(CHILD, min_size=1, max_size=5),
        "ids": st.sampled_from(("none", "all", "some")),
        "report_own_children": st.booleans(),
    }
)


def _adult(earned=0, unearned=0, disabled=False, citizen=True):
    return dict(earned=earned, unearned=unearned, disabled=disabled, citizen=citizen)


def _child(kind, disabled=False, age=8, has_ids=True, tax_unit="family", **facts):
    child = dict(
        kind=kind,
        age=age,
        disabled=disabled,
        citizen=True,
        student=False,
        unearned=0,
        away=False,
        tax_unit=tax_unit,
        has_ids=has_ids,
    )
    child.update(facts)
    return child


def _blended(ids, stepmother, father_joins_family=False):
    """Two natural parents at home, the mother's husband and maybe the
    father's wife: three or four deemors for their child (POMS SI 01320.500
    B.4, Example F.5), and different deemor sets for half siblings."""
    return dict(
        mother=_adult(earned=3_000),
        father=_adult(earned=3_000, unearned=900),
        father_status="unmarried",
        stepparent=_adult(earned=1_200),
        stepparent_files_separately=False,
        stepparent_away=False,
        stepmother=_adult(earned=3_000) if stepmother else None,
        father_joins_family=father_joins_family,
        aunt=None,
        grandparent=None,
        children=[
            _child("full", disabled=True),
            _child("full", disabled=True, age=5),
            _child("maternal", disabled=True, age=12),
            _child("half_step", age=3, unearned=150),
            _child("paternal_step", age=2, tax_unit="father"),
            _child("cousin", age=10),
        ],
        ids=ids,
        report_own_children=True,
    )


# Fixed households in every batch, so the rarer structures are always
# exercised: three and four deemors, with and without ids.
FIXED_HOUSEHOLDS = [
    _blended("all", stepmother=False),
    _blended("all", stepmother=True),
    _blended("some", stepmother=True),
    _blended("none", stepmother=False),
    # Without ids the proxy finds three deemors only when the father files
    # in the mother's tax unit.
    _blended("none", stepmother=False, father_joins_family=True),
]
BATCH = st.lists(
    HOUSEHOLD, min_size=HOUSEHOLDS_PER_EXAMPLE, max_size=HOUSEHOLDS_PER_EXAMPLE
).map(lambda households: households + FIXED_HOUSEHOLDS)


def _people(index, household):
    """Return each person's facts: true parents, spouse, tax unit, home."""

    def name(role):
        return f"h{index}_{role}"

    status = household["father_status"]
    father_present = status != "absent"
    married = status == "married"
    stepparent = household["stepparent"] if not married else None
    stepmother = household["stepmother"] if status == "unmarried" else None
    people = []

    def adult(role, facts, tax_unit, role_in_unit, away=False, spouse=None):
        people.append(
            dict(
                name=name(role),
                age=60 if role == "grandparent" else 40,
                disabled=facts["disabled"],
                citizen=facts["citizen"],
                student=False,
                earned=facts["earned"],
                unearned=facts["unearned"],
                parents=(),
                away=away,
                tax_unit=tax_unit,
                role=role_in_unit,
                spouse=spouse,
                has_ids=False,
            )
        )

    adult(
        "mother",
        household["mother"],
        "family",
        "head",
        spouse=(
            name("father") if married else (name("stepparent") if stepparent else None)
        ),
    )
    joins = household.get("father_joins_family", False)
    if father_present:
        adult(
            "father",
            household["father"],
            "family" if married or joins else "father",
            "spouse" if married else ("dependent" if joins else "head"),
            away=status == "away",
            spouse=(
                name("mother")
                if married
                else (name("stepmother") if stepmother else None)
            ),
        )
    if stepmother:
        adult(
            "stepmother",
            stepmother,
            "father",
            "spouse",
            spouse=name("father"),
        )
    if stepparent:
        separate = household["stepparent_files_separately"]
        adult(
            "stepparent",
            stepparent,
            "stepparent" if separate else "family",
            "head" if separate else "spouse",
            away=household["stepparent_away"],
            spouse=name("mother"),
        )
    if household["aunt"]:
        adult("aunt", household["aunt"], "aunt", "head")
    if household["grandparent"]:
        adult("grandparent", household["grandparent"], "grandparent", "head")
    present = {person["name"] for person in people}
    units = {person["tax_unit"] for person in people}

    def parent(role):
        return name(role) if name(role) in present else None

    for position, child in enumerate(household["children"]):
        parents = {
            "full": (parent("mother"), parent("father")),
            "maternal": (parent("mother"),),
            "paternal": (parent("father"),),
            "step": (parent("stepparent"),),
            "half_step": (parent("mother"), parent("stepparent")),
            "paternal_step": (parent("father"), parent("stepmother")),
            "cousin": (parent("aunt"),),
            "unrelated": (None,),
        }[child["kind"]]
        tax_unit = child["tax_unit"] if child["tax_unit"] in units else "family"
        if child["tax_unit"] == "own":
            tax_unit = f"child{position}"
        people.append(
            dict(
                name=name(f"child{position}"),
                age=child["age"],
                disabled=child["disabled"],
                citizen=child["citizen"],
                student=child["student"],
                earned=0,
                unearned=child["unearned"],
                # None is a parent who lives outside the simulation.
                parents=parents,
                away=child["away"],
                tax_unit=tax_unit,
                role="head" if tax_unit == f"child{position}" else "dependent",
                spouse=None,
                has_ids=child["has_ids"],
            )
        )
    # The grandparent is the mother's and the aunt's parent.
    if household["grandparent"]:
        for person in people:
            if person["name"] in (name("mother"), name("aunt")):
                person["parents"] = (name("grandparent"),)
    mode = household["ids"]
    for person in people:
        person["has_ids"] = bool(person["parents"]) and (
            mode == "all" or (mode == "some" and person["has_ids"])
        )
    return people


def _situation(households, reverse=False, child_rise=0, adult_rise=0):
    plurals = ("people", "tax_units", "households", "marital_units", "families")
    situation = {plural: {} for plural in plurals + ("spm_units",)}
    facts = {}
    for index, household in enumerate(households):
        people = _people(index, household)
        if reverse:
            people = people[::-1]
        state = "MO" if index % 2 else "DC"
        ids = {p["name"]: 1_000 * (index + 1) + n + 1 for n, p in enumerate(people)}
        home = {
            p["name"]: f"{p['name']}_away" if p["away"] else f"h{index}_home"
            for p in people
        }
        own_children = {}
        for person in people:
            for parent in person["parents"]:
                if parent and home[parent] == home[person["name"]]:
                    own_children[parent] = own_children.get(parent, 0) + 1
        for person in people:
            child = person["age"] < CHILD_AGE
            parent_ids = [
                ids.get(parent, ABSENT_PARENT_ID) if parent else ABSENT_PARENT_ID
                for parent in person["parents"]
            ]
            parent_ids = (parent_ids + [0, 0])[:2] if person["has_ids"] else [0, 0]
            reported = (
                own_children.get(person["name"], 0)
                if household["report_own_children"]
                else 0
            )
            rise = child_rise if child else adult_rise
            facts[person["name"]] = dict(
                person,
                household=index,
                home=home[person["name"]],
                state=state,
                tax_unit_key=f"h{index}_{person['tax_unit']}",
                reported_children=reported,
                person_id=ids[person["name"]],
                parent_ids=parent_ids,
                earned=person["earned"] + (rise if not child else 0),
                unearned=person["unearned"] + rise,
            )
            f = facts[person["name"]]
            situation["people"][person["name"]] = {
                "age": {YEAR: person["age"]},
                "is_ssi_disabled": {YEAR: person["disabled"]},
                "immigration_status": {
                    YEAR: "CITIZEN" if person["citizen"] else "UNDOCUMENTED"
                },
                "ssi_earned_income": {YEAR: 12 * f["earned"]},
                "ssi_unearned_income": {YEAR: 12 * f["unearned"]},
                "is_full_time_college_student": {YEAR: person["student"]},
                "is_in_k12_school": {YEAR: False},
                "person_id": {YEAR: ids[person["name"]]},
                "parent_1_id": {YEAR: parent_ids[0]},
                "parent_2_id": {YEAR: parent_ids[1]},
                "own_children_in_household": {YEAR: reported},
                "is_tax_unit_head": {YEAR: person["role"] == "head"},
                "is_tax_unit_spouse": {YEAR: person["role"] == "spouse"},
                "is_tax_unit_dependent": {YEAR: person["role"] == "dependent"},
            }
            couple = person["spouse"]
            units = {
                "tax_units": f["tax_unit_key"],
                "households": home[person["name"]],
                "marital_units": (
                    "_".join(sorted((person["name"], couple)))
                    if couple
                    else f"{person['name']}_mu"
                ),
            }
            units["families"] = units["households"]
            units["spm_units"] = units["households"]
            for plural, key in units.items():
                group = situation[plural].setdefault(key, {"members": []})
                group["members"].append(person["name"])
                if plural == "households":
                    group["state_code"] = {YEAR: state}
    return situation, facts


def _countable(earned, unearned):
    """416.1165(d)(1)-(2): the $20 and earned income exclusions, monthly."""
    general = min(GENERAL_EXCLUSION, unearned)
    earned_left = max(0, earned - EARNED_EXCLUSION - (GENERAL_EXCLUSION - general))
    return unearned - general + earned_left / 2


def _oracle(facts, medicaid=False):
    """Every person's outputs from true relationships and the id contract.

    medicaid gives the Medicaid copy: a disabled child need not meet the SSI
    immigration condition, a disabled child who shares the deemed income
    takes no allocation, and Missouri households follow DSS Manual
    0805.020.15 (natural or adoptive parents only, an allocation for every
    minor).
    """
    names = list(facts)

    def co_resident(a, b):
        return facts[a]["home"] == facts[b]["home"]

    def spouse(person):
        partner = facts[person]["spouse"]
        return partner if partner and co_resident(person, partner) else None

    def named_parents(person):
        """Parents an id names who live with the person."""
        if not facts[person]["has_ids"]:
            return set()
        return {
            parent
            for parent in facts[person]["parents"]
            if parent and co_resident(parent, person)
        }

    def household_linked(person):
        return any(
            facts[other]["has_ids"] for other in names if co_resident(other, person)
        )

    def unlinked(person):
        linked = sum(person in named_parents(other) for other in names)
        own = facts[person]["reported_children"]
        return (own > 0 or linked > 0) and (linked == 0 or own > linked)

    def eligible(person):
        """The SSI status conditions: aged, blind or disabled and a citizen."""
        return facts[person]["disabled"] and facts[person]["citizen"]

    def deemors(person, with_spouses):
        if facts[person]["has_ids"]:
            parents = named_parents(person)
            if with_spouses:
                parents |= {spouse(p) for p in parents if spouse(p)}
            return parents
        # The tax-unit proxy: every co-resident unlinked parent in the
        # person's tax unit, the person included, and each one's spouse.
        unit = facts[person]["tax_unit_key"]
        found = set()
        for member in names:
            if facts[member]["tax_unit_key"] != unit or not co_resident(member, person):
                continue
            partner = spouse(member)
            if unlinked(member) or (
                with_spouses and partner is not None and unlinked(partner)
            ):
                found.add(member)
                if with_spouses and partner is not None:
                    found.add(partner)
        return found

    def allocation(child):
        person = facts[child]
        is_child = person["age"] < CHILD_AGE or (
            person["age"] < STUDENT_AGE and person["student"]
        )
        if not is_child or eligible(child):
            return 0
        return max(0, MONTHLY_ALLOCATION - person["unearned"])

    def siblings(person, parents, every_minor):
        relatives = parents | {person}
        presume = not household_linked(person) or any(map(unlinked, relatives))
        # The parents' spouses who live elsewhere: their children at home
        # are still allocated (POMS SI 00501.010 B.2.d).
        absent = {
            facts[p]["spouse"]
            for p in parents
            if facts[p]["spouse"] and not co_resident(p, facts[p]["spouse"])
        }
        units = {facts[r]["tax_unit_key"] for r in relatives | absent}
        found = set()
        for other in names:
            if other == person or other in parents or not co_resident(other, person):
                continue
            if every_minor:
                counts = facts[other]["age"] < CHILD_AGE
            elif facts[other]["has_ids"]:
                counts = bool(named_parents(other) & relatives) or bool(
                    set(facts[other]["parents"]) & absent
                )
            else:
                counts = presume and facts[other]["tax_unit_key"] in units
            if counts:
                found.add(other)
        return found

    rows = {}
    for person in names:
        missouri = medicaid and facts[person]["state"] == "MO"
        parents = deemors(person, with_spouses=not missouri)
        ineligible = {p for p in parents if not eligible(p)}
        status = facts[person]["disabled"] if medicaid else eligible(person)
        applies = facts[person]["age"] < CHILD_AGE and status and bool(ineligible)
        rows[person] = dict(
            parents=frozenset(parents),
            ineligible=ineligible,
            applies=applies,
            missouri=missouri,
        )
    for person, row in rows.items():
        parents, ineligible = row["parents"], row["ineligible"]
        if not row["applies"]:
            row.update(child_allocations=0, parent_allocation=0, net=0)
            continue
        child_allocations = sum(
            allocation(s)
            for s in siblings(person, parents, every_minor=row["missouri"])
            if not (medicaid and rows[s]["applies"])
        )
        n = len(ineligible)
        parent_allocation = COUPLE * (n // 2) + INDIVIDUAL * (n % 2)
        unearned = sum(facts[p]["unearned"] for p in ineligible)
        earned = sum(facts[p]["earned"] for p in ineligible)
        left = max(0, child_allocations - unearned)
        net = max(
            0,
            _countable(max(0, earned - left), max(0, unearned - child_allocations))
            - parent_allocation,
        )
        row.update(
            child_allocations=child_allocations,
            parent_allocation=parent_allocation,
            net=net,
            gross=unearned + earned,
        )
    for person, row in rows.items():
        pool = [
            other
            for other, r in rows.items()
            if r["applies"]
            and r["parents"] == row["parents"]
            and facts[other]["household"] == facts[person]["household"]
        ]
        row["deemed"] = row["net"] / len(pool) if row["applies"] else 0
    for person in names:
        rows[person]["ineligible_parent"] = any(
            r["applies"] and person in r["ineligible"] for r in rows.values()
        )
    return rows


SSI_VARIABLES = (
    "is_ssi_income_deeming_child",
    "is_ssi_ineligible_parent",
    "ssi_parental_deeming_child_allocations",
    "ssi_parental_deeming_parent_allocation",
    "ssi_unearned_income_deemed_from_ineligible_parent",
)
MEDICAID = (
    "medicaid_optional_senior_or_disabled_unearned_income_deemed_from_ineligible_parent"
)


def _calculate(situation, variables):
    simulation = Simulation(situation=situation)
    names = list(situation["people"])
    return {
        variable: dict(zip(names, simulation.calculate(variable, YEAR)))
        for variable in variables
    }


def _close(a, b):
    return abs(float(a) - float(b)) <= TOLERANCE


@settings(max_examples=3, derandomize=True, deadline=None)
@given(BATCH)
def test_parental_deeming_matches_oracle_and_invariants(households):
    situation, facts = _situation(households)
    results = _calculate(situation, SSI_VARIABLES + (MEDICAID,))
    oracle = _oracle(facts)
    medicaid_oracle = _oracle(facts, medicaid=True)
    deemed = results["ssi_unearned_income_deemed_from_ineligible_parent"]

    for name, row in oracle.items():
        # 1. Differential against the oracle.
        assert results["is_ssi_income_deeming_child"][name] == row["applies"], name
        assert results["is_ssi_ineligible_parent"][name] == row["ineligible_parent"], (
            name
        )
        assert _close(
            results["ssi_parental_deeming_child_allocations"][name],
            12 * row["child_allocations"],
        ), name
        assert _close(
            results["ssi_parental_deeming_parent_allocation"][name],
            12 * row["parent_allocation"],
        ), name
        assert _close(deemed[name], 12 * row["deemed"]), name
        # 2. The Medicaid copy: Missouri's rules in Missouri, SSI's in DC,
        # where it equals SSI deeming whenever everyone at home is a citizen.
        assert _close(results[MEDICAID][name], 12 * medicaid_oracle[name]["deemed"]), (
            name
        )
        home = [n for n in facts if facts[n]["home"] == facts[name]["home"]]
        if facts[name]["state"] == "DC" and all(facts[n]["citizen"] for n in home):
            assert _close(results[MEDICAID][name], deemed[name]), name
        # 6. Bounds.
        assert deemed[name] >= 0
        if row["applies"]:
            assert deemed[name] <= 12 * row["gross"] + TOLERANCE

    # 3. Conservation: each set of parents' net income is deemed in full.
    pools = {}
    for name, row in oracle.items():
        if row["applies"]:
            key = (facts[name]["household"], row["parents"])
            pools.setdefault(key, []).append(name)
    for members in pools.values():
        total = sum(deemed[name] for name in members)
        assert _close(total, 12 * oracle[members[0]]["net"]), members

    # 4. Order of people.
    reversed_situation, _ = _situation(households, reverse=True)
    reversed_results = _calculate(reversed_situation, SSI_VARIABLES + (MEDICAID,))
    for variable, values in results.items():
        for name, value in values.items():
            assert _close(reversed_results[variable][name], value), (variable, name)

    # 5. More income for children (smaller allocations) or for adults never
    # lowers deemed income.
    for rise in (dict(child_rise=100), dict(adult_rise=100)):
        richer_situation, _ = _situation(households, **rise)
        richer = _calculate(
            richer_situation, ("ssi_unearned_income_deemed_from_ineligible_parent",)
        )["ssi_unearned_income_deemed_from_ineligible_parent"]
        assert all(richer[name] >= deemed[name] - TOLERANCE for name in deemed)
