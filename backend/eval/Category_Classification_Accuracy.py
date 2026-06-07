from phoenix.evals import create_evaluator
@create_evaluator(
    name="category-classification",
    kind="code",
    direction="maximize"
)
def category_classification(output, expected):

    predicted = {
        c["category_name"].lower()
        for c in output["categories"]
    }

    truth = {
        c["category_name"].lower()
        for c in expected["categories"]
    }

    intersection = predicted.intersection(truth)

    return len(intersection) / len(truth)