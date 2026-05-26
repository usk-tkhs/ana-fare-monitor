# ここでは骨組みです
# ANA検索部分だけ、実画面に合わせて後で調整します

THRESHOLD = 280000

# 1. ANAで候補日程を検索
# 2. 往路 11:40 / 復路 15:30 の便だけ抽出
# 3. エコノミー スタンダードの合計金額を取得
# 4. state.json と比較
# 5. Discordへ通知
# 6. state.json を更新

if price <= THRESHOLD and price != last_alert_price:
    # 強通知 @here
elif best_price is None or price < best_price:
    # 通常通知
else:
    # 通知なし