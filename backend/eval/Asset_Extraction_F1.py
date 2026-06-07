from phoenix.evals import create_evaluator
@create_evaluator(
    name="asset-extraction-f1",
    kind="code",
    direction="maximize"
)
def asset_extraction_f1(output, expected):

    predicted_assets = set()

    for cat in output["categories"]:
        for asset in cat["assets"]:
            predicted_assets.add(
                asset["original_name"].lower()
            )

    truth_assets = set()

    for cat in expected["categories"]:
        for asset in cat["assets"]:
            truth_assets.add(
                asset["name"].lower()
            )

    tp = len(predicted_assets & truth_assets)

    precision = tp / len(predicted_assets) if predicted_assets else 0

    recall = tp / len(truth_assets) if truth_assets else 0

    if precision + recall == 0:
        return 0

    return 2 * precision * recall / (precision + recall)