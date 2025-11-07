import csv
import itertools
import sys

# PROBS is a dictionary containing a number of constants representing probabilities of various different events.
PROBS = {

    # Unconditional probabilities for having gene (if we know nothing about that person’s parents)
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    # conditional probability that a person exhibits a trait (like hearing impairment).
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

    # Mutation probability ( probability that a gene mutates from being the gene in question to not being that gene, and vice versa)
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1]) # stores the data from the csv file in a dictionary

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
    names = set(people) # dictionary with the names of the family
    for have_trait in powerset(names): # dictionary for people who have the trait

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
    probability = 1 # este valor ira cambiando segun evaluamos las personas

    for person in people:

        # 1) check el numero de copias del gen que tiene cada persona
        if person in one_gene:
            genes = 1
        elif person in two_genes:
            genes = 2
        else:
            genes = 0

        # 2) check si la persona tiene el trait
        has_trait = False

        if person in have_trait:
            has_trait = True
        # else:
            # ya esta implementado al inicializar la variable como false

        # 3) calcular la probabilidad de tener el trait
        trait_prob = PROBS["trait"][genes][has_trait]

        # if no parents
        mom = people[person]["mother"]
        father = people[person]["father"]

        if not mom or not father:
            gene_prob = PROBS["gene"][genes]

        # if person has parents
        else:
            def pass_prob(parent):
                #prob that parent passes the gene
                if parent in two_genes:
                    return 1 - PROBS["mutation"]
                elif parent in one_gene:
                    return 0.5
                else:
                    return PROBS["mutation"]

            # prob of passing from each parent
            mom_prob = pass_prob(mom)
            father_prob = pass_prob(father)

            if genes == 2: # both parents can pass
                gene_prob = mom_prob * father_prob
            
            elif genes == 1: # it is either from the mom or dad
                gene_prob = mom_prob * (1 - father_prob) + father_prob * (1 - mom_prob)
            
            else: # neither of the parents can pass
                gene_prob = (1 - mom_prob) * (1 - father_prob)

        #update joint prob
        probability *= gene_prob * trait_prob

    return probability

def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        # update gene probability
        if person in one_gene:
            probabilities[person]["gene"][1] += p
        elif person in two_genes:
            probabilities[person]["gene"][2] += p
        else:
            probabilities[person]["gene"][0] += p

        # update trait probability
        if person in have_trait:
            probabilities[person]["trait"][True] += p
        else: 
            probabilities[person]["trait"][False] += p

def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        #normalize gene probability
        total_genes = sum(probabilities[person]["gene"].values())
        for gene in probabilities[person]["gene"]:
            probabilities[person]["gene"][gene] /= total_genes # aqui estamos dividiendo cada probabilidad del gen entre el numero total de genes para normalizar

        #normalize trait probability
        total_traits = sum(probabilities[person]["trait"].values())
        for gene in probabilities[person]["trait"]:
            probabilities[person]["trait"][gene] /= total_traits


if __name__ == "__main__":
    main()
