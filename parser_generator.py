#! /usr/bin/python
import xml.etree.ElementTree as ET
import re

header_file_dic = {
     "<<<eyxml_buffsize>>>" : "",
     "<<<eyxml_tags_name_max_length>>>" : "",
     "<<<eyxml_tags_number>>>" : "",
     "<<<eyxml_attrs_name_max_length>>>" : "",
     "<<<eyxml_attrs_number>>>" : "",
     "<<<eyxml_attrs_list>>>" : "",
     "<<<eyxml_tags>>>" : "",
     "<<<eyxml_attrs>>>" : "",
     "<<<eyxml_enum_attrs_lists>>>" : "",
     "<<<eyxml_typedef_attrs_lists>>>" : "",
     "<<<eyxml_get_attr_prototype_fun>>>" : "",
}                    

c_file_dic = {
     "<<<eyxml_tags_str>>>" : "",
     "<<<eyxml_attrs_types_str>>>" : "",
     "<<<eyxml_attrs_str>>>" : "",
     "<<<eyxml_attrs_lists_str>>>" : "",
     "<<<eyxml_tags_rule_mat>>>" : "",
     "<<<eyxml_get_attr_def_fun>>>" : "",
     "<<<eyxml_malloc_fun>>>" : "",
     "<<<eyxml_free_fun>>>" : "",
     "<<<eyxml_set_attr_val_case>>>" : ""
}

attrs_list = {
}

tags_list = {
}

tree = ET.parse('format.xml')
root = tree.getroot()
out_file_name = root.tag
memory_tag = root.find('config/memory')
attrs_tag = root.find('attributes')
structure_tag = root.find('structure')

header_file_dic["<<<eyxml_buffsize>>>"] = "("+memory_tag.attrib["yxmlBufferSize"]+")"
header_file_dic["<<<eyxml_tags_name_max_length>>>"] = "("+memory_tag.attrib["max_tag_name_len"]+")"
header_file_dic["<<<eyxml_attrs_name_max_length>>>"] = "("+memory_tag.attrib["max_attr_name_len"]+")"
c_file_dic["<<<eyxml_malloc_fun>>>"] = memory_tag.attrib["malloc"]
c_file_dic["<<<eyxml_free_fun>>>"] = memory_tag.attrib["free"]



for x in attrs_tag:
     attrs_list[x.attrib["name"]] = x.attrib["values"]

header_file_dic["<<<eyxml_attrs_number>>>"] =  "("+str(len(attrs_list))+")"

for x in structure_tag:
     tags_list[x.attrib["name"]] = x.attrib["allowed_inner_tags"]

header_file_dic["<<<eyxml_tags_number>>>"] =  "("+str(len(tags_list))+")"

for x,y in attrs_list.items():
     if(y.find('|') != -1):
          attrs_list[x] = y.split("|")



for x,y in tags_list.items():
     if(y.find('|') != -1):
          tags_list[x] = y.split("|")
          

attrs_value_types_list = ""

for x,y in attrs_list.items():
     if isinstance(y, list):
          t = x.upper()
          t = t.replace("-", "_")
          attrs_value_types_list += "  EYXML_TYPE_LIST_" + t + ",\n"

header_file_dic["<<<eyxml_attrs_list>>>"] =  attrs_value_types_list

tags = ""
tags_str = ""
eyxml_tag_rule_mat = {}

for x,y in tags_list.items():
     t = x.upper()
     t = t.replace("-", "_")
     tags += "\tEYXML_TAG_" + t + ",\n"
     tags_str += "\t\"" + x.lower() + "\",\n"
     if isinstance(y, list):
          eyxml_tag_rule_mat[x] = "{"
          r = 0
          for z in tags_list.keys():
               r += 1
               eyxml_tag_rule_mat[x] += "1" if z in y else "0"
               eyxml_tag_rule_mat[x] += ", " if r != len(tags_list.keys()) else "}, "
     else:
          eyxml_tag_rule_mat[x] = "{"
          r = 0
          for z in tags_list.keys():
               r += 1
               eyxml_tag_rule_mat[x] += "1" if z == x else "0"
               eyxml_tag_rule_mat[x] += ", " if r != len(tags_list.keys()) else "}, "
               

eyxml_tag_rule_mat_val = ""
for x,y in eyxml_tag_rule_mat.items():
     eyxml_tag_rule_mat_val += y + "\n"

header_file_dic["<<<eyxml_tags>>>"] = tags
c_file_dic["<<<eyxml_tags_str>>>"] = tags_str
c_file_dic["<<<eyxml_tags_rule_mat>>>"] = eyxml_tag_rule_mat_val
attrs = ""
attrs_str = ""

for x in attrs_list:
     t = x.upper()
     t = t.replace("-", "_")
     attrs += "\tEYXML_ATTR_" + t + ",\n"
     attrs_str += "\t\"" + x.lower() + "\",\n"

header_file_dic["<<<eyxml_attrs>>>"] = attrs
c_file_dic["<<<eyxml_attrs_str>>>"] = attrs_str

attrs_enum_list = ""
typedefs_attrs = ""
attrs_get_fun_prototype = ""
attrs_get_fun_def = ""
attrs_lists_str = ""
attrs_types = ""
attrs_parser = ""

     
for x,y in attrs_list.items():
     if isinstance(y, list):
          attrs_enum_list += "typedef enum {\n"
          attrs_lists_str += "static const char * eyxml_attr_list_" + x.replace("-", "_").lower() + "_str[" + str(len(y)) + "] = {\n"
          for z in y:
               attrs_enum_list += "\tEYXML_ATTR_LIST_"+x.replace("-", "_").upper()+"_"+z.replace("-", "_").upper()+",\n"
               attrs_lists_str += "\t\"" + z.lower() + "\",\n"
          attrs_lists_str += "};\n\n";
          attrs_enum_list += "} EyxmlAttrList_" + x.replace("-", "_") +";\n"
          typedefs_attrs += "typedef EyxmlAttrList_" + x.replace("-", "_") + " * eyxml_LIST_" + x.replace("-", "_").upper() + "_ptr_t;\n"
          
          attrs_get_fun_prototype += "EYXML_GET_ATTR_PROTOTYPE_FUN(LIST_" + x.replace("-", "_").upper() + ");\n"
          attrs_get_fun_def += "EYXML_GET_ATTR_DEF_FUN(LIST_"+x.replace("-", "_").upper()+");\n"
          attrs_types += "\tEYXML_TYPE_LIST_" + x.upper().replace("-", "_") + ",\n"

          attrs_parser += "\tcase EYXML_TYPE_LIST_" + x.upper().replace("-", "_") + ":\n\t{\n\t\tuint32_t list_item_val = eyxml_get_attr(eyxml_context, eyxml_attr_list_"+x.replace("-", "_").lower()+"_str," + str(len(y)) + ", value);"
          attrs_parser += "\n\t\tif(list_item_val>"+str(len(y)-1)+")\n\t\t\treturn EYXML_STATUS_ERR;\n\t\tcurrent_attr->value.uint_v = list_item_val;\n\t}\n\tbreak;\n"
     else:
          attrs_types += "\tEYXML_TYPE_" + y.upper() + ",\n"

header_file_dic["<<<eyxml_enum_attrs_lists>>>"] = attrs_enum_list
header_file_dic["<<<eyxml_typedef_attrs_lists>>>"] = typedefs_attrs
header_file_dic["<<<eyxml_get_attr_prototype_fun>>>"] = attrs_get_fun_prototype
c_file_dic["<<<eyxml_attrs_lists_str>>>"] = attrs_lists_str
c_file_dic["<<<eyxml_attrs_types_str>>>"] = attrs_types
c_file_dic["<<<eyxml_get_attr_def_fun>>>"] = attrs_get_fun_def
c_file_dic["<<<eyxml_set_attr_val_case>>>"] = attrs_parser
with open("eyxml_parser_2_h", "r") as h_file:
    header_text = h_file.read()

with open("eyxml_parser_2_c", "r") as c_file:
    c_text = c_file.read()
    
for x,y in header_file_dic.items():
     header_text = header_text.replace(x,y)

for x,y in c_file_dic.items():
     c_text = c_text.replace(x,y)


f = open(out_file_name+"_parser.h", "w")
f.write(header_text)
f.close()

f = open(out_file_name+"_parser.c", "w")
f.write(c_text)
f.close()
