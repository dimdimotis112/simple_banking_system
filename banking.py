import sqlite3
import random

running = True

# the database object. stores the data (database) in the file.
conn = sqlite3.connect('card.s3db')
cur = conn.cursor()

# for this test you need this code because it creates a new table every time it is run.
cur.execute('DROP TABLE IF EXISTS card')

cur.execute("""CREATE TABLE IF NOT EXISTS card(
               id INTEGER PRIMARY KEY,
               number TEXT,
               pin TEXT,
               balance INTEGER DEFAULT 0);""")
conn.commit()


# function for stopping the program.
def exit_():
    conn.close()
    global running
    running = False


def start():
    while running:
        print("1. Create an account")
        print("2. Log into account")
        print("0. Exit")
        choice = int(input())
        print()

        if choice == 1:
            create_account()
        elif choice == 2:
            log_in()
        elif choice == 0:
            exit_()
            return


def create_account():
    end_numb_list = [4, 0, 0, 0, 0, 0]
    pin = ""

    while len(end_numb_list) < 15:
        numb = random.randrange(9)
        end_numb_list.append(numb)

    end_numb_list_check = end_numb_list.copy()
    # multiplies odd index numbers by two.

    for i in range(1, len(end_numb_list_check) + 1):
        if i % 2 != 0:
            end_numb_list_check[i - 1] *= 2

    # subtracts 9 if a number is over 9.

    for i in range(len(end_numb_list_check)):
        if end_numb_list_check[i] > 9:
            end_numb_list_check[i] -= 9

    sum_of_list = sum(end_numb_list_check)

    if sum_of_list % 10 != 0:
        for i in range(1, 10):
            if (sum_of_list + i) % 10 == 0:
                end_numb_list.append(i)
                break
    else:
        end_numb_list.append(0)

    end_numb = ""
    for numb in end_numb_list:
        end_numb += str(numb)

    while len(pin) < 4:
        num = random.randrange(9)
        pin += str(num)

    cur.execute(f'INSERT INTO card(number, pin) VALUES("{end_numb}", "{pin}")')
    conn.commit()

    print("Your card has been created")
    print("Your card number:")
    print(end_numb)
    print("Your card PIN:")
    print(pin)
    print()


def luhn_checker(card_number):
    nDigits = len(card_number)
    nSum = 0
    isSecond = False

    for i in range(nDigits - 1, -1, -1):
        d = ord(card_number[i]) - ord('0')

        if (isSecond == True):
            d = d * 2

        # We add two digits to handle
        # cases that make two digits after
        # doubling
        nSum += d // 10
        nSum += d % 10

        isSecond = not isSecond

    if (nSum % 10 == 0):
        return False
    else:
        return True


def log_in():
    def show_balance():
        cur.execute(f"""SELECT balance
                    FROM card
                    WHERE number = '{card_nr}';""")
        balance = cur.fetchone()
        print(f'Balance: {balance[0]}')  # [0] so that it doesn't return a Tuple, just the value.
        print()

    def add_income():
        print("Enter income:")
        income = int(input())
        cur.execute(f"""UPDATE card
                        SET balance = balance + {income}
                        WHERE number = {card_nr};""")
        conn.commit()
        print("Income was added!")
        print()

    def transfer():
        print("Enter card number:")
        receiver_nr = input()

        cur.execute(f"SELECT balance FROM card WHERE number = {card_nr};")  # gets the senders balance.
        balance = cur.fetchone()
        cur.execute(f"SELECT number, balance FROM card WHERE number = {receiver_nr};")  # gets the receiver number.

        try:
            receiver_nr_exist, receiver_balance = cur.fetchone()
        except TypeError:
            receiver_nr_exist = 0

        if luhn_checker(receiver_nr):
            print("Probably you made a mistake in the card number. Please try again!")
        elif receiver_nr == card_nr:
            print("You can't transfer money to the same account!")
        elif receiver_nr != receiver_nr_exist:
            print("Such a card does not exist.")
        else:
            print("Enter how much money you want to transfer:")
            amount = int(input())

            if amount > balance[0]:
                print("Not enough money!")
            else:
                cur.execute(f"UPDATE card SET balance = balance + {amount} WHERE number = {receiver_nr};")
                cur.execute(f"UPDATE card SET balance = balance - {amount} WHERE number = {card_nr};")
                conn.commit()
                print("Success!")
                print()

    def close_acc():
        # deletes the account from the database.
        cur.execute(f"DELETE FROM card WHERE number = {card_nr};")
        conn.commit()
        print("The account has been closed!")
        print()

    def log_out():
        print("You have successfully logged out!")
        print()

    print("Enter your card number:")
    card_nr = input()
    print("Enter your PIN:")
    card_pin = input()
    print()

    cur.execute(f"""SELECT pin FROM card
                    WHERE number = '{card_nr}'""")
    # Try to extract the number and pin from cursor, if there's no value set it to None.

    pin = cur.fetchone()

    if pin is not None and card_pin == pin[0]:
        print("You have successfully logged in!")
        print()

        while True:
            print("1. Balance")
            print("2. Add income")
            print("3. Do transfer")
            print("4. Close account")
            print("5. Log out")
            print("0. Exit")
            choice = int(input())
            print()

            if choice == 1:
                show_balance()
            elif choice == 2:
                add_income()
            elif choice == 3:
                transfer()
            elif choice == 4:
                close_acc()
            elif choice == 5:
                log_out()
                return
            elif choice == 0:
                exit_()
                return
    else:
        print("Wrong card number or PIN!")


start()
print("Bye!")
