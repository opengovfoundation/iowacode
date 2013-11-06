#!/usr/bin/python
# Rostislav Tsiomenko
# Convert Iowa legal code into OpenGov XML format
import re
from os import listdir
from os.path import isfile, join

# Structure: Title > Subtitle > Chapter > Section
# Titles are in roman numerals, chapters are number + [letter]*
titles = 16
roman_numerals = {"I":1, "II":2, "III":3, "IV":4, "V":5, "VI":6, "VII":7,
                  "VIII":8, "IX":9, "X":10, "XI":11, "XII":12, "XIII":13,
                  "XIV":14, "XV":15, "XVI":16}

def roman_to_int(roman):
    return roman_numerals[roman]

def int_to_roman(number):
    for roman, integer in roman_numerals.iteritems():
        if integer == number:
            return roman

def parse_section(xml):
    # First, get inside the body tags
    section = re.search(r'<slim\:Body>(.*)</slim\:Body>', xml, re.DOTALL).group(1)
    # Now we need to separate the history subsection
    split = section.partition('<xhtml:div class="history">')
    content = split[0]
    history = split[2]
    # Now we need to strip XML tags from both. This should be improved as a lot of
    # semantic meaning is lost, but accounting for all possible tags is very long-winded.
    content = re.sub(r'<slim\:codeSection.*</slim\:Heading>', '', content, 0)
    # Identifiers are used for subsections but they do not enclose the actual subsection they
    # are numbering/lettering. Instead, the subsection is first wrapped in one or more subsection
    # types, and then labeled with an identifier. For now we will just convert these to text
    # and ignore the complex nesting.
    content = re.sub(r'<xhtml:span class="identifier">(?P<identifier>.*?)</xhtml:span>', ' \g<identifier>' + ": ", content, 0)
    content = re.sub(r'<.*?>', '', content, 0)
    history = re.sub(r'<.*?>', '', history, 0)
    # Return the content and history
    return [content, history]

def write_xml(title, title_name, subtitle, subtitle_name, chapter, chapter_name, section, section_name, text, history):
    filename = "../statedecoded-master/htdocs/admin/import-data/" + section + ".xml"
    orderby = section.partition('.')[2]
    law = open(filename, "w")
    law.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
    law.write("<law>\n")
    law.write("\t<structure>\n")
    law.write("\t\t<unit label=\"title\" identifier=\"" + str(title) + "\" order_by=\"" + str(title) + "\" level=\"1\">")
    law.write(title_name + "</unit>\n")
    law.write("\t\t<unit label=\"subtitle\" identifier=\"" + subtitle + "\" order_by=\"" + subtitle + "\" level=\"2\">")
    law.write(subtitle_name + "</unit>\n")
    law.write("\t\t<unit label=\"chapter\" identifier=\"" + chapter + "\" order_by=\"" + chapter + "\" level=\"3\">")
    law.write(chapter_name + "</unit>\n")
    law.write("\t</structure>\n")
    law.write("\t<section_number>" + section + "</section_number>\n")
    law.write("\t<catch_line>" + section_name + "</catch_line>\n")
    law.write("\t<order_by>" + orderby + "</order_by>\n")
    law.write("\t<text>")
    law.write(text)
    law.write("\n\t</text>\n")
    if history:
        law.write("\t<history>" + history + "</history>\n")
    law.write("</law>\n")
    law.close()

# Title level
for title in range(1, titles + 1):
    title_filename = "CodeTitle/" + int_to_roman(title) + ".xml"
    with open(title_filename, "r") as title_file:
        title_xml = title_file.read()
    # Get name of title
    title_name = re.search(r'<headnote>(.*)</headnote>', title_xml).group(1)
    title_name = title_name.lower().title()
    # print "\n------\nTitle number: " + str(title)
    # print "Title name: " + title_name
    # Subtitle level
    for match in re.compile(r'cms-name="(.*?)"').findall(title_xml)[1:]:
        subtitle_filename = "CodeSubTitle/" + match + ".xml"
        with open(subtitle_filename, "r") as subtitle_file:
            subtitle_xml = subtitle_file.read()
        subtitle_name = re.search(r'<headnote>(.*)</headnote>', subtitle_xml).group(1)
        subtitle_name = subtitle_name.lower().title()
        subtitle_number = match.partition('.')[2].partition('.xm')[0]
        # print "\tSubtitle number: " + match + " subtitle name: " + subtitle_name
        # Chapter level
        for match in re.compile(r'cms-name="(.*?)"').findall(subtitle_xml)[1:]:
            chapter_filename = "CodeChapter/" + match + ".xml"
            with open(chapter_filename, "r") as chapter_file:
                chapter_xml = chapter_file.read()
            chapter_name = re.search(r'class="headnote">(.*?)</', chapter_xml).group(1)
            # Remove some inner xhtml tags from chapter names
            chapter_name = re.sub(r'<xhtml\:span class="em-dash"/>', '-', chapter_name, 0)
            chapter_name = re.sub(r'<xhtml\:span class="blank-line"/>', ' ', chapter_name, 0)
            chapter_name = re.sub(r'<xhtml\:span class="new-line"/>', ' ', chapter_name, 0)
            chapter_name = chapter_name.lower().title()
            # print "\t\tChapter number: " + match + " chapter name: " + chapter_name
            # Now we have title > subtitle > chapter, so go into the chapter folder
            # and find all section documents under that chapter
            section_path = "CodeSection/" + match + "/"
            try:
                sections = [section for section in listdir(section_path) if isfile(join(section_path, section))]
                for section_filename in sections:
                    with open(section_path + section_filename, "r") as section_file:
                        section_xml = section_file.read()
                    section_number = section_filename.partition('.xm')[0]
                    try:
                        section_name = re.search(r'class="headnote">(.*?)</', section_xml).group(1)
                        section_name = section_name.lower().title()
                        # If we've gotten here, that means the chapter exists and the
                        # section isn't repealed nor reserved, so it's name and content exist.
                        section_parse = parse_section(section_xml)
                        section_content = section_parse[0]
                        section_history = section_parse[1]
                        write_xml(title, title_name, subtitle_number, subtitle_name,
                                  match, chapter_name, section_number, section_name,
                                  section_content, section_history)
                        # print "\n\n====================\n" + section_name
                        # print "\n\n====================\n" + section_content
                        # print "\nHistory********:\n\n" + section_history
                    except AttributeError:
                        print "Section warning: " + section_number + " is repealed or reserved."
            except OSError, e:
                print "Chapter warning: " + match + " is reserved and doesn't actually exist."
