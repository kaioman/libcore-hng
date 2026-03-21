from pydantic import Field
from libcore_hng.core.base_config_model import BaseConfigModel

class GcpConfig(BaseConfigModel):
    """
    Google Cloud Platform (GCP) サービスの設定モデル

    このモデルは、GCPと連携するための必要な設定パラメータを定義する。
    例えば、プロジェクトIDやSecret Managerのシークレット名など。
    """
    project_id: str = Field(default="", description="Google CloudのProjectID")
    """ Google Cloud プロジェクトID """

    secret_name: str = Field(default="", description="Google CloudのSecret Managerシークレット名")
    """ Google Cloud Secret Managerのシークレット名 """

    # Workload Identity Federation (WIF) 関連の設定
    wif_enabled: bool = Field(default=False, description="Workload Identity Federation を有効にするかどうか")
    """ Workload Identity Federation の有効化フラグ """
    
    project_number: str = Field(default="", description="Workload Identity Pool が属するプロジェクト番号")
    """ Workload Identity Pool が属するプロジェクト番号 """
    
    pool_id: str = Field(default="", description="Workload Identity Pool の ID")
    """ Workload Identity Pool ID """
    
    provider_id: str = Field(default="", description="Workload Identity Provider の ID")
    """ Workload Identity Provider ID """
    service_account_email: str = Field(default="", description="Impersonate するサービスアカウントのメールアドレス")
    """ Impersonate するサービスアカウントのメールアドレス """

    issuer: str = Field(default="", description="自前JWTのIssuer (発行者)")
    """ 自前JWTのIssuer (発行者) """

    app_env: str = Field(default="dev", description="アプリケーション環境 (dev, prdなど) Secret ManagerのSecret IDのサフィックスに使用")
    """ アプリケーション環境 (dev, prdなど) Secret ManagerのSecret IDのサフィックスに使用 """
    
    kid: str = Field(default="wif-key-01", description="Workload Identity FederationのJWT署名に使用するKey ID")
    """ Workload Identity FederationのJWT署名に使用するKey ID """

    sts_url: str = Field(default="https://sts.googleapis.com/v1/token", description="Security Token Service (STS) のエンドポイントURL")
    """ Security Token Service (STS) のエンドポイントURL """

    iam_credentials_url_base: str = Field(default="https://iamcredentials.googleapis.com", description="IAM Credentials API のベースURL")
    """ IAM Credentials API のベースURL """

    # STS token exchange data
    sts_grant_type: str = Field(default="urn:ietf:params:oauth:grant-type:token-exchange", description="STSトークン交換時のgrantType")
    """ STSトークン交換時のgrantType """

    sts_requested_token_type: str = Field(default="urn:ietf:params:oauth:token-type:access_token", description="STSトークン交換時にリクエストするトークンタイプ")
    """ STSトークン交換時にリクエストするトークンタイプ """

    sts_scope: str = Field(default="https://www.googleapis.com/auth/cloud-platform", description="STSトークン交換時のスコープ")
    """ STSトークン交換時のスコープ """

    sts_subject_token_type: str = Field(default="urn:ietf:params:oauth:token-type:jwt", description="STSトークン交換時のSubjectTokenタイプ")
    """ STSトークン交換時のSubjectTokenタイプ """

gcp_config: GcpConfig | None = None
""" GCP設定インスタンスを保持するグローバル変数 """
