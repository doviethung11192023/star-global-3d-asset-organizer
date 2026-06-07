from phoenix.evals import create_evaluator
@create_evaluator(
    name="category-slug-accuracy",
    kind="code",
    direction="maximize"
)
def category_slug_accuracy(output, expected):

    expected_map = {
        c["category_name"]: c["expected_slug"]
        for c in expected["categories"]
    }

    total = 0
    correct = 0

    for category in output["categories"]:

        total += 1

        if (
            category["category_name"] in expected_map
            and category["slug"]
            == expected_map[category["category_name"]]
        ):
            correct += 1

    return correct / total if total else 0