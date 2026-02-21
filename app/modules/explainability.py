from typing import Dict, List


def generate_explainability(
    geometry_result: Dict,
    ndvi_result: Dict,
    landuse_result: Dict,
    crop_result: Dict,
    overlap_result: Dict,
    final_score: float,
    decision: str,
    contribution_breakdown: Dict
) -> Dict:

    explanation: List[str] = []

    # -------------------------------------------------
    # 1️⃣ Plot Existence
    # -------------------------------------------------
    plot_exists = geometry_result.get("valid", False)

    if plot_exists:
        explanation.append(
            "Your land boundary was successfully verified."
        )
    else:
        explanation.append(
            "There is an issue with the land boundary you submitted."
        )

    # -------------------------------------------------
    # 2️⃣ Agricultural Land Verification
    # -------------------------------------------------
    is_agricultural_land = landuse_result.get("land_score", 0) > 0.4

    if is_agricultural_land:
        explanation.append(
            "Satellite records confirm that this land is agricultural."
        )
    else:
        explanation.append(
            "Satellite data does not clearly classify this land as agricultural."
        )

    # -------------------------------------------------
    # 3️⃣ Vegetation Evidence
    # -------------------------------------------------
    if ndvi_result.get("agriculture_score", 0) > 0.3:
        explanation.append(
            "Recent satellite images show healthy crop growth on the land."
        )
    else:
        explanation.append(
            "Current satellite images show limited vegetation on the land!"
        )

    # -------------------------------------------------
    # 4️⃣ Crop Plausibility
    # -------------------------------------------------
    crop_plausible = crop_result.get("crop_score", 0) > 0.5

    if crop_plausible:
        explanation.append(
            "The local climate and conditions are suitable for the selected crop."
        )
    else:
        explanation.append(
            "The local climate may not be ideal for the selected crop."
        )

    # -------------------------------------------------
    # 5️⃣ Overlap / Fraud Check
    # -------------------------------------------------
    if overlap_result.get("overlap_score", 1) < 0.7:
        explanation.append(
            "There may be a boundary overlap with another registered plot."
        )
    else:
        explanation.append(
            "No boundary conflicts were detected with other registered plots."
        )

    # -------------------------------------------------
    # 6️⃣ Final Decision Message
    # -------------------------------------------------
    if decision == "PASS":
        explanation.append(
            "Your plot has been successfully validated."
        )
    elif decision == "REVIEW":
        explanation.append(
            "Your plot requires manual review before approval!."
        )
    else:
        explanation.append(
            "Your plot could not be approved based on current data."
        )

    return {
        "plot_exists": plot_exists,
        "is_agricultural_land": is_agricultural_land,
        "crop_plausible": crop_plausible,
        "confidence_score": final_score,
        "decision": decision,
        "explanation": explanation,
        "contribution_breakdown": contribution_breakdown
    }