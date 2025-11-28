
def exists_string(target_string:str, matching_string:list):
    
    """
    対象文字列にマッチング文字列リストの要素が含まれるか判定する

    Parameters
    ----------
    target_string : str
        対象文字列
    matching_string : list
        マッチング文字列リスト
    """
    
    # 文字列のマッチング
    for s in matching_string:
        result = s in target_string
        if result:
            break
    
    return result

def get_matched_string_list(target_string:str, matching_string:list):
    
    """
    対象文字列に対してマッチング文字列リストと一致した要素を返す

    Parameters
    ----------
    target_string : str
        対象文字列
    matching_string : list
        マッチング文字列リスト
    """
    
    result = []
    
    # 文字列のマッチング
    for s in matching_string:
        if s in target_string:
            result.append(s)
    
    return result
    