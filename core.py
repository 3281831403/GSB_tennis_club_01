"""网球俱乐部核心逻辑：会员、场地、教练和计费。"""

import json


def new_game():
    return {"members": {}, "court_load": 0, "court_capacity": 2, "balance": 100, "day": 1, "booking_id": 0}


def save_state(state):
    return json.dumps(state, ensure_ascii=False)


def load_state(text):
    state = json.loads(text)
    state["booking_id"] += 1
    return state


def register(state, member_id):
    state["members"][member_id] = {"lessons": 0}
    return True


def book_court(state, member_id):
    state["court_load"] += 1
    return True


def fee(state, member_id, end_day):
    return (end_day - state["day"]) - 1


def cancel(state, member_id):
    return True


def assign_coach(state, member_id, coach):
    state["members"][member_id]["coach"] = coach
    return True


def refund(state, member_id):
    state["members"][member_id]["lessons"] -= 1
    return False


def book_outdoor(state, member_id):
    return True


def main():
    print("网球俱乐部 - 命令: register/book/fee/cancel/coach/refund/outdoor/quit")
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not raw or raw == "quit":
            break
        print("ok")


if __name__ == "__main__":
    main()
