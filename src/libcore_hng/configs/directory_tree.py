from pydantic import Field
from libcore_hng.core.base_config_model import BaseConfigModel

class TreeBorderStyleConfig(BaseConfigModel):
    """
    ツリーの罫線スタイルを定義する設定クラス
    """
    branch: str = "├── "
    """ 枝の罫線スタイル """
    last: str = "└── "
    """ 最後の枝の罫線スタイル """
    vertical: str = "│   "
    """ 垂直の罫線スタイル """
    blank: str = "    "
    """ 空白の罫線スタイル """

class TreeBorderPresetConfig(BaseConfigModel):
    """
    ツリーの罫線スタイルのプリセットを定義する設定クラス
    """
    normal: TreeBorderStyleConfig = Field(default_factory=TreeBorderStyleConfig)
    """ 通常の罫線スタイル """
    stylish: TreeBorderStyleConfig = Field(
        default_factory=lambda: TreeBorderStyleConfig(
            branch="┣━━ ",
            last="┗━━ ",
            vertical="┃   ",
            blank="    ",
        )
    )
    """ スタイリッシュな罫線スタイル """

class DirectoryTreeConfig(BaseConfigModel):
    """
    ディレクトリ構成をツリーまたはExcel向けTSVで出力するための設定クラス
    """

    borders: TreeBorderPresetConfig = Field(default_factory=TreeBorderPresetConfig)
    """ ツリーの罫線スタイルのプリセット """
