"""
Evaluation Pipeline cho AI Asset Organizer.

Chạy:  cd backend && .\venv\Scripts\python.exe eval\run_eval.py
"""

import os
import sys
import json
import time
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import phoenix as px
from dotenv import load_dotenv
from phoenix.evals import evaluate_dataframe, bind_evaluator

# Load biến môi trường từ file .env (quan trọng: GEMINI_API_KEY)
load_dotenv(Path(__file__).parent.parent / ".env")

from app.services.ai_service import generate_structured_assets

# Import tất cả evaluators
from eval.Asset_Count_Accuracy import asset_count_accuracy
from eval.Category_Count_Accuracy import category_count_accuracy
from eval.Asset_Extraction_F1 import asset_extraction_f1
from eval.Asset_Slug_Accuracy import asset_slug_accuracy
from eval.Category_Classification_Accuracy import category_classification
from eval.Category_Slug_Accuracy import category_slug_accuracy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_expected_safely(expected: dict) -> dict:
    """
    Chuẩn hóa expected JSON từ CSV.
    - expected có thể lưu asset dưới key "name" (golden data)
    - output từ Gemini lưu dưới key "original_name"
    Hàm này copy "name" → "original_name" để evaluator có thể mapping.
    """
    fixed = dict(expected)
    for cat in fixed.get("categories", []):
        for asset in cat.get("assets", []):
            # Golden data dùng "name", AI output dùng "original_name"
            if "name" in asset and "original_name" not in asset:
                asset["original_name"] = asset["name"]
    return fixed


def main():
    logger.info("=" * 60)
    logger.info("BẮT ĐẦU EVALUATION PIPELINE")
    logger.info("=" * 60)

    # 1. Load golden dataset
    csv_path = Path(__file__).parent / "golden_data.csv"
    df = pd.read_csv(csv_path)
    logger.info(f"Đã load {len(df)} test cases từ golden_data.csv")

    # 2. Parse JSON columns
    df["input"] = df["input_json"].apply(json.loads)
    df["expected_raw"] = df["expected_json"].apply(json.loads)
    # Chuẩn hóa expected → "name" → "original_name"
    df["expected"] = df["expected_raw"].apply(parse_expected_safely)

    # 3. Gọi Gemini cho từng test case
    outputs = []
    for idx, row in df.iterrows():
        inp = row["input"]
        logger.info(f"[{idx+1}/{len(df)}] Đang xử lý: {inp['project_name']}...")
        try:
            ai_result = generate_structured_assets(
                project_name=inp["project_name"],
                raw_text=inp["raw_text"]
            )
            # Pydantic object → dict
            output_dict = ai_result.model_dump()
            outputs.append(output_dict)
            logger.info(f"       ✅ Thành công: {output_dict['metadata_summary']['total_assets']} assets")
        except Exception as e:
            logger.error(f"       ❌ Lỗi: {str(e)}")
            outputs.append(None)  # Đánh dấu lỗi
        time.sleep(0.5)  # Tránh rate limit

    df["output"] = outputs

    # 4. Lọc bỏ các row bị lỗi
    df_clean = df.dropna(subset=["output"]).copy()
    logger.info(f"Có {len(df_clean)}/{len(df)} test cases xử lý thành công")

    if df_clean.empty:
        logger.error("Không có test case nào thành công! Dừng lại.")
        return

    # 5. Chạy tất cả evaluators
    logger.info("Đang chạy evaluators...")

    # Fix port conflict: Dùng port khác thay vì 4317 mặc định
    os.environ["PHOENIX_GRPC_PORT"] = "4318"

    session = px.launch_app()
    logger.info(f"Phoenix Dashboard: {session.url}")

    evaluator_list = [
        asset_count_accuracy,
        category_count_accuracy,
        asset_extraction_f1,
        asset_slug_accuracy,
        category_classification,
        category_slug_accuracy,
    ]

    # Bind từng evaluator để map cột "output" và "expected" trong DataFrame
    # vào tham số của hàm evaluator (output=..., expected=...)
    bound_evaluators = [
        bind_evaluator(evaluator=e, input_mapping={"output": "output", "expected": "expected"})
        for e in evaluator_list
    ]

    results_df = evaluate_dataframe(
        dataframe=df_clean,
        evaluators=bound_evaluators,
        exit_on_error=False,  # Không dừng nếu 1 evaluator lỗi
    )

    # 6. Tổng hợp kết quả
    print()
    logger.info("=" * 60)
    logger.info("KẾT QUẢ EVALUATION")
    logger.info("=" * 60)

    logger.debug(f"Sample column: {[c for c in results_df.columns if '_score' in c][:2]}")
    logger.debug(f"Sample value type: {type(results_df.iloc[0, -1])}")

    summary = {}
    for evaluator in evaluator_list:
        eval_name = evaluator.name
        score_col = f"{eval_name}_score"
        if score_col in results_df.columns:
            # Score là JSON string (VD: "{'name': '...', 'score': 1.0, ...}")
            # Parse string → dict → lấy 'score'
            def extract_score(val):
                if isinstance(val, (int, float)):
                    return float(val)
                if isinstance(val, dict):
                    return float(val.get("score", val.get("value", 0)))
                if isinstance(val, str):
                    try:
                        d = json.loads(val.replace("'", "\""))
                        return float(d.get("score", d.get("value", 0)))
                    except Exception:
                        pass
                return float(val)

            scores = results_df[score_col].apply(extract_score)
            mean_score = scores.mean()
            summary[eval_name] = mean_score
            logger.info(f"  {eval_name:<30s}: {mean_score:.3f}")
        else:
            logger.warning(f"  {eval_name:<30s}: ❌ Không tìm thấy cột '{score_col}'")

    # 7. Lưu kết quả
    result_csv = Path(__file__).parent / "results.csv"
    results_df.to_csv(result_csv, index=False)
    logger.info(f"Đã lưu kết quả chi tiết vào {result_csv}")

    print()
    logger.info("=" * 60)
    logger.info(f"HOÀN THÀNH! Dashboard: {session.url}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()