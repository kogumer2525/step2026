#!/usr/bin/env python3

import sys # コマンドライン引数（sys.argv）を使うために読み込む
import random, time, math

# common.pyから2つの関数を取り込む
# read_input: input_*.csvを読んで[(x,y), ...]の座標リストを返す
# print_tour: 点番号のリストを標準出力に書き出す
from common import print_tour, read_input

# 貪欲法で初期解を作る
# 今いる点から一番近い未訪問の点へ進み続ける
def greedy(cities):
    n = len(cities) # 点の総数

    tour = [0] # 訪問順（点番号で記録）。出発点は0番
    visited = [False]*n # 各点が訪問済みか。添字=点番号、最初は全部False
    visited[0] = True # 0番は出発点なので訪問済みにする
    cx, cy = cities[0] # 今いる点の座標（最初は0番の座標）

    for _ in range(n-1): # 残りn-1個の点を1つずつ訪問していく
        best, nd = -1, float("inf") # best:最も近い点の番号、nd:その距離²（infで初期化）

        for j in range(n): # 全ての点を番号jで順に調べる
            if not visited[j]: # まだ訪れていない点だけを候補にする
                # 今いる点(cx,cy)と点jの距離の2乗。比較だけなのでsqrtは取らない
                d = (cities[j][0]-cx)**2 + (cities[j][1]-cy)**2
                if d < nd: # これまでの最短より近ければ
                    nd, best = d, j # 最短距離と最近点の番号を更新

        visited[best] = True # 見つかった最近点を訪問済みにする
        tour.append(best) # その点の「番号」を訪問順に追加
        cx, cy = cities[best] # 今いる点をその最近点へ移動

    return tour # 完成した訪問順（点番号のリスト）を返す

# 交差している2辺を見つけ、間を逆順にして交差をほどく
def two_opt(cities, path):
    n = len(path) # 点の数
    improved = True # このパスで入れ替えが起きたかを示すフラグ

    while improved: # 入れ替えが起きる限り繰り返す
        improved = False # 開始時にリセットする。入れ替えがなければwhileを抜ける。

        for i in range(1, n-1): # 辺(辺1とする)の位置を動かしていく
            a = path[i-1] # 辺1の始点
            b = path[i] # 辺1の終点
            
            # 辺の(辺2とする)を動かす。
            # nまで回すことで閉じる辺も対象にする
            for j in range(i+1, n+1):
                # 辺1(0→1) と閉じる辺(n-1→0) は点0を共有する
                # その場合は交差しないので飛ばす
                if  i == 1 and j == n:
                    continue   

                c = path[j-1] # 辺2の始点
                d = path[j % n]; # 辺2の終点。j==n のときpath[0]に戻る

                before = dist(cities[a],cities[b]) + dist(cities[c],cities[d])
                after  = dist(cities[a],cities[c]) + dist(cities[b],cities[d])
                
                if after - before < -1e-10:   # 繋ぎ直した方が短いなら
                    path[i:j] = path[i:j][::-1]  # B〜C の区間(=index i〜j-1)を逆順に
                    improved = True
                    break

    # ほどき終わった経路を返す
    return path

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

# 巡回路の総距離を返す（最後の点から先頭点へ戻る分も足す）
def tour_len(cities, path):
    n = len(path)
    return sum(dist(cities[path[i]], cities[path[(i+1)%n]]) for i in range(n)) # i+1 を len(path) で割った余りにすることで、最後だけ (n-1)→0 のループになる

# 巡回路を4つに切って真ん中2ブロックを入れ替える
def double_bridge(path):
    n = len(path) # 点の数
    p1 = 1 + random.randrange(n - 3) # 1番目の切れ目
    p2 = p1 + 1 + random.randrange(n - p1 - 2) # # 2番目の切れ目（p1より後ろ）
    p3 = p2 + 1 + random.randrange(n - p2 - 1)  # 3番目の切れ目（p2より後ろ）
    # [0:p1] [p1:p2] [p2:p3] [p3:] の4ブロックを、真ん中2つを入れ替えて再結合
    return path[:p1] + path[p2:p3] + path[p1:p2] + path[p3:]

# 局所探索：2-opt → or-opt を順にかけて、これ以上縮まない状態まで持っていく
def local_search(cities, path):
    return or_opt(cities, two_opt(cities, path))

# 全体の流れ
def solve(cities, time_limit=30.0, T0=None, T_end=1e-6):
    init_greedy = greedy(cities)                          # 貪欲法で初期解
    best = local_search(cities, init_greedy)             # 2-opt→or-opt
    return best

if __name__ == '__main__':
    assert len(sys.argv) > 1
    tour = solve(read_input(sys.argv[1]))
    print("index")       
    print_tour(tour)