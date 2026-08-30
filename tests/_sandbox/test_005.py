from libcore_hng.utils.textops import exists_string, get_matched_string_list

matching_list = ['apple', 'banana', 'cherry']

if exists_string("1", matching_list):
    print("Match found")
else:
    print("No match")
    
matched_list = get_matched_string_list("1apple2", matching_list)
print(matched_list)
