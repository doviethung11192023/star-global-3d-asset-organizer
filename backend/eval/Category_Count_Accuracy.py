from phoenix.evals import create_evaluator
@create_evaluator(
    name="category-count-accuracy",
    kind="code",
    direction="maximize"
)
def category_count_accuracy(output, expected):

    predicted = len(output["categories"])
    ground_truth = expected["total_categories"]

    return float(predicted == ground_truth)