tickets = []                    # all tickets ever issued
completed = []                  # served tickets
counters = [None, None]         # None = free, otherwise the ticket number
streak = 0                      # priority tickets served in a row
numbers = iter(range(1, 1000))  # ticket numbers, never reused

PURPOSES = ["Enrollment", "Records", "Payment"]
TYPES = ["regular", "priority"]


def is_valid(purpose, service_type):
    return purpose in PURPOSES and service_type in TYPES


def issue_ticket(purpose, service_type="regular"):
    # returns the ticket number, or None if the input is invalid
    if not is_valid(purpose, service_type):
        return None
    try:
        number = next(numbers)
    except StopIteration:
        return None
    tickets.append({"number": number, "purpose": purpose,
                    "type": service_type, "status": "waiting"})
    return number


def issue_many(*requests):
    # each request is (purpose, service_type)
    # if any request is invalid, no ticket is created
    for r in requests:
        if not is_valid(r[0], r[1]):
            return []
    result = []
    for r in requests:
        result.append(issue_ticket(r[0], r[1]))
    return result


def next_ticket(waiting, streak):
    # returns an INDEX in the waiting list, or None if nobody is waiting
    first_priority = None
    first_regular = None
    for i in range(len(waiting)):
        if waiting[i]["type"] == "priority" and first_priority is None:
            first_priority = i
        if waiting[i]["type"] == "regular" and first_regular is None:
            first_regular = i

    if first_priority is None:
        return first_regular
    if first_regular is None:
        return first_priority
    if streak >= 2:
        return first_regular
    return first_priority


def report(**kwargs):
    # prints only the counts we know; other keywords are ignored
    print("--- Summary Report ---")
    for name in ["waiting", "served", "cancelled", "free_counters"]:
        if name in kwargs:
            print(name + ":", kwargs[name])


def get_waiting():
    waiting = []
    for t in tickets:
        if t["status"] == "waiting":
            waiting.append(t)
    return waiting


while True:
    print("\n1 Issue a ticket")
    print("2 Call the next ticket")
    print("3 Complete a service")
    print("4 Cancel a waiting ticket")
    print("5 Show waiting tickets")
    print("6 Show counter status and completed history")
    print("7 Show a summary report")
    print("8 Exit")
    choice = input("Choose: ")

    if choice == "1":
        count = int(input("How many tickets? "))
        requests = []
        for i in range(count):
            purpose = input("Purpose (Enrollment/Records/Payment): ")
            service_type = input("Type (regular/priority): ")
            requests.append((purpose, service_type))
        result = issue_many(*requests)
        if result == []:
            print("Invalid input. No ticket was issued.")
        else:
            print("Ticket number(s):", result)

    elif choice == "2":
        if None not in counters:
            print("Both counters are busy.")
        else:
            waiting = get_waiting()
            index = next_ticket(waiting, streak)
            if index is None:
                print("No tickets are waiting.")
            else:
                t = waiting[index]
                t["status"] = "serving"
                c = counters.index(None)      # first free counter
                counters[c] = t["number"]
                if t["type"] == "priority":
                    streak = streak + 1
                else:
                    streak = 0
                print("Ticket", t["number"], "go to Counter", c + 1)

    elif choice == "3":
        c = int(input("Which counter finished (1 or 2)? ")) - 1
        if c not in [0, 1] or counters[c] is None:
            print("That counter has no ticket.")
        else:
            for t in tickets:
                if t["number"] == counters[c]:
                    t["status"] = "served"
                    completed.append(t)
            counters[c] = None
            print("Service completed. Counter", c + 1, "is free.")

    elif choice == "4":
        number = int(input("Ticket number to cancel: "))
        found = False
        for t in tickets:
            if t["number"] == number and t["status"] == "waiting":
                t["status"] = "cancelled"
                found = True
        if found:
            print("Ticket cancelled.")
        else:
            print("No waiting ticket with that number.")

    elif choice == "5":
        waiting = get_waiting()
        if len(waiting) == 0:
            print("No tickets are waiting.")
        for t in waiting:
            print("Ticket", t["number"], t["type"], t["purpose"])

    elif choice == "6":
        for i in range(2):
            if counters[i] is None:
                print("Counter", i + 1, ": free")
            else:
                print("Counter", i + 1, ": busy with ticket", counters[i])
        print("Completed history:")
        for t in completed:
            print("Ticket", t["number"], t["type"], t["purpose"])

    elif choice == "7":
        cancelled = 0
        for t in tickets:
            if t["status"] == "cancelled":
                cancelled = cancelled + 1
        free = counters.count(None)
        report(waiting=len(get_waiting()), served=len(completed),
               cancelled=cancelled, free_counters=free, note="ignored")

    elif choice == "8":
        print("Goodbye!")
        break

    else:
        print("Invalid choice. Enter 1 to 8.")