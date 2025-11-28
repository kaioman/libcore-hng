from decimal import Decimal, ROUND_FLOOR, ROUND_HALF_UP, ROUND_CEILING, ROUND_DOWN
from enum import Enum

class Fraction(Enum):
    """
    端数調整方法
    """
    
    FLOOR = ROUND_FLOOR
    """ 切り捨て """

    HALF_UP = ROUND_HALF_UP
    """ 四捨五入 """

    CEILING = ROUND_CEILING
    """ 切り上げ """
    
    ROUND_DOWN = ROUND_DOWN
    """ ゼロ方向切り捨て """

def roundx(val, f:Fraction, digits = 0):
    """
    指定された端数処理で数値を丸める関数

    Parameters
    ----------
    val : float | int | str
        丸め対象の値
    f : Fraction
        端数処理の種類 (切り捨て/四捨五入/切り上げ)
    digits : int, optional
        丸める桁数 (0=整数, 正=小数点以下, 負=10の位以上)
    """

    # 浮動小数点誤差の回避のためDecimal型に変換
    ret_val = Decimal(str(val))
    
    # 丸め対象のフォーマット文字列を生成
    if digits > 0:
        quantize_str = '1.' + '0' * digits     # 例: digits=2 -> '1.00'
    elif digits < 0:
        quantize_str = f"1E{-digits}"          # 例: digits=-2 -> '1E2' -> 100単位
    else:
        quantize_str = '1'                     # 整数丸め
    
    # 丸め処理を実行して戻り値として返す
    result_val = ret_val.quantize(Decimal(quantize_str), rounding=f.value)

    # digits < 0の場合、int型に変換⇒Decimal型に戻す
    if digits < 0:
        return Decimal(str(int(result_val)))
    else:
        return result_val