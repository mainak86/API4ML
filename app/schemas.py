"""Pydantic schemas for API request/response."""
from sqlmodel import SQLModel, Field
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class MarkdownFormat(SQLModel):
    """Markdown format metadata"""

    is_markdown: bool = False
    confidence: float = 0.0
    has_code: bool = False
    has_links: bool = False
    has_lists: bool = False
    sections: List[Dict[str, Any]] = Field(default_factory=list)


class MessageRead(SQLModel):
    """Message response model"""

    id: Optional[int] = None
    content: str
    sender: str
    timestamp: str
    file_url: Optional[str] = None
    file_name: Optional[str] = None
    format: Optional[MarkdownFormat] = None
    display_as_markdown: Optional[bool] = False


class MessageCreate(SQLModel):
    """Message creation model"""

    content: str
    sender: str
    timestamp: Optional[str] = None
    file_url: Optional[str] = None
    file_name: Optional[str] = None


class ChatSessionRead(SQLModel):
    """Chat session response model"""

    id: str
    title: str
    created_at: str
    messages: List[MessageRead] = []


# Authentication Schemas


class UserRegister(SQLModel):
    """User registration request"""

    username: str = Field(min_length=3, max_length=50, description="Username")
    email: str = Field(description="Email address")
    firstname: str = Field(min_length=1, max_length=100, description="First Name")
    lastname: str = Field(min_length=1, max_length=100, description="Last Name")
    password: str = Field(min_length=8, description="Password (min 8 characters)")
    user_role: Optional[str] = Field(default="user", description="User Role")


class UserLogin(SQLModel):
    """User login request"""

    username: str = Field(description="Username")
    password: str = Field(description="Password")



class UserUpdate(SQLModel):
    """User update request"""

    firstname: Optional[str] = Field(default=None, min_length=1, max_length=100, description="First Name")
    lastname: Optional[str] = Field(default=None, min_length=1, max_length=100, description="Last Name")
    email: Optional[str] = Field(default=None, description="Email address")
    password: Optional[str] = Field(default=None, min_length=8, description="Password (min 8 characters)")
    user_role: Optional[str] = Field(default=None, description="User Role")
    is_active: Optional[bool] = Field(default=None, description="Is Active")
    locked: Optional[bool] = Field(default=None, description="Is Locked")


class UserRead(SQLModel):
    """User response model (without password)"""

    id: Optional[int] = None
    username: str
    email: str
    firstname: str
    lastname: str
    user_role: str
    created_at: str
    is_active: bool = True
    locked: bool = False
    failed_login_attempts: int = 0


class UserWrapperResponse(SQLModel):
    """Wrapped user response"""
    user: UserRead


class TokenResponse(SQLModel):
    """JWT token response"""

    access_token: str
    token_type: str = "bearer"
    user: UserRead


# EDA Schemas
class ColumnStats(BaseModel):
    column_name: str
    data_type: str
    missing_count: int
    missing_percentage: float
    unique_count: int
    
    # Numerical stats
    mean: Optional[float] = None
    median: Optional[float] = None
    std: Optional[float] = None
    min: Optional[float] = None
    max: Optional[float] = None
    q25: Optional[float] = None
    q75: Optional[float] = None
    
    # Categorical stats
    top_values: Optional[Dict[str, int]] = None
    mode: Optional[Any] = None

class DatasetOverview(BaseModel):
    filename: str
    total_rows: int
    total_columns: int
    memory_usage_mb: float
    duplicate_rows: int
    columns: List[str]
    dtypes: Dict[str, str]

class HistogramData(BaseModel):
    column: str
    bins: List[float]
    counts: List[int]
    mean: float
    median: float
    std: float

class BoxPlotData(BaseModel):
    column: str
    min: float
    q1: float
    median: float
    q3: float
    max: float
    outliers: List[float]

class BarChartData(BaseModel):
    column: str
    categories: List[str]
    counts: List[int]
    percentages: List[float]

class CorrelationMatrix(BaseModel):
    columns: List[str]
    matrix: List[List[float]]
    high_correlations: List[Dict[str, Any]]

class MissingDataMatrix(BaseModel):
    columns: List[str]
    missing_counts: List[int]
    missing_percentages: List[float]
    total_rows: int

class ScatterPlotData(BaseModel):
    x_column: str
    y_column: str
    data_points: List[Dict[str, float]]
    correlation: float

class ChartDataCollection(BaseModel):
    histograms: List[HistogramData]
    box_plots: List[BoxPlotData]
    bar_charts: List[BarChartData]
    correlation_matrix: Optional[CorrelationMatrix] = None
    missing_data: MissingDataMatrix
    scatter_plots: List[ScatterPlotData]

class EDAResponse(BaseModel):
    overview: DatasetOverview
    column_stats: List[ColumnStats]
    chart_data: ChartDataCollection
    insights: List[str]

class DatasetUploadResponse(BaseModel):
    filename: str
    file_path: str
    size_mb: float
    uploaded_at: datetime
    message: str

class DatasetListItem(BaseModel):
    filename: str
    size_mb: float
    uploaded_at: datetime

class DatasetListResponse(BaseModel):
    datasets: List[DatasetListItem]
    count: int

class ColumnRemovalRequest(BaseModel):
    filename: str
    columns_to_remove: List[str]

class ColumnRemovalResponse(BaseModel):
    original_filename: str
    new_filename: str
    original_columns: int
    new_columns: int
    removed_columns: List[str]
    columns_remaining: List[str]
    file_path: str
    message: str