"""
Creates new list of films, shortened version of locations.list
"""
with open("locations.list", encoding="utf-8", errors="ignore") as file_to_read:
    with open("shortened.locations.list(1000 lines)", encoding="utf-8", mode="w") as file_to_write:
        i = 0
        for line in file_to_read:
            if i<1000:
                file_to_write.write(line)
                i+=1
            else:
                continue
