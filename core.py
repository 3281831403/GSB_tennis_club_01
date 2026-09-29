"""网球俱乐部核心逻辑：会员、场地、教练和计费。"""

import json

DEPOSIT = 20
FEE_PER_DAY = 1


def new_game():
    return {
        "members": {},
        "court_load": 0,
        "court_capacity": 2,
        "balance": 100,
        "day": 1,
        "booking_id": 0,
        "coaches": {"C1": False, "C2": True},
        "rain": False,
        "outdoor_load": 0,
        "cancelled": [],
    }


def save_state(state):
    return json.dumps(state, ensure_ascii=False)


def load_state(text):
    state = json.loads(text)
    # 补全新增字段的默认值，保证旧存档可读；预订编号原样保留，避免编号重复
    state.setdefault("coaches", {"C1": False, "C2": True})
    state.setdefault("rain", False)
    state.setdefault("outdoor_load", 0)
    state.setdefault("cancelled", [])
    return state


def register(state, member_id):
    # 同一会员不可重复注册；重复注册不覆盖既有资料
    if member_id in state["members"]:
        return False
    state["members"][member_id] = {"lessons": 0}
    return True


def book_court(state, member_id):
    # 场地满员不可预约
    if state["court_load"] >= state["court_capacity"]:
        return False
    member = state["members"].setdefault(member_id, {"lessons": 0})
    # 同一会员重复预约幂等处理
    if member.get("booked"):
        return False
    state["court_load"] += 1
    state["balance"] -= DEPOSIT
    state["booking_id"] += 1
    member["booked"] = True
    member["booking_id"] = state["booking_id"]
    member.setdefault("cancelled", False)
    member["cancelled"] = False
    return True


def fee(state, member_id, end_day):
    # 跨日场地费：从当前 day 到 end_day 共跨 end_day - day 天（首尾跨日按天计）
    return (end_day - state["day"]) * FEE_PER_DAY


def cancel(state, member_id):
    # 取消订场退还押金；幂等：同一会员重复取消只退一次
    if member_id in state["cancelled"]:
        return False
    member = state["members"].get(member_id)
    if member is not None and member.get("booked"):
        member["booked"] = False
        state["court_load"] = max(0, state["court_load"] - 1)
    state["balance"] += DEPOSIT
    state["cancelled"].append(member_id)
    if member is not None:
        member["cancelled"] = True
    return True


def assign_coach(state, member_id, coach):
    # 会员不存在或教练请假中均不可排课
    member = state["members"].get(member_id)
    if member is None:
        return False
    if state["coaches"].get(coach, False):
        return False
    member["coach"] = coach
    return True


def refund(state, member_id):
    # 退课失败不扣课时：仅当会员已排教练课时才可退课
    member = state["members"].get(member_id)
    if member is None or not member.get("coach"):
        return False
    if member.get("lessons", 0) <= 0:
        return False
    member["lessons"] -= 1
    member.pop("coach", None)
    return True


def book_outdoor(state, member_id):
    # 雨天闭场：不可预约且不计费，重复调用状态不变
    if state.get("rain", False):
        return False
    state["outdoor_load"] += 1
    return True


def main():
    state = new_game()
    print("网球俱乐部 - 命令: register/book/fee/cancel/coach/refund/outdoor/quit")
    handlers = {
        "register": lambda a: register(state, a[0]) if len(a) == 1 else None,
        "book": lambda a: book_court(state, a[0]) if len(a) == 1 else None,
        "fee": lambda a: fee(state, a[0], int(a[1])) if len(a) == 2 else None,
        "cancel": lambda a: cancel(state, a[0]) if len(a) == 1 else None,
        "coach": lambda a: assign_coach(state, a[0], a[1]) if len(a) == 2 else None,
        "refund": lambda a: refund(state, a[0]) if len(a) == 1 else None,
        "outdoor": lambda a: book_outdoor(state, a[0]) if len(a) == 1 else None,
    }
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not raw or raw == "quit":
            break
        parts = raw.split()
        cmd, args = parts[0], parts[1:]
        handler = handlers.get(cmd)
        if handler is None:
            print("unknown command")
            continue
        result = handler(args)
        if result is None:
            print("bad arguments")
        else:
            print(result)


if __name__ == "__main__":
    main()
