import traceback

from app.services.db_service import save_ai_result_to_db
from app.models.schemas import (
AIProjectAnalysis,
MetadataSummary,
CategoryItem,
AssetItem
)

def test_save_real_data():
    try:
        print("=" * 60)
        print("START TEST")
        print("=" * 60)

        ai_data = AIProjectAnalysis(
            metadata_summary=MetadataSummary(
                total_assets=2,
                total_categories=1,
                insights="Test save database"
            ),
            ai_suggestions=[
                "Suggestion 1",
                "Suggestion 2"
            ],
            categories=[
                CategoryItem(
                    category_name="Khu kỹ thuật",
                    slug="khu-ky-thuat",
                    assets=[
                        AssetItem(
                            original_name="Bơm P101",
                            slug="bom-p101",
                            description="Máy bơm chính"
                        ),
                        AssetItem(
                            original_name="Tủ điện A1",
                            slug="tu-dien-a1",
                            description="Tủ điện điều khiển"
                        )
                    ]
                )
            ]
        )

        project_id = save_ai_result_to_db(
            project_name="TEST PROJECT",
            raw_text="Bơm P101 và Tủ điện A1",
            ai_data=ai_data
        )

        print()
        print("SUCCESS")
        print("PROJECT ID:", project_id)

        assert project_id is not None

    except Exception as e:
        print()
        print("ERROR OCCURRED")
        print(type(e).__name__)
        print(str(e))
        print()

        traceback.print_exc()

        raise
