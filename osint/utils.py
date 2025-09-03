from tabulate import tabulate

def print_table(title, data):
    """
    Print data as a table.
    title: string for the table header
    data: list of (key, value) tuples
    """
    print(f"\n=== {title} ===")
    print(tabulate(data, headers=["Field", "Value"], tablefmt="grid"))
