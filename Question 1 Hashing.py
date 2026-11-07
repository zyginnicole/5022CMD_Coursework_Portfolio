"""
5022CMD Advanced Algorithms - Portfolio
Question 1: Hashing (Open Addressing with Linear Probing)
"""
import math
import random
import time

# Part 1: Hash table

"""
Bucket class represents a slot in the hash table where it
holds a key, a value and a state flag (empty, occupied or deleted)

State flags are required to handle deletion in open addressing so that it
does not break the probe chain.   
"""


class bucket:

    empty = 0 # search stops
    occupied = 1 # holds a value
    deleted = 3 # tombstone marker

    def __init__(self):
        self.key = None
        self.value = None
        self.state = bucket.empty


class HashTable:
    # Hash table using linear probing

    max_load = 0.7 # resize table when 70% of slots are used (shorter probes)
    table_size = 11

    def __init__(self, table_size):
        self.size = table_size
        self.buckets = [bucket() for _ in range(self.size)]
        self.count = 0
        self.tombstone = 0

    # perform hashing
    def hash_func(self, key):
        # Perform hashing for numbers
        if isinstance(key,int):
            return key % self.size

        # Polynomial rolling hash for strings: h = h*31 + ascii(char).
        # Unlike a plain ASCII sum, this gives different results for
        # anagrams (e.g. "AB12" vs "21BA"), which reduces collisions.
        h=0
        for c in str(key):
            h = h * 31 + ord(c)
        return h % self.size

    # Insert function
    def insert(self, key, value):
        # Returns the number of probes on success
        # else returns -1 if the key already exists
        if self.findIndex(key)[0] != -1:
            return -1

        # Resize first if the table is getting crowded.
        # Tombstones count, because they also lengthen probe sequences.
        if (self.count + self.tombstone + 1) / self.size > self.max_load:
            self.resize()

        index = self.hash_func(key)
        # number of occupied buckets moved past (0 = went straight into home slot)
        probes = 0

        # Linear probing
        while self.buckets[index].state == bucket.occupied:
            index = (index + 1) % self.size
            probes += 1

        # Reusing tombstone
        if self.buckets[index].state == bucket.deleted:
            self.tombstone -= 1

        slot = self.buckets[index]
        slot.key, slot.value, slot.state = key, value, bucket.occupied
        self.count += 1
        return probes

    # search functions: finding index
    def findIndex(self, key):
        # Returns a tuple (slot index, probes used) for a key
        # index is -1 if the key is not found
        index = self.hash_func(key)
        probes = 0

        for i in range(self.size):
            slot = self.buckets[index]
            if slot.state == bucket.empty:
                return -1, probes

            if slot.state == bucket.occupied and slot.key == key:
                return index, probes

            index = (index + 1) % self.size
            probes += 1
        # scanned whole table
        return -1, probes

    # search function: returns values
    def search(self, key):
        # Returns a tuple (value, index, probes)
        # value is None if the key is not found
        index, probes = self.findIndex(key)
        value = self.buckets[index].value if index != -1 else None
        return value, index, probes

    # update function
    def update(self, key, newValue):
        # Replace the value of an existing key
        # Returns true if found = updated
        # _ means ignore the probes
        index, _ = self.findIndex(key)
        if index == -1:
            return False
        self.buckets[index].value = newValue
        return True

    # delete function
    def delete(self, key):
        # Find key by probing, then clear its slot
        # and mark it as a tombstone
        index, _ = self.findIndex(key)
        if index == -1:
            return False
        slot = self.buckets[index]
        slot.key, slot.value, slot.state = None, None, bucket.deleted
        self.count -= 1
        self.tombstone += 1
        return True

    def resize(self):
        """Increase table size by multiplying 2
         then find the next prime number
        and re-insert all live pairs.

        Re-hashing is required because the home index depends on the
        table size. It also clears all tombstones.
        """
        old_buckets = self.buckets
        self.size = self._next_prime(self.size * 2)
        self.buckets = [bucket() for _ in range(self.size)]
        self.count = 0
        self.tombstone = 0

        # re-insertion
        for b in old_buckets:
            if b.state == bucket.occupied:
                self.insert(b.key, b.value)

    @staticmethod
    def is_prime(num):
        if num < 2:
            return False

        for d in range(2, int(math.sqrt(num)) + 1):
            if num % d == 0:
                return False
        return True

    @staticmethod
    def _next_prime(num):
        while not HashTable.is_prime(num):
            num += 1
        return num

    # display
    def load_factor(self):
        return self.count / self.size

    def display(self):
        """Print every slot so the layout and collisions are visible."""
        print(f"\nHash Table (size={self.size}, items={self.count}, "
              f"load factor={self.load_factor():.2f})")
        print("-" * 60)
        for i, slot in enumerate(self.buckets):
            if slot.state == bucket.empty:
                print(f"Slot {i:>3}: [EMPTY]")
            elif slot.state == bucket.deleted:
                print(f"Slot {i:>3}: [DELETED]")
            else:
                home = self.hash_func(slot.key)
                note = "" if home == i else f"  (collision: home slot {home})"
                print(f"Slot {i:>3}: {slot.key} -> {slot.value.productName}{note}")
        print("-" * 60)

# PART 2: ENTITY CLASS - PHARMACY PRODUCT

class Medicine:
    def __init__(self, productID, productName, category, price, qty,
                 expiryDate, requiresPrescription = False):
        self.productID = productID
        self.productName = productName
        self.category = category
        self.price = price
        self.qty = qty
        self.expiryDate = expiryDate
        self.requiresPrescription = requiresPrescription

    # special function, overwrite it
    # makes it print the actual data when called
    def __str__(self):
        pres = "Yes" if self.requiresPrescription else "No"

        return (f"ID: {self.productID} | {self.productName} | {self.category} | "
                f"RM{self.price:.2f} | Qty: {self.qty} | "
                f"Expiry: {self.expiryDate} | Prescription: {pres}")

# PART 3: PHARMACY INVENTORY SYSTEM (local storage + command-line menu)
class PharmacyInventory:
    # Local storage system
    def __init__(self, table_size=11):
        self.table = HashTable(table_size)
        self.loadSampleData()

    def loadSampleData(self):
        """Insert pre-defined records (Req #2). Data kept in one list so
                the same records can be reused for the array comparison."""
        self.sample_data = [
            Medicine("MED001", "Paracetamol 500mg", "Painkiller", 5.50, 120, "2027-06-30"),
            Medicine("MED002", "Ibuprofen 400mg", "Painkiller", 8.90, 80, "2027-03-15"),
            Medicine("MED003", "Amoxicillin 250mg", "Antibiotic", 15.00, 45, "2026-12-01", True),
            Medicine("MED004", "Vitamin C 1000mg", "Vitamin", 22.50, 200, "2028-01-20"),
            Medicine("MED005", "Cetirizine 10mg", "Antihistamine", 9.80, 60, "2027-09-10"),
            Medicine("MED006", "Omeprazole 20mg", "Gastric", 18.30, 35, "2027-02-28"),
            Medicine("MED007", "Metformin 500mg", "Diabetes", 12.40, 90, "2027-11-05", True),
            Medicine("MED008", "Cough Syrup 100ml", "Cough & Cold", 11.20, 70, "2026-11-30"),
            Medicine("MED009", "Antiseptic Cream", "First Aid", 7.60, 55, "2028-04-18"),
            Medicine("MED010", "Loratadine 10mg", "Antihistamine", 10.50, 40, "2027-07-22"),
        ]
        for med in self.sample_data:
            self.table.insert(med.productID, med)

    def insertProduct(self):
        print("\n--- Insert New Product ---")
        product_id = input("Product ID: ").strip().upper()
        if not product_id:
            print("Product ID cannot be empty.")
            return
        name = input("Name: ").strip()
        category = input("Category: ").strip()
        price = self.readNumber("Price (RM): ", float)
        qty = self.readNumber("Quantity: ", int)
        expiry = input("Expiry date (YYYY-MM-DD): ").strip()
        pres = input("Requires prescription? (y/n): ").strip().lower() == "y"

        med = Medicine(product_id, name, category, price, qty, expiry, pres)
        probes = self.table.insert(product_id, med)
        if probes == -1:
            print(f"Insert failed: product ID '{product_id}' already exists.")
        else:
            print(f"Inserted '{name}' after moving past {probes} occupied slot(s).")

    def searchProduct(self):
        print("\n--- Search Product ---")
        # clean whitespace and capitalize a string in Python
        product_id = input("Enter product ID: ").strip().upper()
        med, index, probes = self.table.search(product_id)
        if med is None:
            print(f"Product '{product_id}' not found.")
        else:
            print(f"Found at slot {index} after moving past {probes} occupied slot(s):")
            print(med)

    def editProduct(self):
        print("\n--- Edit Product ---")
        product_id = input("Enter product ID: ").strip().upper()
        # search() returns (value, index, probes); only the value is needed here
        med, _, _ = self.table.search(product_id)
        if med is None:
            print("Product not found.")
            return
        print("Current:", med)
        # Pressing Enter keeps the current value.
        new_price = input("New price (Enter to keep): ").strip()
        new_qty = input("New quantity (Enter to keep): ").strip()
        try:
            if new_price:
                med.price = float(new_price)
            if new_qty:
                med.qty = int(new_qty)
        except ValueError:
            print("Invalid number entered. Nothing changed.")
            return
        # Objects are stored by reference, so the table already sees the change.
        print("Updated:", med)

    def deleteProduct(self):
        print("\n--- Delete Product ---")
        product_id = input("Enter product ID: ").strip().upper()
        if self.table.delete(product_id):
            print(f"Product '{product_id}' deleted.")
        else:
            print("Product not found.")

    @staticmethod
    def readNumber(prompt, cast):
        """Keep asking until the user types a valid number (input validation)."""
        while True:
            try:
                return cast(input(prompt))
            except ValueError:
                print("Please enter a valid number.")

    def run(self):
        """Main command-line menu loop."""
        actions = {
            "1": self.insertProduct,
            "2": self.searchProduct,
            "3": self.editProduct,
            "4": self.deleteProduct,
            "5": self.table.display,
            "6": lambda: run_benchmark(self.sample_data),
        }
        while True:
            print("\n===== PHARMACY INVENTORY SYSTEM =====")
            print("1. Insert product")
            print("2. Search product")
            print("3. Edit product (price / quantity)")
            print("4. Delete product")
            print("5. Display hash table")
            print("6. Run performance test (Hash Table vs Array)")
            print("0. Exit")
            choice = input("Choose an option: ").strip()
            if choice == "0":
                print("Goodbye!")
                break
            action = actions.get(choice)
            if action:
                action()
            else:
                print("Invalid option, please try again.")

# PART 4: PERFORMANCE COMPARISON - HASH TABLE vs 1-D ARRAY
def arraySearch(array, product_id):
    """Linear search through a 1-D array (Python list): O(n)."""
    for med in array:
        if med.productID == product_id:
            return med
    return None


def timeSearch(search_fn, keys, repeats):
    """Average time (ns) of one search, measured over many repeats.

    A single search is too fast for the clock to measure reliably, so we
    run all keys 'repeats' times and divide the total by the search count.
    """
    start = time.perf_counter_ns()
    for _ in range(repeats):
        for key in keys:
            search_fn(key)
    elapsed = time.perf_counter_ns() - start
    return elapsed / (repeats * len(keys))

# Demo dataset for larger test sizes, set by N
def build_dataset(n):
    return [Medicine(f"MED{i:06d}", f"Drug {i}", "Test", 10.0, 1,
                     "2028-01-01") for i in range(1, n + 1)]

def run_benchmark(sample_data=None):
    """Insert the same data into a hash table and an array
    then conduct searches"""
    random.seed(42)  # fixed seed => reproducible results for sc in report
    datasets = {}
    if sample_data:
        datasets[len(sample_data)] = sample_data  # the real pharmacy data
    for n in (100, 1000, 10000):
        datasets[n] = build_dataset(n)

    print("\n" + "=" * 70)
    print("PERFORMANCE TEST: Hash Table (linear probing) vs 1-D Array")
    print("Average time per search in nanoseconds (lower is better)")
    print("=" * 70)
    print(f"{'Records':>8} | {'Case':<10} | {'Hash Table (ns)':>15} | "
          f"{'Array (ns)':>15} | {'Array/Hash':>10}")
    print("-" * 70)

    for n in sorted(datasets):
        records = datasets[n]
        table = HashTable(11)
        for med in records:  # same data goes into both structures
            table.insert(med.productID, med)
        array = list(records)

        # Existing keys picked at random; missing keys never exist.
        found_keys = [m.productID for m in random.sample(records, min(50, n))]
        missing_keys = [f"NOPE{i}" for i in range(50)]
        repeats = max(1, 20000 // n)

        for label, keys in (("Found", found_keys), ("Not found", missing_keys)):
            t_hash = timeSearch(table.search, keys, repeats)
            t_arr = timeSearch(lambda k: arraySearch(array, k), keys, repeats)
            print(f"{n:>8} | {label:<10} | {t_hash:>15.0f} | "
                  f"{t_arr:>15.0f} | {t_arr / t_hash:>9.1f}x")
        print("-" * 70)

    print("Hash table search is O(1) on average; array search is O(n).")

if __name__ == "__main__":
    PharmacyInventory().run()