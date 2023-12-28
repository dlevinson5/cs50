import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """

    def inherited_from(parent):
        """
        Every child inherits one copy of the GJB2 gene from each of their parents.
        - If a parent has two copies of the mutated gene, then they will pass the mutated gene on to the child;
        - if a parent has no copies of the mutated gene, then they will not pass the mutated gene on to the child;
        - and if a parent has one copy of the mutated gene, then the gene is passed on to the child with probability 0.5.
        After a gene is passed on, though, it has some probability of undergoing additional mutation: changing from a
        version of the gene that causes hearing impairment to a version that doesn’t, or vice versa.

        Finally, PROBS["mutation"] is the probability that a gene mutates from being the gene in question to not being
        that gene, and vice versa. If a mother has two versions of the gene, for example, and therefore passes one on
        to her child, there’s a 1% chance it mutates into not being the target gene anymore. Conversely, if a mother
        has no versions of the gene, and therefore does not pass it onto her child, there’s a 1% chance it mutates into
        being the target gene. It’s therefore possible that even if neither parent has any copies of the gene in
        question, their child might have 1 or even 2 copies of the gene.
        """

        if parent in one_gene:
            return 0.5
        elif parent in two_genes:
            return 1 - PROBS["mutation"]  # not mutated
        else:
            return PROBS["mutation"]  # mutated

    result = 1

    for person, data in people.items():

        genes = 2 if person in two_genes else 1 if person in one_gene else 0
        trait = person in have_trait
        mother = data['mother']
        father = data['father']

        # For anyone with parents in the data set, each parent will pass one of their two genes on to their child
        # randomly, and there is a PROBS["mutation"] chance that it mutates (goes from being the gene to not being
        # the gene, or vice versa).
        if mother and father:

            probability_from_mother = inherited_from(data['mother'])
            probability_from_father = inherited_from(data['father'])
            # P(!a) = 1 - P(a)
            probability_not_from_father = 1 - probability_from_father
            probability_not_from_mother = 1 - probability_from_mother

            match genes:
                case 2:
                    # Marginalization P(a, b) = P(a) * P(b)
                    probability_parents = probability_from_mother * probability_from_father
                case 1:
                    # Marginalization P(a) = P(a, !b) + P(a!, b)
                    probability_parents = ((probability_from_father * probability_not_from_mother) +
                                           (probability_from_mother * probability_not_from_father))
                case _:
                    # Marginalization P(!a, !b) = P(!a) * P(!b)
                    probability_parents = probability_not_from_father * probability_not_from_mother

            probability = probability_parents * PROBS['trait'][genes][trait]

        # For anyone with no parents listed in the data set, use the probability distribution PROBS["gene"] to
        # determine the probability that they have a particular number of the gene.
        else:

            probability = PROBS['gene'][genes] * PROBS['trait'][genes][trait]

        result *= probability

    return result


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """

    for person, data in probabilities.items():
        genes = 2 if person in two_genes else 1 if person in one_gene else 0
        trait = person in have_trait
        data['gene'][genes] += p
        data['trait'][trait] += p

    return


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """

    for person, data in probabilities.items():

        genes_sum = sum(data['gene'].values())
        trait_sum = sum(data['trait'].values())

        for key in data['gene']:
            value = data['gene'][key]
            data['gene'][key] = value / genes_sum

        for key in data['trait']:
            value = data['trait'][key]
            data['trait'][key] = value / trait_sum

    return


if __name__ == "__main__":
    main()
