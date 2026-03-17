from pydantic import BaseModel, Field

class GcpConfig(BaseModel):
    project_id: str = Field(default="", description="Google Cloud Project ID")
    secret_name: str = Field(default="", description="Google Cloud Secret Manager Secret Name")
