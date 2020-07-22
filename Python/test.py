# def user_input():
#     info_check = str(input("Is the information above correct? (y/n)  ")).lower().strip()
#     if info_check == "y":
#         print ("Information will shortly pushed to SharePoint. Thank you for using ASEULA!")
#     elif info_check == "n":
#         print ("\n")
#         print (*fields, sep= ", ")
#         field_correction = input("\nWhich of the fields information needs to be corrected?  ").lower().strip()
#         print ('-' * 10)
#         incorrect_data = field_dict[field_correction]
#         print (*incorrect_data, sep=", ")
#         user_selection = input("\nwhich value is correct?  ")
#         index_element = incorrect_data.index(user_selection)
#         selected_dict[field_correction] = incorrect_data[index_element]
#     else:
#         print('Invalid input. Please try again.')
#         return user_input()



# fields = ["Url", "Software name", "Organization"]
# stripped_url = ["a", "b", "c"]
# stripped_software = ["d", "e", "f"]
# stripped_org = ["g", "h", "i"]

# selected_dict = {"url": stripped_url[1], "software name": stripped_software[2], "org": stripped_org[0]}
# field_dict = {"url": stripped_url, "software name": stripped_software, "org": stripped_org}


# print ("old: " + selected_dict["software name"])
# user_input()
# print ("new: " + selected_dict["software name"])

# test = int(input("type something: "))
# test_type = type(test)

# if test_type == int:
#     print ("this is a int")
# elif test_type == str:
#     print ("this is a string")

test = input("type something: ")
test_type2 = int(test)
if type(test_type2) == int:
    print ("this is a int")
elif type(test_type2) == str:
    print ("this is a string")