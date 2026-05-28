import random, sys
import hash_table # Use the hash table you implemented in Homework #2

###########################################################################
#                                                                         #
# Implement a cache that stores the most recently accessed items from     #
# scratch!                                                                #
#                                                                         #
# Please do not use Python's dictionary or Python's collections library.  #
# The goal is to implement the data structure yourself.                   #
#                                                                         #
###########################################################################

class Page:
    def __init__(self, url, contents):
        # URL
        self.url = url
        # The contents of the URL
        self.contents = contents
        # Previous page
        self.prev = None
        # Next page
        self.next = None

        
class Cache:
    # Initialize the cache.
    # 'limit': The size limit of the cache.
    def __init__(self, limit):
        assert(limit >= 1)
        self.limit = limit
        self.hit_count = 0 # Increment on a cache hit
        self.miss_count = 0 # Increment on a cache miss
        self.cache_count = 0 # キャッシュに入っているページ数
        self.head = Page(None, None) # キャッシュの先頭（新しい）
        self.tail = Page(None, None) # キャッシュの末端（古い）
        self.head.next = self.tail
        self.tail.prev = self.head
        self.hashtable = hash_table.HashTable() # urlとキャッシュへのポインタを対応させるためのハッシュテーブル

    # Access a page and update the cache so that it stores the most recently
    # accessed pages up to the 'limit'. This needs to be done with mostly O(1).
    # 'url': The accessed URL
    # 'contents': The contents of the URL
    def access_page(self, url, contents):
        assert type(url) == str
        # ハッシュテーブルからURLに対応するページを探す
        page, result = self.hashtable.get(url)
        if result:
            # ハッシュテーブルに既にページが入っていた場合、キャッシュ先頭に移動
            self.hit_count += 1
            # キャッシュの現在の位置からページを外す
            page.prev.next = page.next
            page.next.prev = page.prev
            # キャッシュの先頭に入れる
            page.prev = self.head
            page.next = self.head.next
            self.head.next.prev = page
            self.head.next = page
        else:
            # ページがハッシュテーブルにない場合、新しいページを作成
            self.miss_count += 1
            page = Page(url, contents)
            # キャッシュが満杯だった場合（新ページを先頭に入れ、末尾のページを削除）
            if self.cache_count == self.limit:
                # ハッシュテーブルから一番古いページを削除する
                self.hashtable.delete(self.tail.prev.url)
                # キャッシュ末尾のページを外す
                self.tail.prev.prev.next = self.tail
                self.tail.prev = self.tail.prev.prev
                # キャッシュ先頭に新しいページを入れる
                page.next = self.head.next
                page.prev = self.head
                self.head.next.prev = page
                self.head.next = page
                # ハッシュテーブルに新しいページを入れる
                self.hashtable.put(url, page)
            # キャッシュに空きがあった場合（新ページを先頭に入れる）
            else:
                # キャッシュ先頭に新しいページを入れる
                page.next = self.head.next
                page.prev = self.head
                self.head.next.prev = page
                self.head.next = page
                # ハッシュテーブルに新しいページを入れる
                self.hashtable.put(url, page)
                # キャッシュのページ数のカウントを増やす
                self.cache_count += 1

    # Return the URLs stored in the cache. The URLs are ordered in the order
    # in which the URLs are mostly recently accessed.
    # Return value: [url, url, ...]
    def get_pages(self):
        url_list = []
        page = self.head.next
        while page != self.tail:
            url_list.append(page.url)
            page = page.next
        return url_list


    # Return the cache hit rate.
    def get_hitrate(self):
        total = self.hit_count + self.miss_count
        return self.hit_count / total if total > 0 else 0

    
def cache_test():
    # Set the size of the cache to 4.
    cache = Cache(4)

    # Initially, no page is cached.
    assert cache.get_pages() == []

    # Access "a.com".
    cache.access_page("a.com", "AAA")
    # "a.com" is cached.
    assert cache.get_pages() == ["a.com"]

    # Access "b.com".
    cache.access_page("b.com", "BBB")
    # The cache is updated to:
    #   (new)<-- "b.com", "a.com" -->(old)
    assert cache.get_pages() == ["b.com", "a.com"]

    # Access "c.com".
    cache.access_page("c.com", "CCC")
    # The cache is updated to:
    #   (new)<-- "c.com", "b.com", "a.com" -->(old)
    assert cache.get_pages() == ["c.com", "b.com", "a.com"]

    # Access "d.com".
    cache.access_page("d.com", "DDD")
    # The cache is updated to:
    #   (new)<-- "d.com", "c.com", "b.com", "a.com" -->(old)
    assert cache.get_pages() == ["d.com", "c.com", "b.com", "a.com"]

    # Access "d.com" again.
    cache.access_page("d.com", "DDD")
    # The cache is updated to:
    #   (new)<-- "d.com", "c.com", "b.com", "a.com" -->(old)
    assert cache.get_pages() == ["d.com", "c.com", "b.com", "a.com"]

    # Access "a.com" again.
    cache.access_page("a.com", "AAA")
    # The cache is updated to:
    #   (new)<-- "a.com", "d.com", "c.com", "b.com" -->(old)
    assert cache.get_pages() == ["a.com", "d.com", "c.com", "b.com"]

    cache.access_page("c.com", "CCC")
    assert cache.get_pages() == ["c.com", "a.com", "d.com", "b.com"]
    cache.access_page("a.com", "AAA")
    assert cache.get_pages() == ["a.com", "c.com", "d.com", "b.com"]
    cache.access_page("a.com", "AAA")
    assert cache.get_pages() == ["a.com", "c.com", "d.com", "b.com"]

    # Access "e.com".
    cache.access_page("e.com", "EEE")
    # The cache is full, so we remove the least recently accessed page "b.com".
    # The cache is updated to:
    #   (new)<-- "e.com", "a.com", "c.com", "d.com" -->(old)
    assert cache.get_pages() == ["e.com", "a.com", "c.com", "d.com"]

    # Access "f.com".
    cache.access_page("f.com", "FFF")
    # The cache is full, so we remove the least recently accessed page "c.com".
    # The cache is updated to:
    #   (new)<-- "f.com", "e.com", "a.com", "c.com" -->(old)
    assert cache.get_pages() == ["f.com", "e.com", "a.com", "c.com"]

    # Access "e.com".
    cache.access_page("e.com", "EEE")
    # The cache is updated to:
    #   (new)<-- "e.com", "f.com", "a.com", "c.com" -->(old)
    assert cache.get_pages() == ["e.com", "f.com", "a.com", "c.com"]

    # Access "a.com".
    cache.access_page("a.com", "AAA")
    # The cache is updated to:
    #   (new)<-- "a.com", "e.com", "f.com", "c.com" -->(old)
    assert cache.get_pages() == ["a.com", "e.com", "f.com", "c.com"]

    print("Tests passed!")


def performance_test():
    # Set the size of the cache to 100.
    cache = Cache(100)

    # Generate queries based on the Zipf law.
    ALPHA = 1.5
    NUM_QUERIES = 1000000
    NUM_PAGES = 1000
    ranks = range(1, NUM_PAGES + 1)
    weights = [1.0 / (r ** ALPHA) for r in ranks]
    random.seed(1)
    queries = random.choices(ranks, weights=weights, k=NUM_QUERIES)    
    for query in queries:
        cache.access_page(str(query), "")

    # If your cache implementation is correct, the hit rate will be 91%.
    print("Cache hit rate = %d %%" % (cache.get_hitrate() * 100))
    print("Performance tests passed!")


if __name__ == "__main__":
    cache_test()
    performance_test()
