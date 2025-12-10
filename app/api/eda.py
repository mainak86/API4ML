# app/api/eda.py

from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pathlib import Path
import shutil
import uuid
from datetime import datetime

from app.schemas import (
    EDAResponse, DatasetUploadResponse, 
    DatasetListResponse, DatasetListItem,
    ColumnRemovalRequest, ColumnRemovalResponse
)
from app.services.eda_service import EDAService
from app.api.auth import get_current_user
from app.schemas import UserWrapperResponse

router = APIRouter(prefix="/api/eda", tags=["eda"])

# Configuration
DATASET_DIR = Path("dataset")
DATASET_DIR.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".json", ".parquet"}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB


@router.post("/upload", response_model=DatasetUploadResponse)
async def upload_dataset(
    file: UploadFile = File(...),
    current_user: UserWrapperResponse = Depends(get_current_user),
) -> DatasetUploadResponse:
    """Upload a dataset file."""
    
    # Validate file extension
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Supported: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Generate unique filename
    unique_id = str(uuid.uuid4())[:8]
    filename = f"{unique_id}_{file.filename}"
    file_path = DATASET_DIR / filename
    
    # Save file
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_size = file_path.stat().st_size / 1024**2  # Convert to MB
        
        return DatasetUploadResponse(
            filename=filename,
            file_path=str(file_path),
            size_mb=file_size,
            uploaded_at=datetime.now(),
            message="File uploaded successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")


@router.get("/analyze/{filename}", response_model=EDAResponse)
async def analyze_dataset(
    filename: str,
    current_user: UserWrapperResponse = Depends(get_current_user),
) -> EDAResponse:
    """Perform EDA on uploaded dataset and return chart data."""
    
    file_path = DATASET_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    try:
        # Load dataset
        df = EDAService.load_dataset(file_path)
        
        # Get analysis results
        overview = EDAService.get_overview(df, filename)
        column_stats = EDAService.get_column_stats(df)
        chart_data = EDAService.get_all_chart_data(df)
        insights = EDAService.generate_insights(df)
        
        return EDAResponse(
            overview=overview,
            column_stats=column_stats,
            chart_data=chart_data,
            insights=insights
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/columns/{filename}")
async def get_column_info(
    filename: str,
    current_user: UserWrapperResponse = Depends(get_current_user),
):
    """Get detailed information about all columns in the dataset."""
    
    file_path = DATASET_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    try:
        column_info = EDAService.get_column_info(file_path)
        return column_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get column info: {str(e)}")


@router.post("/remove-columns", response_model=ColumnRemovalResponse)
async def remove_columns(
    request: ColumnRemovalRequest,
    current_user: UserWrapperResponse = Depends(get_current_user),
) -> ColumnRemovalResponse:
    """
    Remove specified columns from dataset and save as new file with _eda suffix.
    
    Args:
        request: Contains filename and list of columns to remove
        current_user: Authenticated user
        
    Returns:
        Information about the new dataset with removed columns
        
    Example request body:
        {
            "filename": "abc123_data.csv",
            "columns_to_remove": ["deal_id", "acquirer_name", "target_name"]
        }
    """
    
    file_path = DATASET_DIR / request.filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    if not request.columns_to_remove:
        raise HTTPException(status_code=400, detail="No columns specified for removal")
    
    try:
        # Remove columns and save new file
        new_filename, df_cleaned, removed_cols, remaining_cols = EDAService.remove_columns_and_save(
            file_path=file_path,
            columns_to_remove=request.columns_to_remove,
            output_dir=DATASET_DIR
        )
        
        new_file_path = DATASET_DIR / new_filename
        
        return ColumnRemovalResponse(
            original_filename=request.filename,
            new_filename=new_filename,
            original_columns=len(removed_cols) + len(remaining_cols),
            new_columns=len(remaining_cols),
            removed_columns=removed_cols,
            columns_remaining=remaining_cols,
            file_path=str(new_file_path),
            message=f"Successfully removed {len(removed_cols)} column(s) and saved as {new_filename}"
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove columns: {str(e)}")


@router.get("/datasets", response_model=DatasetListResponse)
async def list_datasets(
    current_user: UserWrapperResponse = Depends(get_current_user),
) -> DatasetListResponse:
    """List all uploaded datasets."""
    
    datasets = []
    for file_path in DATASET_DIR.glob("*"):
        if file_path.is_file():
            datasets.append(DatasetListItem(
                filename=file_path.name,
                size_mb=file_path.stat().st_size / 1024**2,
                uploaded_at=datetime.fromtimestamp(file_path.stat().st_mtime)
            ))
    
    # Sort by upload time, newest first
    datasets.sort(key=lambda x: x.uploaded_at, reverse=True)
    
    return DatasetListResponse(datasets=datasets, count=len(datasets))


@router.delete("/datasets/{filename}", status_code=204)
async def delete_dataset(
    filename: str,
    current_user: UserWrapperResponse = Depends(get_current_user),
):
    """Delete a dataset."""
    
    file_path = DATASET_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    try:
        file_path.unlink()
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")


@router.get("/preview/{filename}")
async def preview_dataset(
    filename: str,
    rows: int = 10,
    current_user: UserWrapperResponse = Depends(get_current_user),
):
    """Preview first N rows of dataset."""
    
    file_path = DATASET_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    try:
        df = EDAService.load_dataset(file_path)
        preview_data = df.head(rows).to_dict(orient='records')
        
        return {
            "filename": filename,
            "rows_shown": len(preview_data),
            "total_rows": len(df),
            "columns": df.columns.tolist(),
            "data": preview_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Preview failed: {str(e)}")