"""
Creates new list of films, shortened version of locations.list
"""


def main():
    """
    Executes all module work.
    """
    with open("data/locations.list", encoding="utf-8", errors="ignore") as file_to_read:
        with open("data/shortened_and_processed_locations_list(3000 lines)", encoding="utf-8", mode="w") as file_to_write:
            i = 0
            file_to_write.write("name,year,addinfo,place\n")
            for line in file_to_read:
                if 0 <= i <= 13:
                    i+=1
                elif i <= 3013:
                    quote_pos1 = line.find('"')
                    quote_pos2 = line.find('"', quote_pos1 + 1)
                    brackets1_pos1 = line.find('(', quote_pos2 + 1)
                    brackets1_pos2 = line.find(')', brackets1_pos1 + 1)
                    brackets2_pos1 = line.find('{', brackets1_pos2 + 1)
                    brackets2_pos2 = line.find('}', brackets2_pos1 + 1)

                    if quote_pos1 == -1 or quote_pos2 == -1:
                        title = "NO DATA"
                    else:
                        title = line[quote_pos1+1: quote_pos2].replace(",", "")
                    if brackets1_pos1 == -1 or brackets1_pos2 == -1:
                        year = "NO DATA"
                    else:
                        year = line[brackets1_pos1 + 1: brackets1_pos2].replace(",", "").\
                            replace("/", "").replace("I", "").replace("?", "0")
                    if brackets2_pos1 == -1 or brackets2_pos2 == -1:
                        addinfo = "NO DATA"
                    else:
                        addinfo = line[brackets2_pos1 + 1: brackets2_pos2].replace(",", "")

                    line = line[max(quote_pos2+1, brackets1_pos2+1, brackets2_pos2+1):].strip(" \t\n")

                    brackets1_pos3 = line.find('(')
                    brackets1_pos4 = line.find(')')

                    if brackets1_pos3!=-1 and brackets1_pos4!=-1:
                        place = line[:brackets1_pos3].strip(" \t\n").replace(",", "")
                    else:
                        place = line.strip(" \t\n").replace(",", "")

                    file_to_write.write(title + "," + year + "," + addinfo + "," + place + "\n")
                    i+=1
                else:
                    continue


if __name__ == "__main__":
    main()
