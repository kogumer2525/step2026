import sys
import collections
import time # 'find_longest_path' での時間制限管理に使う
import random # 'find_longest_path' での探索順ランダムに使う

class Wikipedia:

    # Initialize the graph of pages.
    def __init__(self, pages_file, links_file):

        # A mapping from a page ID (integer) to the page title.
        # For example, self.titles[1234] returns the title of the page whose
        # ID is 1234.
        self.titles = {}

        # A set of page links.
        # For example, self.links[1234] returns an array of page IDs linked
        # from the page whose ID is 1234.
        self.links = {}

        # Read the pages file into self.titles.
        with open(pages_file) as file:
            for line in file:
                (id, title) = line.rstrip().split(" ")
                id = int(id)
                assert not id in self.titles, id
                self.titles[id] = title
                self.links[id] = []
        print("Finished reading %s" % pages_file)

        # Read the links file into self.links.
        with open(links_file) as file:
            for line in file:
                (src, dst) = line.rstrip().split(" ")
                (src, dst) = (int(src), int(dst))
                assert src in self.titles, src
                assert dst in self.titles, dst
                self.links[src].append(dst)
        print("Finished reading %s" % links_file)
        print()

    # Example: Find the longest titles.
    def find_longest_titles(self):
        titles = sorted(self.titles.values(), key=len, reverse=True)
        print("The longest titles are:")
        count = 0
        index = 0
        while count < 15 and index < len(titles):
            if titles[index].find("_") == -1:
                print(titles[index])
                count += 1
            index += 1
        print()


    # Example: Find the most linked pages.
    def find_most_linked_pages(self):
        link_count = {}
        for id in self.titles.keys():
            link_count[id] = 0

        for id in self.titles.keys():
            for dst in self.links[id]:
                link_count[dst] += 1

        print("The most linked pages are:")
        link_count_max = max(link_count.values())
        for dst in link_count.keys():
            if link_count[dst] == link_count_max:
                print(self.titles[dst], link_count_max)
        print()

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
    
    # Homework #3 (optional):
    # Search the longest path with heuristics.
    # 'start': A title of the start page.
    # 'goal': A title of the goal page.
    def find_longest_path(self, start, goal):
        start_id = self.find_id(start) # スタートのタイトルをページIDに変換
        goal_id = self.find_id(goal) # ゴールのタイトルをページIDに変換
        assert start_id is not None, f"開始ページ {start} が見つかりません"  # 見つからなければ即停止
        assert goal_id is not None, f"目標ページ {goal} が見つかりません"  # 見つからなければ即停止

        # リンクを逆向きにコピーする処理
        # 次のBFSでゴールから逆に辿るため
        reverse_links = collections.defaultdict(list) # {dst: [そこへ向かう元ノードたち]} を作る
        for src in self.links: # 全リンク元srcについて
            for dst in self.links[src]: # srcが張る各リンク先dstについて
                reverse_links[dst].append(src) # dst->src の逆向きで記録
        
        # ゴールから逆向きにBFSをし、各ノードからゴールまでの距離を計算する
        # ゴールに行けるノードのみを'dist_to_goal'に入れる
        dist_to_goal = {goal_id: 0} # ゴール自身までの距離は0
        bfs_queue = collections.deque([goal_id]) # BFSの探索キュー。ゴールから開始。       
        while bfs_queue: # キューが空になるまで
            node = bfs_queue.popleft() # 先頭ノードを取り出す
            for prev in reverse_links[node]: # nodeへ向かっていた一つ前のノードたちを見る
                if prev not in dist_to_goal: # まだ距離未確定（未訪問）なら
                    dist_to_goal[prev] = dist_to_goal[node] + 1 # nodeより1歩遠い距離を確定
                    bfs_queue.append(prev) # 次の探索対象としてキューに追加

        goal_preds = set(reverse_links[goal_id])

        # 最低でも返せる最短経路を最初に求めておく
        # 時間切れになってもゴールへ続く道が見つからなかったとき用
        def shortest_baseline():
            path = [start_id] # スタートから始める
            cur = start_id # 現在地
            while cur != goal_id: # ゴールにつくまで
                # 今いる場所からのリンク先を全て見て、'dist_to_goal'に入ってるもの(ゴールへ届いているもの)だけを残す
                # その中から'dist_to_goal'が一番小さいもの(ゴールに最も近いもの)を選ぶ
                nxt = min((c for c in self.links[cur] if c in dist_to_goal), key=lambda c: dist_to_goal[c])
                path.append(nxt) # 経路を伸ばす
                cur = nxt # 現在地を更新
            return path # スタート -> ゴールの最短経路を返す

        best_path = shortest_baseline() # まず最短経路を暫定の最長経路として確保
        
        TOTAL_TIME_LIMIT = 1000 # 探索全体の制限時間（秒）
        RESTART_INTERVAL = 300 # 1回の探索あたりの制限時間（秒）
        overall_deadline = time.time() + TOTAL_TIME_LIMIT # 全体の締め切り時刻
        
        # 'self.links.value()'を並び替える関数
        def make_iter(node):
            # ゴールに届かない行き先は最初から除外する
            # ゴール自身も除外
            children = [c for c in self.links[node] if c in dist_to_goal and c != goal_id]

            # 毎回違う経路を探索する
            random.shuffle(children)

            return iter(children)

        def run_once(slice_deadline):
            local_best = [] # 探索で見つかった最長経路を保存する
            visited = {start_id} # 今辿っている経路上で、すでに通ったノードの集合
            path = [start_id] # 今歩いている経路のノードIDのリスト
            stack = [make_iter(start_id)] # 各地点で次どこへ行くかの候補リスト
            reason = "dead_end"

            while stack:
                # 時間切れになったらやめる
                if time.time() > slice_deadline:
                    reason = "timeout"  
                    break
                node = path[-1]

                # ゴールへ直リンクしてるノードに来たら、その場で記録
                if node in goal_preds and len(path) + 1 > len(local_best):
                    local_best = path + [goal_id]

                # ゴールではない通常のノードにいるとき
                for child in stack[-1]:
                    # 今の経路で未訪問だったら進む
                    if child not in visited:
                        visited.add(child) # 経路に追加
                        path.append(child) # 経路を伸ばす
                        stack.append(make_iter(child)) # 候補iterを積む
                        break # 一つ選んだらfor文を抜ける

                # 子候補を全部試し終えた場合は、一つ戻る
                else:
                    path.pop() # 現在地を経路から取り除き、一つ前のノードに戻る
                    visited.discard(node) # 現在地の訪問済みフラグを解除する
                    stack.pop() # 現在地のイテレータもスタックから取り除く

            return local_best, reason
        
        restart = 0
        while time.time() < overall_deadline:
            slice_deadline = min(time.time() + RESTART_INTERVAL, overall_deadline)
            candidate, reason = run_once(slice_deadline) 
            print(f"[restart {restart}] len={len(candidate)-1 if candidate else 0} reason={reason}")
            if len(candidate) > len(best_path):
                best_path = candidate
                print(f"[restart {restart}] 経路長を更新: {len(best_path) - 1} ステップ")
            restart += 1

        self.assert_path(best_path, start, goal)
        print(f"\n最長経路 ({len(best_path)} ノード / {len(best_path) - 1} ステップ):")
        for i, p in enumerate(best_path):
            print(f"{i}: {self.titles[p]}")
        print()

    # Helper function for Homework #3:
    # Please use this function to check if the found path is well formed.
    # 'path': An array of page IDs that stores the found path.
    #     path[0] is the start page. path[-1] is the goal page.
    #     path[0] -> path[1] -> ... -> path[-1] is the path from the start
    #     page to the goal page.
    # 'start': A title of the start page.
    # 'goal': A title of the goal page.
    def assert_path(self, path, start, goal):
        assert(start != goal)
        assert(len(path) >= 2)
        assert(self.titles[path[0]] == start)
        assert(self.titles[path[-1]] == goal)
        for i in range(len(path) - 1):
            assert(path[i + 1] in self.links[path[i]])
        visited = {}
        for node in path:
            assert(node not in visited)
            visited[node] = True


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: %s pages_file links_file" % sys.argv[0])
        exit(1)

    wikipedia = Wikipedia(sys.argv[1], sys.argv[2])
    # Example
    # wikipedia.find_longest_titles()
    # Example
    # wikipedia.find_most_linked_pages()
    # Homework #1
    # wikipedia.find_shortest_path("渋谷", "パレートの法則")
    # Homework #2
    # wikipedia.find_most_popular_pages()
    # Homework #3 (optional)
    wikipedia.find_longest_path("渋谷", "池袋")