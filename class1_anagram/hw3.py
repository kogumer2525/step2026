import sys

if len(sys.argv) != 3:
    print("使い方: python script.py <入力ファイル> <出力ファイル>")
    print("例: python script.py anagram/large.txt large_answer.txt")
    sys.exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2]

# スコア一覧（a~z）
SCORES = [1, 3, 2, 2, 1, 3, 3, 1, 1, 4, 4, 2, 2, 1, 1, 3, 4, 1, 1, 1, 2, 3, 3, 4, 3, 4]

# 単語の各文字に対応するスコアを計算して返す
# 例: "cat" -> c(2) + a(1) + t(1) = 4
def calculate_score(word):
    score = 0
    for character in list(word):
        score += SCORES[ord(character) - ord('a')]
    return score

# 文字を受け取り、a~zそれぞれが何回出現するかを数えた26要素のリストを返す
# 例: "cat" -> [1,0,1,0,...,1,...] (a=1, c=1, t=1)
def count_word_num(word: str) -> list[int]:
    nums = [0] * 26
    for i in range(len(word)):
        nums[ord(word[i]) - ord('a')] += 1
    return nums

# 辞書全体を、（各文字の出現回数のリスト, 元の単語, スコア, 単語数）のタプルが並んだリストに変換する
def count_dictionary(dictionary: list[str]) -> list[tuple[list[int], str]]:
    new_dictionary = [] 
    for word in dictionary:
        # 空行は辞書として無効なのでスキップ
        if not word:
            continue
        nums = count_word_num(word)
        score = calculate_score(word)
        length = len(word)
        new_dictionary.append((nums, word, score, length))
    return new_dictionary

# 各文字の出現回数のリストを参照し、入力された単語で辞書の単語が作れるかをチェックする
def check(word_nums: list[int], dictionary_nums: list[int]) -> bool:
    for i in range(26):
        if word_nums[i] < dictionary_nums[i]:
            return False
    return True

# DFSで、見込みなしとして探索を打ち切る基準を定める
# スコア効率順（一文字に対するスコア順）にソート済みの候補リストを上から見て、作れる単語を片っ端から採用する
def initialize_dfs(anagram_list, word_nums):
    remaining = list(word_nums)
    chosen = []
    sum_score = 0
    for nums, word, score, length in anagram_list:
        if check(remaining, nums):
            for i in range(26):
                remaining[i] -= nums[i]
            chosen.append(word)
            sum_score += score
    return sum_score, chosen

# インデックスi以降の候補の中で、一文字に対するスコアが最も高い値を計算する
# DFSで「ここから取れる最大スコアの上限」を見積もり、計算量を減らすために使う
def calculate_max_eff(anagram_list):
    n = len(anagram_list)
    max_eff = [0.0] * (n+1)
    for i in range(n-1, -1, -1): # max_eff[i+1]が分かれば、max_eff[i]はそれと「自分の効率」のmaxで決まる
        # スコア/単語数 で一文字に対するスコアを求める
        # max_eff[i]はインデックスi以降の候補の中で、一文字に対するスコアが最も高い値
        max_eff[i] = max(max_eff[i+1], anagram_list[i][2]/anagram_list[i][3])
    return max_eff
            
# 辞書ファイルを読み込み、(文字数, 単語, スコア, 長さ) のリストに変換
with open("anagram/words.txt", "r") as file:
    dictionary = file.read().split("\n")
new_dictionary = count_dictionary(dictionary)

# 入力ファイルを読み込む
with open(input_file, "r") as file:
    words = file.read().split("\n")

max_words = []
# 入力ファイルの各行を順に処理
for word in words:
    # 文字数を数える
    word_nums = count_word_num(word)

    # 辞書を一つ一つ見ていき、anagramになる候補選ぶ
    # 同じ文字構成のアナグラムは1つだけ残す（例: cat/act/tacはいずれか一つだけ残す。スコアは同じため。）
    anagram_list = [] # anagramになる候補を格納するリスト
    seen_counts = set() # 同じ文字構成のアナグラムの重複を防ぐためのセット
    for i in range(len(new_dictionary)):
        if check(word_nums, new_dictionary[i][0]):
            key = tuple(new_dictionary[i][0])
            if key not in seen_counts:
                seen_counts.add(key)
                anagram_list.append(new_dictionary[i])
    
    # スコア効率（一文字に対するスコア）の高い順にソート
    anagram_list.sort(key=lambda x: x[2]/x[3], reverse=True)

    # インデックスi以降の最大効率を前計算
    max_eff = calculate_max_eff(anagram_list)

    # DFSで、見込みなしとして探索を打ち切る基準を定める
    init_score, init_words = initialize_dfs(anagram_list, word_nums)
    best_score = [init_score] # 暫定ベストスコア
    best_words = [init_words] # 暫定ベストの単語リスト

    # 理論上の最大スコアの計算
    # 入力文字を全部使い切った時以上のスコアにすることは不可能なため
    theoretical_max = calculate_score(word)
    # initialize_dfs関数で求めれたスコアがすでに理論上の最大に到達していたらDFSは不要
    found_optimal = [best_score[0] >= theoretical_max]

    remaining = list(word_nums) # まだ単語作りに使える文字の内訳(DFS中に書き換えながら使う)
    chosen = [] # 現在採用中の単語リスト(DFS中に書き換えながら使う)
    n = len(anagram_list)
    # 候補リストから、複数の単語の最良の組み合わせを探す
    # start_idx: anagram_listの探索開始のインデックス
    # current_score: 現在採用中の単語のスコア合計
    # remaining_total: 残っている文字の総数
    def dfs(start_idx, current_score, remaining_total):
        # 理論上の最大に到達したら終了
        if found_optimal[0]:
            return
        
        # 今のスコアが暫定ベストより良ければ更新
        if current_score > best_score[0]:
            best_score[0] = current_score
            best_words[0] = list(chosen)
            # 理論上の最大に到達したら終了
            if best_score[0] >= theoretical_max:
                found_optimal[0] = True
                return
        
        # 「現在のスコア + 残り文字数 × 残り候補の最大効率」が暫定ベストを超えないなら、この枝の先を最後まで探索しても無駄なので諦める（anagram_listはスコア効率順に並んでいるため）
        if current_score + remaining_total * max_eff[start_idx] <= best_score[0]:
            return
        
        # start_idx以降の候補を順に試す
        for i in range(start_idx, n):
            if found_optimal[0]:
                return
            
            nums_i, word_i, score_i, length_i = anagram_list[i]

            # 「現在のスコア + 残り文字数 × 残り候補の最大効率」が暫定ベストを超えないなら、この枝の先を最後まで探索しても無駄なので諦める（anagram_listはスコア効率順に並んでいるため）
            if current_score + remaining_total * max_eff[i] <= best_score[0]:
                return
            
            # この単語を作るのに必要な文字が足りているかチェック
            if not check(remaining, nums_i):
                continue

            # 使える文字を消費して、chosenに追加
            for k in range(26):
                remaining[k] -= nums_i[k]
            chosen.append(word_i)

            # 再帰
            # この単語を採用した状態で、次の単語（i+1以降）を探しにいく
            dfs(i+1, current_score + score_i, remaining_total - length_i)
            
            # 別の選択肢を試すために、消費した文字を戻す
            chosen.pop()
            for k in range(26):
                remaining[k] += nums_i[k]
    # DFS実行
    if not found_optimal[0]:
        # 再帰深度を上げておく
        sys.setrecursionlimit(max(10000, n + 1000))
        dfs(0, 0, sum(word_nums))
    
    # この行の答えを記録
    max_words.append(" ".join(best_words[0]))

# 結果をファイルに書き出す
with open(output_file, "w") as file:
    file.write("\n".join(max_words))