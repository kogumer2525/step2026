import random, sys, time

###########################################################################
#                                                                         #
# Implement a hash table from scratch!                                    #
#                                                                         #
# Please do not use Python's dictionary or Python's collections library.  #
# The goal is to implement the data structure yourself.                   #
#                                                                         #
###########################################################################

# Hash function.
#
# 'key': string
# Return value: a hash value
def calculate_hash(key):
    assert type(key) == str
    # 文字を29進数（アルファベット数26の次の素数）としてハッシュ化する
    # 各文字のコード値に位ごとの重み（29のi乗）を掛け手たし合わせる（文字の並び順によって違うハッシュ値にするため）
    hash = 0
    for i in range(len(key)):
        hash += ord(key[i]) * (29**i)
    return hash


# An item object that represents one key - value pair in the hash table.
class Item:
    # 'key': The key of the item. The key must be a string.
    # 'value': The value of the item.
    # 'next': The next item in the linked list. If this is the last item in the
    #         linked list, 'next' is None.
    def __init__(self, key, value, next):
        assert type(key) == str
        self.key = key
        self.value = value
        self.next = next


# The main data structure of the hash table that stores key - value pairs.
# The key must be a string. The value can be any type.
#
# 'self.bucket_size': The bucket size.
# 'self.buckets': An array of the buckets. self.buckets[hash % self.bucket_size]
#                 stores a linked list of items whose hash value is 'hash'.
# 'self.item_count': The total number of items in the hash table.
class HashTable:

    # Initialize the hash table.
    def __init__(self):
        # Set the initial bucket size to 97. A prime number is chosen to reduce
        # hash conflicts.
        self.bucket_size = 97
        self.buckets = [None] * self.bucket_size
        self.item_count = 0

    # ハッシュテーブルの大きさを変えて、全アイテムを入れ直す
    #
    # 'flag': テーブルを小さくしたい・大きくしたいかを判別する
    def rehash(self, flag):
        old_buckets = self.buckets # 古いテーブルを、新しく入れ直す前にコピーしておく
        if flag == "bigger":
            self.bucket_size = self.bucket_size * 2 - 1 # テーブルのサイズを2倍にする
        else:
            self.bucket_size = self.bucket_size // 2 if self.bucket_size > 2 else 1 # テーブルのサイズを半分にする
        self.buckets = [None] * self.bucket_size
        # 古いテーブルのitemを取り出し、新しいテーブルに全itemを入れ直す
        for buckets in old_buckets:
            current = buckets
            # リストを辿ってitemを取り出す
            while current is not None:
                # 新しいテーブルに全itemを入れ直す
                hash = calculate_hash(current.key) % self.bucket_size
                self.buckets[hash] = Item(current.key, current.value, self.buckets[hash])
                current = current.next

    # Put an item to the hash table. If the key already exists, the
    # corresponding value is updated to a new value.
    #
    # 'key': The key of the item.
    # 'value': The value of the item.
    # Return value: True if a new item is added. False if the key already exists
    #               and the value is updated.
    def put(self, key, value):
        assert type(key) == str
        check_size(self.size(), self.bucket_size)  # Don't remove this code.
        # アイテム数がテーブルサイズの7割を超えていたら、テーブルを大きくする
        if self.item_count > self.bucket_size * 0.7:
            self.rehash("bigger")
        # ハッシュを計算し、テーブルの先頭に入れる
        # リストをたどり、衝突がないかを確認する。衝突した場合は入れ替える。
        hash = calculate_hash(key) % self.bucket_size
        # 該当するハッシュのリストを辿り、同じキーが既に存在するかを確認する
        current = self.buckets[hash]
        while current is not None:
            # 同じキーがあれば値だけ上書きし、Falseを返す
            if current.key == key:
                current.value = value
                return False
            current = current.next
        # 同じキーが無かった場合、新しいItemをリストの先頭に追加する
        self.buckets[hash] = Item(key, value, self.buckets[hash])
        self.item_count += 1
        return True

    # Get an item from the hash table.
    #
    # 'key': The key.
    # Return value: If the item is found, return (the value of the item, True).
    #               Otherwise, return (None, False).
    def get(self, key):
        assert type(key) == str
        check_size(self.size(), self.bucket_size)  # Don't remove this code.
        # 該当するハッシュのリストをたどり、欲しいアイテムと一致するものを探す
        hash = calculate_hash(key) % self.bucket_size
        current = self.buckets[hash]
        while current is not None:
            # 見つかったら（値, True）を返す
            if current.key == key:
                return (current.value, True)
            current = current.next
        # 最後まで見つからなければ（None, False）を返す
        return (None, False)

    # Delete an item from the hash table.
    #
    # 'key': The key.
    # Return value: True if the item is found and deleted successfully. False
    #               otherwise.
    def delete(self, key):
        assert type(key) == str
        hash = calculate_hash(key) % self.bucket_size
        current = self.buckets[hash]
        before = None # 一つ前に見ていたハッシュ
        # 該当するハッシュのリストをたどり、削除したいアイテムと一致するものを探す
        while current is not None:
            # 見つかったらリストから外す
            if current.key == key:
                if before:
                    # 前のItemのnextを、削除する要素の次に繋げる
                    before.next = current.next
                else:
                    # 削除したい要素がリストの先頭だった場合
                    # リスト先頭を次の要素に差し替える
                    self.buckets[hash] = current.next
                self.item_count -= 1
                # itemの削除に成功した場合、アイテム数がテーブルサイズの3割を切ったら、テーブルを縮小する
                if self.item_count < self.bucket_size * 0.3:
                    self.rehash("smaller")
                return True
            # 見つからなかった場合、一つ見るリストを進める
            before = current
            current = current.next
         # 最後まで見つからなければ削除失敗としてFalseを返す
        return False

    # Return the total number of items in the hash table.
    def size(self):
        return self.item_count


# Check that the hash table has a "reasonable" bucket size.
# The bucket size is judged "reasonable" if it is smaller than 100 or
# the buckets are 30% or more used.
#
# Note: Don't change this function.
def check_size(item_count, bucket_size):
    assert (bucket_size < 100 or item_count >= bucket_size * 0.3)


# Test the functional behavior of the hash table.
def functional_test():
    hash_table = HashTable()

    assert hash_table.put("aaa", 1) == True
    assert hash_table.get("aaa") == (1, True)
    assert hash_table.size() == 1

    assert hash_table.put("bbb", 2) == True
    assert hash_table.put("ccc", 3) == True
    assert hash_table.put("ddd", 4) == True
    assert hash_table.get("aaa") == (1, True)
    assert hash_table.get("bbb") == (2, True)
    assert hash_table.get("ccc") == (3, True)
    assert hash_table.get("ddd") == (4, True)
    assert hash_table.get("a") == (None, False)
    assert hash_table.get("aa") == (None, False)
    assert hash_table.get("aaaa") == (None, False)
    assert hash_table.size() == 4

    assert hash_table.put("aaa", 11) == False
    assert hash_table.get("aaa") == (11, True)
    assert hash_table.size() == 4

    assert hash_table.delete("aaa") == True
    assert hash_table.get("aaa") == (None, False)
    assert hash_table.size() == 3

    assert hash_table.delete("a") == False
    assert hash_table.delete("aa") == False
    assert hash_table.delete("aaa") == False
    assert hash_table.delete("aaaa") == False

    assert hash_table.delete("ddd") == True
    assert hash_table.delete("ccc") == True
    assert hash_table.delete("bbb") == True
    assert hash_table.get("aaa") == (None, False)
    assert hash_table.get("bbb") == (None, False)
    assert hash_table.get("ccc") == (None, False)
    assert hash_table.get("ddd") == (None, False)
    assert hash_table.size() == 0

    assert hash_table.put("abc", 1) == True
    assert hash_table.put("acb", 2) == True
    assert hash_table.put("bac", 3) == True
    assert hash_table.put("bca", 4) == True
    assert hash_table.put("cab", 5) == True
    assert hash_table.put("cba", 6) == True
    assert hash_table.get("abc") == (1, True)
    assert hash_table.get("acb") == (2, True)
    assert hash_table.get("bac") == (3, True)
    assert hash_table.get("bca") == (4, True)
    assert hash_table.get("cab") == (5, True)
    assert hash_table.get("cba") == (6, True)
    assert hash_table.size() == 6

    assert hash_table.delete("abc") == True
    assert hash_table.delete("cba") == True
    assert hash_table.delete("bac") == True
    assert hash_table.delete("bca") == True
    assert hash_table.delete("acb") == True
    assert hash_table.delete("cab") == True
    assert hash_table.size() == 0

    # Test the rehashing.
    for i in range(100):
        hash_table.put(str(i), str(i))
    for i in range(100):
        assert hash_table.get(str(i)) == (str(i), True)
    for i in range(100):
        assert hash_table.delete(str(i)) == True
    hash_table.put("abc", 1)
    hash_table.put("acb", 2)
    assert hash_table.get("abc") == (1, True)
    assert hash_table.get("acb") == (2, True)
    print("Functional tests passed!")


# Test the performance of the hash table.
#
# Your goal is to make the hash table work with mostly O(1).
# If the hash table works with mostly O(1), the execution time of each iteration
# should not depend on the number of items in the hash table. To achieve the
# goal, you will need to 1) implement rehashing (Hint: expand / shrink the hash
# table when the number of items in the hash table hits some threshold) and
# 2) tweak the hash function (Hint: think about ways to reduce hash conflicts).
def performance_test():
    hash_table = HashTable()

    for iteration in range(100):
        begin = time.time()
        random.seed(iteration)
        for i in range(10000):
            rand = random.randint(0, 100000000)
            hash_table.put(str(rand), str(rand))
        random.seed(iteration)
        for i in range(10000):
            rand = random.randint(0, 100000000)
            hash_table.get(str(rand))
        end = time.time()
        print("%d %.6f" % (iteration, end - begin))

    for iteration in range(100):
        random.seed(iteration)
        for i in range(10000):
            rand = random.randint(0, 100000000)
            hash_table.delete(str(rand))

    assert hash_table.size() == 0
    print("Performance tests passed!")


if __name__ == "__main__":
    functional_test()
    performance_test()
