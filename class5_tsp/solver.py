#!/usr/bin/env python3

import sys # コマンドライン引数（sys.argv）を使うために読み込む

# common.pyから2つの関数を取り込む
# read_input: input_*.csvを読んで[(x,y), ...]の座標リストを返す
# print_tour: 点番号のリストを標準出力に書き出す
from common import print_tour, read_input

# 貪欲法で初期解を作る
# 今いる点から一番近い未訪問の点へ進み続ける
def greedy(cities):
    # Build a trivial solution.
    # Visit the cities in the order they appear in the input.
    path = [] # 訪問順に座標を入れていくリスト
    visited = set() # 訪問済みの点を入れる集合
    x, y = cities[0] # 出発点は入力の0番目の点
    path.append((x, y)) # 出発点を経路の先頭に入れる
    visited.add((x, y)) # 出発点を訪問済みとして登録

    # 全ての点を辿り終わるまで繰り返す
    # pathに全ての点が入り、元の'cities'と同じ長さになったら終了
    while len(path) < len(cities):

        nearest_city = () # 今の点から最も近い点
        nearest_distance = float("inf") # 最短距離

        # 全ての点を一つずつ調べる
        for (nx, ny) in cities:

            # まだ訪れたことのない点のみ候補とする
            if (nx, ny) not in visited:
                # 今いる点と候補点との距離の2乗を計算
                # 大小比較のみなら2乗のままで結果が同じなのでsqrtは取らない
                distance = (nx-x)**2+(ny-y)**2

                # 計算の結果、これまでの最短より短ければ
                if distance < nearest_distance:
                    nearest_city = (nx, ny) # 最も近い点を更新
                    nearest_distance = distance # 最短距離も更新

        x, y = nearest_city # 見つかった最も近い点へ移動
        path.append((x, y)) # その点を経路に追加
        visited.add((x, y)) # 訪問済みに登録

    return path # 完成した経路（座標のリスト）を返す

# x座標が線分の内側に存在するかを判定する
# x: 判定したいx座標
# xa, xb: 線分の両端のx座標
def inside(x, xa, xb):
    return min(xa, xb) < x < max(xa, xb)

# 交差している2辺を見つけ、間を逆順にして交差をほどく
def two_opt(cities, path):
    n = len(path) # 点の数
    improved = True # このパスで入れ替えが起きたかを示すフラグ

    while improved: # 入れ替えが起きる限り繰り返す
        improved = False # 開始時にリセットする。入れ替えがなければwhileを抜ける。

        for i in range(1, n-2): # 辺(辺1とする)の位置を動かしていく
            x1, y1 = path[i-1] # 辺1の始点
            x2, y2 = path[i] # 辺1の終点
            slop_12 = (y2-y1) / (x2-x1) # 辺1の傾き（yの増加 ÷ xの増加）
            b12 = y1 - slop_12*x1 # 辺1の切片（y = 傾き*x + 切片 の切片部分）
            
            # 辺の(辺2とする)を動かす。
            # nまで回すことで閉じる辺も対象にする
            for j in range(i+2, n+1):
                # 辺1(0→1) と閉じる辺(n-1→0) は点0を共有する
                # その場合は交差しないので飛ばす
                if  i == 1 and j == n:
                    continue   

                x3, y3 = path[j-1] # 辺2の始点
                x4, y4 = path[j % n] # 辺2の終点。j==n のときpath[0]に戻る
                slop_34 = (y4-y3) / (x4-x3) # 辺2の傾き
                b34 = y3 - slop_34*x3 # 辺2の切片

                # 平行の場合は交点がないのでスキップ
                if slop_12 == slop_34:
                    continue

                # 交点のx座標を求める
                px = (b34-b12) / (slop_12-slop_34)
                
                # 交点のx座標が両方の線分の内側にあったら
                if inside(px, x1, x2) and inside(px, x3, x4):
                    # インデックスiからjまでを逆向きに並べ替える
                    # 交わっている部分を解くため
                    path[i:j] = path[i:j][::-1]
                    improved = True
                    break

            # 入れ替えがあったら、外側のループを抜けてwhileの先頭からやり直す
            if improved:
                break
    # ほどき終わった経路を返す
    return path

def solve(cities):
    # まず貪欲法で初期解を作る
    path = greedy(cities)
    # それを2-optで改善する
    path = two_opt(cities, path)
    # 座標の列を点番号の列に変換して返す
    return [cities.index(c) for c in path]

if __name__ == '__main__':
    assert len(sys.argv) > 1
    tour = solve(read_input(sys.argv[1]))
    print_tour(tour)