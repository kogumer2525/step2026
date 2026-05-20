# 辞書の各単語に、その文字をソートした文字列をつけてタプル化し、ソートして返す
# アナグラム同士でソートされた単語は同一なため、後に二分探索でまとめて取れるようにするため
def sort_dictionary(dictionary: list[str]) -> list[tuple[str, str]]:
    # (ソート済み文字列, 元の単語) のタプルを作る
    # 例："cab" -> ("abc", "cab")
    new_dictionary = [] 
    for word in dictionary:
        new_dictionary.append(("".join(sorted(word)), word))
    
    # タプルの第1要素（ソート済み文字列）で辞書順にソート
    new_dictionary.sort()
    return new_dictionary

# ソート済み文字列が、入力された単語(word)と一致する単語を二分探索ですべて取り出す
def binary_search(sorted_word: str, original_word: str, new_dictionary: list[str]) -> list[str]:
    # 二分探索
    # leftは条件を満たさない最大のindex, rightは満たす最小のindexとなる
    left, right = -1, len(new_dictionary)
    while right - left > 1:
        mid = (right + left) // 2
        if new_dictionary[mid][0] < sorted_word:
            left = mid # midはwordより小さい → 答えはもっと右
        else:
            right = mid # midはword以上 → 答え候補

    # rightから一つずつ右を見ていき、ソートずみの単語が入力された単語(word)と一致する単語を全て集める
    index = right
    ans = []
    while index < len(new_dictionary) and new_dictionary[index][0] == sorted_word:
        if new_dictionary[index][1] != original_word: # 入力された文字自身は除く
            ans.append(new_dictionary[index][1])
            index += 1 
    return ans

# 辞書ファイルを読み込んで1単語ずつのリストにする
with open("anagram/words.txt", "r") as file:
    dictionary = file.read().split("\n")

# 辞書を (ソート済み, 元単語) のソート済みリストに変換    
new_dictionary = sort_dictionary(dictionary)

# 入力された文字列をソートする
original_word = input("input word: ")
sorted_word = "".join(sorted(original_word))

# 二分探索でアナグラム候補をすべて取得
ans = binary_search(sorted_word, original_word, new_dictionary)
if ans:
    print(f"anagrams: {', '.join(ans)}")
else:
    print("no anagrams found")