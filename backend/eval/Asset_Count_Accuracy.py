from phoenix.evals import create_evaluator

@create_evaluator(
    name="asset-count-accuracy",
    kind="code",
    direction="maximize"
)
def asset_count_accuracy(output, expected):

    predicted = output["metadata_summary"]["total_assets"]
    ground_truth = expected["total_assets"]

    return float(predicted == ground_truth)