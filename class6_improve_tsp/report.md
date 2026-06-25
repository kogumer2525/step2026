
## 1. Or-opt

### 概要(Or-opt)

- 連続するL個の点のかたまりを抜き取って、別の場所に挿し込むことで、経路を短縮する

### 方針

- 動かすかたまりの長さを1,2,3と試す
- かたまりの開始位置を各iについて探索
  - かたまりを抜く前と抜いた後で、浮くコストを計算
  - 抜き取った後の残りの点において、正順・逆順で挿し込んだ時の最良の点を探索
  - 改善があれば挿し込む

### 結果

```
Challenge 0
output          :    3291.62
sample/random   :    3862.20
sample/sa       :    3291.62

Challenge 1
output          :    3778.72
sample/random   :    6101.57
sample/sa       :    3778.72

Challenge 2
output          :    4494.42
sample/random   :   13479.25
sample/sa       :    4494.42

Challenge 3
output          :    8364.30
sample/random   :   47521.08
sample/sa       :    8150.91

Challenge 4
output          :   10897.02
sample/random   :   92719.14
sample/sa       :   10675.29

Challenge 5
output          :   20750.76
sample/random   :  347392.97
sample/sa       :   21119.55

Challenge 6
output          :   40909.17
sample/random   : 1374393.14
sample/sa       :   44393.89
```

### 実装

```python
# 2点 a,b の距離を返す
def dist(a, b):
    dx = a[0] - b[0]                 # x座標の差
    dy = a[1] - b[1]                 # y座標の差
    return (dx*dx + dy*dy) ** 0.5    # √(dx²+dy²)

def or_opt(cities, path):
    n = len(path) # 点の数
    improved = True # 直前のパスで改善があったか（最初は回すためTrue）
    while improved: # 改善が1つでも起きる限り、頭からやり直す
        improved = False # このパスの開始時にリセット（無改善ならループを抜ける）

        # 動かすかたまりの長さを 1→2→3 と変える
        for L in (1, 2, 3): 

            # かたまりの開始位置 i を全点ぶん試す
            for i in range(n):
                seg = [path[(i + t) % n] for t in range(L)] # i から L個ぶんのかたまり（端は%nで巻き戻す）
                p = path[(i - 1) % n] # かたまりの直前の点
                q = path[(i + L) % n] # かたまりの直後の点
                s0, s1 = seg[0], seg[-1] # かたまりの先頭点 s0 と末尾点 s1

                # nが小さく前後がかたまりと重なるケースは飛ばす
                if p in seg or q in seg:
                    continue 

                removed = dist(cities[p],cities[s0]) + dist(cities[s1],cities[q]) - dist(cities[p],cities[q])  # かたまりを抜くと浮く距離（p-s0,s1-qが消えp-qが繋がる）
                # 抜いても得が無いなら、挿入先を探す必要がない
                if removed <= 1e-10:                
                    continue                        

                segset = set(seg) # かたまりの点の集合（除外判定を速くするため）
                rest = [c for c in path if c not in segset]  # かたまりを取り除いた残りの巡回路
                m = len(rest) # 残りの点数（= n - L）

                best_gain, best_at, best_rev = 1e-10, None, False  # 最良の改善量・挿入位置・反転フラグ
                # 残りの各辺 rest[k]→rest[k+1] の隙間を挿入先候補にする
                for k in range(m):    
                    a = rest[k] # 隙間の手前の点
                    b = rest[(k + 1) % m] # 隙間の奥の点（末尾は%mで先頭へ戻る）
                    base = dist(cities[a], cities[b]) # いま a-b を直接つないでいる距離（挿入で消える辺）

                    gain_f = removed - (dist(cities[a],cities[s0]) + dist(cities[s1],cities[b]) - base) # かたまりを「正順」で割り込ませた時の得
                    if gain_f > best_gain: # これまでで一番得なら
                        best_gain, best_at, best_rev = gain_f, k + 1, False # 位置k+1・正順 を記録

                    gain_r = removed - (dist(cities[a],cities[s1]) + dist(cities[s0],cities[b]) - base) # かたまりを「逆順」で割り込ませた時の得
                    if gain_r > best_gain: # 逆順の方がさらに得なら
                        best_gain, best_at, best_rev = gain_r, k + 1, True # 位置k+1・逆順 を記録

                if best_at is not None: # 得する挿入先が1つでも見つかったら引っ越し実行
                    piece = seg[::-1] if best_rev else seg # 逆順フラグが立っていればかたまりを反転
                    path = rest[:best_at] + piece + rest[best_at:] # rest の best_at 位置にかたまりを差し込む
                    improved = True # 改善したので、このパスをやり直すフラグを立てる
                    break # path が変わったので i ループを抜けて作り直す
                
    return path # これ以上どこを動かしても縮まない状態の経路を返す
```