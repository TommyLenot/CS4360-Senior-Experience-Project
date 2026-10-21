
import math


def convert_model_outputs(
    anomaly_scores,
    predictions,
    actual_labels=None,
    dataset="NSL-KDD",
):
    """Convert model outputs into ingestion-ready detection records."""

    scores = list(anomaly_scores)
    predicted = list(predictions)

    if len(scores) != len(predicted):
        raise ValueError(
            "Anomaly scores and predictions must have the same length."
        )

    if actual_labels is not None:
        labels = list(actual_labels)

        if len(labels) != len(scores):
            raise ValueError(
                "Actual labels must match the number of scores."
            )
    else:
        labels = None

    results = []

    for index, (score, prediction) in enumerate(
        zip(scores, predicted)
    ):
        score = float(score)
        prediction = int(prediction)

        if not math.isfinite(score):
            raise ValueError(
                f"Anomaly score at record {index} must be finite."
            )

        if prediction not in (0, 1):
            raise ValueError(
                f"Prediction at record {index} must be 0 or 1."
            )

        result = {
            "dataset": dataset,
            "record_index": index,
            "anomaly_score": score,
            "model_prediction": prediction,
        }

        if labels is not None:
            label = int(labels[index])

            if label not in (0, 1):
                raise ValueError(
                    f"Actual label at record {index} must be 0 or 1."
                )

            result["actual_label"] = label

        results.append(result)

    return results
