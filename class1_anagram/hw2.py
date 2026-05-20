# execute: python hw2.py input_file_path output_file_path"
import sys

args = sys.argv
if len(args) != 3:
    print(f"command: python {args[0]} input_file_path output_file_path")
    exit()
input_file_path = args[1]
output_file_path = args[2]

# 文字を受け取り、a~zそれぞれが何回出現するかを数える
def count_word_num(word: str) -> list[int]:
    nums = [0] * 26
    for i in range(len(word)):
        nums[ord(word[i]) - ord('a')] += 1
    return nums

# （各文字の出現回数のリスト, 元の単語）が並んだ辞書を作成する
def count_dictionary(dictionary: list[str]) -> list[tuple[list[int], str]]:
    new_dictionary = [] 
    for word in dictionary:
        nums = count_word_num(word)
        new_dictionary.append((nums, word))
    return new_dictionary

# 各文字の出現回数のリストを参照し、入力された単語で辞書の単語が作れるかをチェックする
def check(word_nums: list[int], dictionary_nums: list[int]) -> bool:
    for i in range(26):
        if word_nums[i] < dictionary_nums[i]:
            return False
    return True

# スコア一覧（a~z）
SCORES = [1, 3, 2, 2, 1, 3, 3, 1, 1, 4, 4, 2, 2, 1, 1, 3, 4, 1, 1, 1, 2, 3, 3, 4, 3, 4]

# 単語の各文字に対応するスコアを計算して返す
def calculate_score(word):
    score = 0
    for character in list(word):
        score += SCORES[ord(character) - ord('a')]
    return score

# 辞書ファイルを読み込んで1単語ずつのリストにする
with open("anagram/words.txt", "r") as file:
    dictionary = file.read().split("\n")

# 辞書を (ソート済み, 元単語) のソート済みリストに変換    
new_dictionary = count_dictionary(dictionary)

# 入力された文字列をソートする
with open(input_file_path, "r") as file:
    words = file.read().split("\n")

max_words = []
for word in words:
    # 入力された文字列の各単語の個数を数える
    word_nums = count_word_num(word)

    # 辞書を一つ一つ見ていき、anagramになるもの選ぶ
    anagram_list = []
    for i in range(len(new_dictionary)):
        # 入力された単語で辞書の単語が作れるかをチェックする
        ans = check(word_nums, new_dictionary[i][0])
        if ans == True:
            anagram_list.append(new_dictionary[i][1]) # 後にスコアが一番高いものに絞るため、候補を全てanagram_listに入れる
    
    # anagramが存在する場合のみ、最高スコアの単語を選ぶ
    max_score = 0
    max_index = 0
    for i in range(len(anagram_list)):
        score = calculate_score(anagram_list[i])
        if score > max_score:
            max_index = i
            max_score = score
    if anagram_list:
        max_words.append(anagram_list[max_index])

# 結果をファイルに書き出す
with open(output_file_path, "w") as file:
    file.write("\n".join(max_words))