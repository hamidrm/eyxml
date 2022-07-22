
# eyxml
C XML Parser Library
**This repo is based on [Yxml project](https://dev.yorhel.nl/yxml) (By Yoran Heling)**
You can build a C XML parser according to 'format.xml' file by run 'parser_generator.py' file. To use the output C file, just create a  `eyxml_t` data structure and assign `on_error_cb` a value to handle errors and `xml_data` as a pointer to XML data.
After calling `eyxml_init`and next, calling `eyxml_parse`, eyxml will create a tree from XML data on the memory. At last, you can use `eyxml_next_child`, `eyxml_count_childs`, and `eyxml_get_child_at`to traverse the tree.
