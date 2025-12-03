import libcore_hng.utils.app_core as app
from libcore_hng.utils.imageops import ImageOps, FontNotSetError
from libcore_hng.exceptions.file_exception import FontFileNotFoundError, ImageFileNotFoundError
from libcore_hng.core.base_config import BaseConfig

# アプリ初期化
app.init_app(BaseConfig, __file__, "logger.json")

try:
    # イメージクラスインスタンス
    iops = ImageOps()

    # イメージ読込
    image1 = iops.load_image('tests/data', '045_roland.png')
    image2 = iops.load_image('tests/data', '045_roland.png')

    # フォントセット
    image1.set_font('tests/data/font/アプリ明朝.otf', 14)
    image2.set_font('tests/data/font/アプリ明朝.otf', 16)

    # テキスト挿入
    image1.insert_text('俺か俺以外か', (10, 20))
    image2.insert_text('俺か俺以外か', (10, 20))

    # リサイズ
    path1 = image1.resize(300).save('tests/data/output','new_pic1.png')
    path2 = image1.resize(400).save('tests/data/output','new_pic2.png')

    # オリジナルイメージパス 
    print(iops.get_org_image_path())
    # 出力先パス  
    print(path1)
    print(path2)

except FontNotSetError as e:
    print(e)
except FontFileNotFoundError as e:
    print(e)
except ImageFileNotFoundError as e:
    print(e)
