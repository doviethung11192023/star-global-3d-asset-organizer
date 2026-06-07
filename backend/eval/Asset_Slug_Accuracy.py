from phoenix.evals import create_evaluator
@create_evaluator(
    name="asset-slug-accuracy",
    kind="code",
    direction="maximize"
)
def asset_slug_accuracy(output, expected):

    total = 0
    correct = 0

    expected_map = {}

    for cat in expected["categories"]:
        for asset in cat["assets"]:
            expected_map[
                asset["name"].lower()
            ] = asset["expected_slug"]

    for cat in output["categories"]:
        for asset in cat["assets"]:

            total += 1

            name = asset["original_name"].lower()

            if (
                name in expected_map
                and asset["slug"] == expected_map[name]
            ):
                correct += 1

    return correct / total if total else 0