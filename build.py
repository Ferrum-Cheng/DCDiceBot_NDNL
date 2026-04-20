import core

def bd7_main(code):
    if (len(code) != 3) and code != "":
        return "格式錯誤！範例：.cc7bd 742"
    times = list(map(int, code)) if code else [5, 3, 1]

    batches = [
        {"times": times[0], "dice": "3d6", "tag": "STR, CON, DEX, APP, POW"},
        {"times": times[1], "dice": "2d6+6", "tag": "INT, SIZ, EDU"},
        {"times": times[2], "dice": "3d6", "tag": "LUK"}
    ]

    result = []

    for batch in batches:
        batch_data = []
        for _ in range(batch["times"]):
            total, rolls = core.eval_dice(batch["dice"])
            batch_data.append({"rolls": f"[ {rolls} ] × 5", "total": f"{total*5}"})
        result.append(batch_data)

    if times == [5, 3, 1]:
        flat = [item for sublist in result for item in sublist]
        tag = ["STR", "CON", "DEX", "APP", "POW", "INT", "SIZ", "EDU", "LUK"]
        lines = ["============="]

        for i, tag in enumerate(tag):
            lines.append(f"{tag}：{flat[i]['rolls']} = {flat[i]['total']}")
            if tag in ["POW", "EDU", "LUK"]:
                lines.append("=============")
        return "\n".join(lines) + "\n"
    else:
        lines = ["自由分配屬性點數"]
        for i, batch in enumerate(batches):
            lines.append(f"=== {batch['dice']} for {batch['tag']} ===")
            crolls = result[i]
            for t_result in crolls:
                lines.append(f"{t_result['rolls']} = {t_result['total']}")
        lines.append("=============")
        return "\n".join(lines) + "\n"