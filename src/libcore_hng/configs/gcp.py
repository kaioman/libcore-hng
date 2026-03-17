from pydantic import Field
from libcore_hng.core.base_config_model import BaseConfigModel

class GcpConfig(BaseConfigModel):
    """
    Google Cloud Platform (GCP) サービスの設定モデル

    このモデルは、GCPと連携するための必要な設定パラメータを定義する。
    例えば、プロジェクトIDやSecret Managerのシークレット名など。
    """
    
    project_id: str = Field(default="", description="Google Cloud Project ID")
    """ Google Cloud プロジェクトID """

    secret_name: str = Field(default="", description="Google Cloud Secret Manager Secret Name")
    """ Google Cloud Secret Managerのシークレット名 """
