shoplist = "shoplist.txt"
# Function to read the shopping list
def read_shoplist(filename=shoplist):
    try:
        with open(filename, "r") as f:
            items = [line.strip() for line in f if line.strip()]
        return items
    except FileNotFoundError:
        return []

# Function to write to the shopping list
def write_shoplist(items, filename=shoplist):
    with open(filename, "a") as f:
        for item in items:
            f.write(str(item).strip(" ") + "\n")

def remove_item(item, filename=shoplist):
    items = []
    with open(filename, "r") as f:
        items = [line.strip() for line in f if line.strip()]
        for i in items:
            if i == item:
                items.remove(i)

    with open(filename, "w") as f:
        for i in items:
            f.write(i + "\n")