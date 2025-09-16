import os
import sys
import time
import termios
import tkinter as tk
from datetime import datetime, date
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

def select_item_gui(items):
    """Open a GUI window to select item with autocomplete"""
    selected_item = {"value": None}  # Use dict to allow modification inside inner function

    class AutocompleteEntry(tk.Entry):
        def __init__(self, items, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.items = sorted(items)
            self.var = self["textvariable"] = tk.StringVar()
            self.var.trace("w", self.changed)
            self.listbox = None

        def changed(self, name, index, mode):
            if self.var.get() == "":
                if self.listbox:
                    self.listbox.destroy()
                    self.listbox = None
                return

            words = [item for item in self.items if item.lower().startswith(self.var.get().lower())]

            if words:
                if not self.listbox:
                    self.listbox = tk.Listbox()
                    self.listbox.bind("<<ListboxSelect>>", self.on_select)
                    self.listbox.place(x=self.winfo_x(), y=self.winfo_y() + self.winfo_height())
                self.listbox.delete(0, tk.END)
                for w in words:
                    self.listbox.insert(tk.END, w)
            else:
                if self.listbox:
                    self.listbox.destroy()
                    self.listbox = None

        def on_select(self, event):
            if self.listbox and self.listbox.curselection():
                index = self.listbox.curselection()[0]
                value = self.listbox.get(index)
                selected_item["value"] = value
                # Delay destroying root to avoid "winfo" error
                self.after(50, root.destroy)


    root = tk.Tk()
    root.title("Select Item")
    root.geometry("400x150")

    tk.Label(root, text="Type item name:").pack(pady=10)
    entry = AutocompleteEntry(items, root)
    entry.pack(padx=20, pady=5)

    # Cancel button
    tk.Button(root, text="Cancel", command=root.destroy).pack(pady=10)

    root.mainloop()
    return selected_item["value"]


inventory = []
ITEM = "item_name.txt"
FILE_NAME = "inventory.txt"
SELL_RECORD = "sell_records.txt"
PURCHASE_RECORD = "purchase_records.txt"


if os.path.exists(FILE_NAME):

    with open(FILE_NAME, "r") as file:
        
        for line in file: 
            parts1 = line.strip().split(",")
            if len(parts1) < 2:
                continue
            name = parts1[0]        # First part is the name
            price = float(parts1[1]) # Second part is the price (convert to number)
            # Add to inventory
            inventory.append({"name": name, "price": price})


def clear_input_buffer():
    """clear any buffer keystrokes"""
    try:
        termios.tcflush(sys.stdin, termios.TCIFLUSH)
    except:
        try:
            import msvcrt
            while msvcrt.kbhit():
                msvcrt.getch()
        except:
            pass


def loading_animation(message="Loading", duration=0.5):
    """Display a loading animation for given duration"""
    for i in range(duration * 10):
        print(f"\r{message} {'.' * (i % 4)}", end="", flush=True)
        time.sleep(0.1)
    os.system('cls' if os.name == 'nt' else 'clear') 

    
def sell():
    loading_animation("\033[94mEntering Sell Module\033[0m", 1)
    clear_input_buffer()
    print("\n------------------------------------------------")
    print("|\t\t SELL ENTRY                    |")
    print("------------------------------------------------")
    print("| 0. BACK TO MENU  |")
    print("--------------------")

    with open("item_name.txt", "r") as file:
        items = [line.strip().split(",")[0] for line in file if line.strip()]

    customer_name = input("\nEnter Customer Name : ")
    if customer_name == "0":
        return

    # Open GUI to select item
    item_name = select_item_gui(items)
    if item_name is None:
        return

    quantity = int(input("Enter the quantity: "))
    if quantity == 0:
        return

    # ✅ Step 1: Check if item exists in ITEM file
    item_found = False
    item_price = 0
    with open(ITEM, "r") as file:
        for line in file:
            parts = line.strip().split(",")
            if len(parts) < 2:
                continue
            name = parts[0]
            price = float(parts[1])
            if name == item_name:
                item_found = True
                item_price = price
                break

    if not item_found:
        print("\033[91mItem does not exist in catalog! Please add it first.\033[0m")
        return

    # ✅ Step 2: Check if item exists in inventory and has enough quantity
    inventory_found = False
    inventory_qty = 0
    with open(FILE_NAME, "r") as file:
        lines = file.readlines()

    for line in lines:
        parts = line.strip().split(",")
        if len(parts) < 2:
            continue
        name = parts[0]
        qty = int(parts[1])
        if name == item_name:
            inventory_found = True
            inventory_qty = qty
            break

    if not inventory_found:
        print("\033[91mItem not available in inventory! Please purchase it first.\033[0m")
        return

    if quantity > inventory_qty:
        print("\n\033[91mNot enough stock available! Please purchase more.\033[0m")
        return

    # ✅ If both checks pass, proceed to sell
    final_price = quantity * item_price
    print(f"\nSelling {quantity} of {item_name} to {customer_name} at total {final_price}")

    # You can now update the inventory, record the sale, etc.

    updated_lines = []
    for line in lines:
        parts = line.strip().split(",")
        if len(parts) < 2:
            continue
        name = parts[0]
        qty = int(parts[1])
        
        if name == item_name:
            new_qty = qty - quantity
            updated_lines.append(f"{name},{new_qty}\n")
        else:
            updated_lines.append(line)

    with open(FILE_NAME, "w") as file:
        file.writelines(updated_lines)

    print("\033[92mInventory updated successfully ✅\033[0m")

    for item in inventory:
        if item['name'] == item_name:
            item['price'] = item_price
            item['quantity'] = inventory_qty - quantity
            break

    # ✅ Record the sale
    current_time = datetime.now()
    today_date = date.today()
    with open(SELL_RECORD, "a") as sell_file:
        sell_file.write(f"{customer_name},{item_name},{final_price},{today_date}\n")

    print(f"\033[93mSale recorded on {today_date} at {current_time.strftime('%H:%M:%S')}\033[0m")

def purchase():
    loading_animation("\033[94mEntering purchase Module\033[0m", 1) 
    clear_input_buffer()
    print("\n------------------------------------------------")
    print("|\t\t PURCHASE ENTRY                |")
    print("------------------------------------------------")
    print("| 0. BACK TO MENU  |")
    print("--------------------")
    sup_name = input("\nEnter Supplier Name : ")
    if sup_name == "0":
        return
    sup_item = input("Enter Item Name :")
    if sup_item == "0":
        return
    
    with open(ITEM, "r") as file:
        lines = file.readlines()

        for words in lines:
            parts3 = words.strip().split(",")
            name = parts3[0]
            if name == sup_item:
                sup_quantity = int(input("Enter Item Quantity :"))
                sup_price = float(input("Enter Item price :"))
                final_p_price = sup_price * sup_quantity
                current_date = datetime.today()
                print(f"\n \t\t\t Date = {current_date}\n \t✅Purchase History Updated \n Supplyer Name = {sup_name} \n Item Name = {sup_item} \n Quantity = {sup_quantity} \n Item Price = {final_p_price} \n")

                with open(PURCHASE_RECORD, "a") as purchase_file:
                    purchase_file.write(f"{sup_name},{sup_item},{sup_quantity},{final_p_price},{current_date.date()}")

                    with open(FILE_NAME, "a") as inv_file:
                        inv_file.write(f"{sup_item},{sup_quantity},{sup_price}\n")
                    break

        else :
            print("\n\033[91mItem Dose Not Exits ! , Add Item First /033[0m")
            print("\033[92mRedircting To Add Items Page ... \n\033[0m")
            Add_item()

def Add_item():
    loading_animation("\033[94mEntering Add Items Module\033[0m", 1) 
    clear_input_buffer()
    print("\n------------------------------------------------")
    print("|\t\t ADD ITEM                      |")
    print("------------------------------------------------")
    print("| 0. BACK TO MENU   |")
    print("---------------------")

    with open("item_name.txt", "r") as file:
        items = [line.strip().split(",")[0] for line in file if line.strip()]


    item_completer = WordCompleter(items, ignore_case=True)


    name = prompt("\nEnter Item Name : ", completer=item_completer).strip()
    if name == "0":
        return

    # ✅ Check if the item already exists
    with open(ITEM, "r") as file:
        for line in file:
            parts = line.strip().split(",")
            if len(parts) < 2:
                continue
            existing_name = parts[0]
            if existing_name.lower() == name.lower():
                print(f"\n❌ \033[92mItem '{name}' already exists in the catalog!\033[0m")
                return

    try:
        price = float(input("Enter Item Selling Price : "))
        if price <= 0:
            print("Price must be greater than 0.")
            return
    except ValueError:
        print("\033[91mInvalid price entered!\033[0m")
        return

    # ✅ Add the new item
    with open(ITEM, "a") as file:
        file.write(f"{name},{price}\n")
    
    print(f"\033[92m\n✅ Item '{name}' added successfully with price {price}\033[0m")


def Remove_item():
        loading_animation("\033[94mEntering Remove Items Module\033[0m", 1) 
        clear_input_buffer()
        print("\n------------------------------------------------")
        print("|\t\t REMOVE IETM'S                 |")
        print("------------------------------------------------")
        print("| 0. BACK TO MENU  |")
        print("--------------------")
        rem = input("\nEnter The Item Name You Want To Remove (CASE SENSITIVE !) : ")
        if rem == "0":
            return 
        global inventory
        found = False
        for item in inventory:
            if item["name"] == rem:
                inventory.remove(item)
                found = True
                break

        if found:
            sure = input(f"\033[91mARE YOU SURE YOU WANT TO DELETE THE {rem}? (Y/N) :\033[0m")
            sure = sure.lower()

            if sure == 'y':

                with open(FILE_NAME, "r") as file:
                    lines = file.readlines()


                    new_lines = []
                    for line in lines:
                        if not line.startswith(rem + ","):
                            new_lines.append(line)

                with open(FILE_NAME, "w") as remove_file:
                    remove_file.writelines(new_lines)
                
                    print(f"\033[91m'{rem}'removed successfully.\033[0m")
            else :
                return 
        
        else :
            print("\033[91mItem Not Found !\033[0m")


from datetime import datetime, date

def calculate():
    loading_animation("\033[94mEntering Calculate Module\033[0m", 1) 
    clear_input_buffer()
    print("\n--------------------------------------------------")
    print("|\t\t CALCULATE (DAY / MONTH) P&L     |")
    print("--------------------------------------------------")
    print("| 0. BACK TO MENU  |")
    print("--------------------")

    try:
        choose1 = input("Enter to find monthly or daily P & L (M/D) : ")
        choose1 = choose1.lower()

        if choose1 not in ["m", "d"]:
            print("\n\033[91mENTER ONLY M or D!! FOR (P & L)\033[0m")
            return

        today = date.today()
        today_str = today.isoformat()  # "YYYY-MM-DD"
        month = today.month
        year = today.year

        # Calculate total sales
        total_sales = 0
        with open(SELL_RECORD, "r") as cal_file:
            for line in cal_file:
                parts = line.strip().split(",")
                amount = float(parts[2])
                sale_date = parts[3]

                if choose1 == "d":
                    if sale_date == today_str:
                        total_sales += amount
                else:  # Monthly
                    sale_date_obj = datetime.strptime(sale_date, "%Y-%m-%d").date()
                    if sale_date_obj.year == year and sale_date_obj.month == month:
                        total_sales += amount

        # Calculate total purchases
        total_purchases = 0
        with open(PURCHASE_RECORD, "r") as cal_file2:
            for line in cal_file2:
                parts = line.strip().split(",")
                amount = float(parts[3])
                purchase_date = parts[4]

                if choose1 == "d":
                    if purchase_date == today_str:
                        total_purchases += amount
                else:
                    purchase_date_obj = datetime.strptime(purchase_date, "%Y-%m-%d").date()
                    if purchase_date_obj.year == year and purchase_date_obj.month == month:
                        total_purchases += amount

        result = total_sales - total_purchases

        if result >= 0:
            print(f"\n✅ Your {'Daily' if choose1 == 'd' else 'Monthly'} Profit is Around {result}")
        else:
            print(f"\n❌ Your {'Daily' if choose1 == 'd' else 'Monthly'} Loss is Around {abs(result)}")

    except Exception as e:
        print("An error occurred:", e)

    


def list_item():
    loading_animation("\033[94mEntering List Items Module\033[0m", 1) 
    clear_input_buffer()
    print("\n--------------------------------------------------")
    print("|\t\t ITEM LIST                       |")
    print("--------------------------------------------------")
    with open(ITEM, "r") as list_file:
            list_lines = list_file.readlines()

    if not list_lines:  # 🟢 Check if list is EMPTY
        print("List IS Empty , Add Items..")
        choose1 = input("\033[93mWant To Add New Items ?\033[93m (\033[92mY\033[0m/\033[91mN\033[0m)").lower()
        if choose1 == 'y':
            print("\n\033[92mRedirecting To Add Items ...\033[92m")
            Add_item()
        else:
            print("\n Redirecting To Main Menu ...")
            return   # main_fun()  # ⚠️ Be careful: calling main_fun() recursively might cause issues
    else:
        print("\n\t\tALL ITEM LIST 📋")
        num = 1
        for line4 in list_lines:
            parts4 = line4.strip().split(",")
            if len(parts4) >= 1 and parts4[0].strip():  # 🟢 Safety check
                l_item = parts4[0]
                print(f"{num}) {l_item}")
                num += 1


def list_sales():
    loading_animation("\033[94mEntering List Sales Module\033[0m", 1)
    clear_input_buffer()
    print("\n--------------------------------------------------")
    print("|\t\t SALES RECORD                   |")
    print("--------------------------------------------------")

    try:
        with open(SELL_RECORD, "r") as file:
            lines = file.readlines()

        if not lines:
            print("\033[91mNo sales records found!\033[0m")
            return

        print("\nDate\tCustomer\tItem\tAmount")
        print("---------------------------------------")
        for line in lines:
            parts = line.strip().split(",")
            customer = parts[0]
            item = parts[1]
            amount = parts[2]
            date_str = parts[3]
            print(f"{date_str}\t{customer}\t{item}\t{amount}")

    except FileNotFoundError:
        print("Sales record file not found!")
    except Exception as e:
        print("An error occurred:", e)


def list_purchases():
    loading_animation("\033[94mEntering List Purchases Module\033[0m", 1)
    clear_input_buffer()
    print("\n--------------------------------------------------")
    print("|\t\t PURCHASE RECORD                |")
    print("--------------------------------------------------")

    try:
        with open(PURCHASE_RECORD, "r") as file:
            lines = file.readlines()

        if not lines:
            print("\033[91mNo purchase records found!\033[0m")
            return

        print("\nDate\tSupplier\tItem\tQuantity\tAmount")
        print("------------------------------------------------")
        for line in lines:
            parts = line.strip().split(",")
            supplier = parts[0]
            item = parts[1]
            quantity = parts[2]
            amount = parts[3]
            date_str = parts[4]
            print(f"{date_str}\t{supplier}\t{item}\t{quantity}\t{amount}")

    except FileNotFoundError:
        print("Purchase record file not found!")
    except Exception as e:
        print("An error occurred:", e)


def list_inventory():
    loading_animation("\033[94mEntering Inventory List Module\033[0m", 1)
    clear_input_buffer()
    print("\n--------------------------------------------------")
    print("|\t\t INVENTORY LIST                  |")
    print("--------------------------------------------------")

    try:
        with open(FILE_NAME, "r") as file:
            lines = file.readlines()

        if not lines:
            print("\033[91mInventory is empty! Please add or purchase items.\033[0m")
            return

        print("\nItem Name\tQuantity")
        print("----------------------------")

        for line in lines:
            parts = line.strip().split(",")
            if len(parts) < 2:
                continue
            name = parts[0]
            qty = int(parts[1])
            print(f"{name}\t{qty}")

    except FileNotFoundError:
        print("Inventory file not found! Please check the system.")
    except Exception as e:
        print(f"An error occurred: {e}")

def main_fun():
    while True:
        print("\n---------------------------------------------------")
        print("|\t\t Data Entry                       |")         
        print("---------------------------------------------------")
        print("| 1. Sell Entry                                   |")
        print("| 2. Purchase Entry                               |")
        print("| 3. Add a New Item                               |")
        print("| 4. Remove an Item                               |")
        print("| 5. Calculate total profit or loss (DAY/MONTH)   |")
        print("| 6. List all items                               |")
        print("| 7. List all sales                               |")
        print("| 8. List all purchases                           |")
        print("| 9. List current inventory                       |")
        print("| 10.EXIT                                        |")
        print("---------------------------------------------------")

        try:
            choose = int(input("Enter Your Choice : "))
            print("--------------------------------------------------")
        
            if choose == 1:
                sell()
            elif choose == 2:
                purchase()
            elif choose == 3:
                Add_item()
            elif choose == 4:
                Remove_item()
            elif choose == 5:
                calculate()
            elif choose == 6:
                list_item()
            elif choose == 7:
                list_sales()
            elif choose == 8:
                list_purchases()
            elif choose == 9:
                list_inventory()
            elif choose == 10:
                print("\033[91mExiting The Software...\033[0m")
                break
            else:
                print("\033[91mEnter a valid option!\033[0m")

        except ValueError:
            print("\033[91mPlease Enter a Number!\033[0m")

main_fun()
