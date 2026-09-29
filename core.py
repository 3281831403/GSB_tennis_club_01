"""网球俱乐部核心逻辑：会员、场地、教练和计费。"""

import json

DEPOSIT = 20
DEFAULT_COACHES = {"C1": True, "C2": False}


def new_game():
    return {
        "members": {},
        "court_load": 0,
        "court_capacity": 2,
        "balance": 100,
        "day": 1,
        "booking_id": 0,
        "active_bookings": {},
        "cancelled": [],
        "coaches": dict(DEFAULT_COACHES),
        "rain": False,
        "outdoor_load": 0,
        "outdoor_bookings": [],
    }


def save_state(state):
    return json.dumps(state, ensure_ascii=False)


def load_state(text):
    state = json.loads(text)
    state.setdefault("active_bookings", {})
    state.setdefault("cancelled", [])
    state.setdefault("coaches", dict(DEFAULT_COACHES))
    state.setdefault("rain", False)
    state.setdefault("outdoor_load", 0)
    state.setdefault("outdoor_bookings", [])
    return state


def register(state, member_id):
    if member_id in state["members"]:
        return False
    state["members"][member_id] = {"lessons": 0}
    return True


def book_court(state, member_id):
    if member_id in state["active_bookings"]:
        return False
    if state["court_load"] >= state["court_capacity"]:
        return False

    state["court_load"] += 1
    state["balance"] -= DEPOSIT
    state["booking_id"] += 1
    state["active_bookings"][member_id] = state["booking_id"]
    return True


def fee(state, member_id, end_day):
    return max(0, end_day - state["day"])


def cancel(state, member_id):
    booking_id = state["active_bookings"].pop(member_id, None)
    if booking_id is not None:
        state["court_load"] = max(0, state["court_load"] - 1)
        if member_id not in state["cancelled"]:
            state["cancelled"].append(member_id)
    elif member_id in state["cancelled"]:
        return False
    else:
        state["cancelled"].append(member_id)

    state["balance"] += DEPOSIT
    return True


def assign_coach(state, member_id, coach):
    member = state["members"].get(member_id)
    if member is None:
        return False
    if not state.get("coaches", DEFAULT_COACHES).get(coach, False):
        return False

    state["members"][member_id]["coach"] = coach
    return True


def refund(state, member_id):
    member = state["members"].get(member_id)
    if member is None:
        return False
    if not member.get("coach"):
        return False
    if member.get("lessons", 0) <= 0:
        return False

    member["lessons"] -= 1
    member.pop("coach", None)
    return True


def book_outdoor(state, member_id):
    if state.get("rain", False):
        return False
    if member_id in state.get("outdoor_bookings", []):
        return False

    state["outdoor_load"] = state.get("outdoor_load", 0) + 1
    state.setdefault("outdoor_bookings", []).append(member_id)
    return True


def main():
    state = new_game()
    print("网球俱乐部 - 命令: register/book/fee/cancel/coach/refund/outdoor/quit")
    handlers = {
        "register": lambda args: register(state, args[0]) if len(args) == 1 else None,
        "book": lambda args: book_court(state, args[0]) if len(args) == 1 else None,
        "fee": lambda args: fee(state, args[0], int(args[1])) if len(args) == 2 else None,
        "cancel": lambda args: cancel(state, args[0]) if len(args) == 1 else None,
        "coach": lambda args: assign_coach(state, args[0], args[1]) if len(args) == 2 else None,
        "refund": lambda args: refund(state, args[0]) if len(args) == 1 else None,
        "outdoor": lambda args: book_outdoor(state, args[0]) if len(args) == 1 else None,
    }

    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        parts = raw.split()
        if not parts or parts[0] == "quit":
            break

        command, args = parts[0], parts[1:]
        handler = handlers.get(command)
        if handler is None:
            print("unknown command")
            continue

        try:
            result = handler(args)
        except (TypeError, ValueError):
            result = None

        if result is None:
            print("bad arguments")
        else:
            print(result)


if __name__ == "__main__":
    main()
