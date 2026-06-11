## Class4

- [問題](#問題)
- [宿題1](#宿題1)
  - [方針](#方針)
  - [コード](#コード)
- [宿題2](#宿題2)
  - [方針](#方針-1)
  - [コード](#コード-1)

## 問題

- **宿題1:** あるページから別のページへの最短経路を出力する
- **宿題2:** ページランクを計算して重要度の高いページトップ10を求める
- **宿題3:** Wikipedia のグラフについて「渋谷」から「池袋」まで、同じページを重複して通らない、できるだけ長い経路を発見する

## 宿題1

### 方針

- 最短経路なのでBFSを使う
- 最短経路を取り出せるようにしたい
  - BFSで次のページに進むたびに、前のページを記録する
    - ページ数分の配列'parent'を用意
    - parent[node]: 'node'の一つ前にいたページ
  - 最後に最短経路を見つけたら、'goal'から'start'まで、前のページを記録したページを辿って経路を求める

### コード

```python
# タイトルの文字列からページIDを探して返す
# title: 検索したいページタイトル
# 返り値: 対応するページID
def find_id(self, title):
    for key, value in self.titles.items():
        if value == title:
            return key

# Homework #1: Find the shortest path.
# 'start': A title of the start page.
# 'goal': A title of the goal page.
def find_shortest_path(self, start, goal):

    # タイトルからページIDに変換する
    start_id = self.find_id(start)
    goal_id = self.find_id(goal)

    queue = collections.deque() # BFS用のキュー
    visited = {} # 訪問済みのページを管理する
    visited[start_id] = True
    queue.append(start_id)

    # 一つ前にいたページを記録しておく
    # 最後に経路を逆にたどり、最短経路を出力するため
    parent = {}

    # 最短を求めたいのでBFS
    # キューが空になるまで続ける
    while len(queue) > 0:
        # キューの先頭（次に処理すべきページ）を取り出す
        node = queue.popleft()

        # ゴールに到達したら終了
        if node == goal_id:
            break

        # 現在のページと隣接している全てのページをキューに追加
        for child in self.links[node]:
            # 既に訪れていたら追加しない
            if child not in visited:
                queue.append(child) # 未訪問なのでキューに積む
                visited[child] = True # 再度訪れないよう記録する
                parent[child] = node # 経路復元用に一つ前のページを記録

    # goalから経路を復元し、最短経路を出力する
    path = [] # 復元した経路を格納するリスト
    before = goal_id # ゴールから順位辿っていく

    # startに戻るまで、parentを使って一つ前のノードへさかのぼる
    while before != start_id:
        path.append(before) # 現在地を経路に追加
        before = parent[before] # 一つ前のノードへ移動       
    # start自身もリストに追加
    path.append(start_id)

    # goal -> start を start -> goal の順に並び直して表示
    for i, p in enumerate(reversed(path)):
        print(f'{i}回目: id: {p}, title: {self.titles[p]}')
    print()
```

## 宿題2

### 方針

- 以下2つのリスト・関数でランク更新を行う
  - keyがidの辞書: 隣接ノードから配布された分を保管（`add_rank`）
  - 全体配布分のランクの合計値: 最後にノード数分で割って分配（`distribute`）

- 処理の流れ
  - ノードを一つ一つ見ていき、以下の処理を行う
    - 隣接ノードがある場合:
      - 自身のページランクの85%を隣接ノードに配分: `add_rank[配布先ID]`に加算
      - 自身のページランクの15%は全体配布する: `distribute`に加算
    - 隣接ノードがない場合:
      - 自身のページランク全てを全体配布する: `distribute`に加算
  - ページランクを更新する。以下2点の合計で新しい値を更新する。
    - 全体配布分のランクの合計値（`distribute`）をノード数で割ったもの
    - `add_rank[自身のID]`に加算された、隣接ノードから配布されたランク

### コード

```python
# 収束判定を行う
    # 収束条件: ∑(new_pagerank[i] - old_pagerank[i])^2 < 0.01
    def check_converge(self, new_pagerank, old_pagerank):
        ans = False
        for id in self.titles.keys():
            if (new_pagerank[id] - old_pagerank[id])**2 >= 0.01:
                ans = True # 収束していない場合、Trueを返す
        return ans # 収束した場合、Falseを返す

    # Homework #2: Calculate the page ranks and print the most popular pages.
    def find_most_popular_pages(self):
        # 使う辞書を用意
        rank = {} # 各ページの現在のPageRank値 {id: 値}
        old_pagerank = {} # 一周前のPageRank値（収束判定で今の値と比べる用）{id: 値}
        add_rank = {} # 計算途中の一時置き場。他ページから流入してくる分の合計 {id: 値}

        # 3つの辞書を初期化
        for id in self.titles.keys(): # 全ページのidについて
            old_pagerank[id] = 0 # 前回値は0スタート（初回判定で未収束にするため）
            rank[id] = 1 # PageRankは全ノード1で初期化
            add_rank[id] = 0 # まだ流入がないので0
        
        # 収束する（'check_converge'がFalseになる）までループする
        # ノードの85%は隣接ノードに均等に配分し、残りの15%は全ノードに均等に配分する
        # もしノードPに隣接ノードがない場合、100%を全ノードに均等に分配する
        while self.check_converge(rank, old_pagerank):
            old_pagerank = rank.copy() # ループの頭で、現在の値を前回値としてコピー
            distribute_all = 0 # 全ノードに分配する分を足していく

            # 各ページが持つページランクを隣接ノードへ配る
            for id in self.titles.keys(): # 全ページidについて
                # 隣接ページを持たないページなら
                if self.links[id] == []:
                    distribute_all += rank[id] # 自分のページランク全部を全体に配分する
                    continue
                # 隣接ページをもつなら
                else:
                    # 自分のrankの85%を、リンク先の数で割って均等配分する
                    distribute_num = rank[id] * 0.85 / len(self.links[id])
                    for next_list in self.links[id]: 
                        # 各隣接ページについて、配分量を流入分に加算
                        add_rank[next_list] += distribute_num
                    
                    # 残り15%は全体に配分する
                    distribute_all += rank[id] * 0.15

            # 全体配布分をページ数で均等に割り、1ページあたりの配布分を求める
            distribute = distribute_all / len(self.titles)
            
            # ページランクを更新する
            for id in self.titles.keys():
                # 隣接ノード配布分と全体配布分を全て足し合わせる
                rank[id] = add_rank[id] + distribute
                add_rank[id] = 0 # 足し終わったので初期化する

            # ページランクの合計値が一定に保たれているかの確認
            total = 0
            for id in self.titles.keys():
                total += rank[id]
            print(total)
        
        # sortのキー関数。(id, value) のタプルからvalueを取り出す
        def get_rank_value(item):
            return item[1]
        # valueで降順にソートする
        result = sorted(rank.items(), key = get_rank_value, reverse=True)
        # 上位10件を表示
        i = 0
        for i, (key, value) in enumerate(result[:10]):
            print(f'{i+1}番目: id: {key}, title: {self.titles[key]}, rank: {value}')
```

## 宿題3

### 方針
