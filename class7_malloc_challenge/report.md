
## 1. Best-fit mallocに改造する

### 方針

- フリーリストを辿っていき、metadataを探索
- 入れたいデータの`size`以上の空き領域の中から、最小のものを選択：
  - 見つけた空き領域が`size`以上であれば、今まで見つけた空き領域と比較し、より小さいほうを採用していく
- 既存のmetadataをフリーリストから削除。余りがあれば、残りを空きスロットとしてフリーリストに戻す

### 結果

```
Welcome to the malloc challenge!
size_of(uint8_t *) = 8
size_of(size_t) = 8
Running tests...
Finished!

====================================================
Challenge #1    |   simple_malloc =>       my_malloc
--------------- + --------------- => ---------------
       Time [ms]|               8 =>            1584
Utilization [%] |              70 =>              70
====================================================
Challenge #2    |   simple_malloc =>       my_malloc
--------------- + --------------- => ---------------
       Time [ms]|               6 =>            1130
Utilization [%] |              40 =>              40
====================================================
Challenge #3    |   simple_malloc =>       my_malloc
--------------- + --------------- => ---------------
       Time [ms]|             129 =>            1381
Utilization [%] |               9 =>              51
====================================================
Challenge #4    |   simple_malloc =>       my_malloc
--------------- + --------------- => ---------------
       Time [ms]|           13077 =>            9516
Utilization [%] |              15 =>              72
====================================================
Challenge #5    |   simple_malloc =>       my_malloc
--------------- + --------------- => ---------------
       Time [ms]|           12029 =>            6032
Utilization [%] |              15 =>              75

Challenge done!
Please copy & paste the following data in the score sheet!
1584,70,1130,40,1381,51,9516,72,6032,75,
```

### コード

```C
void *my_malloc(size_t size) {
  my_metadata_t *metadata = my_heap.free_head;
  my_metadata_t *prev = NULL;
  
  // Best-fit
  // 全スロットを走査し、sizeが入るものの中で最も余りが小さいスロットを選ぶ

  my_metadata_t *min_free_slot = NULL; // これまでの最良候補
  my_metadata_t *prev_metadata = NULL; // ループ上の直前のスロット

  // 最後まで探す
  while (metadata != NULL) {

    // このスロットにsizeが入るとき
    if (metadata->size >= size) {

      // まだ候補が一つもない時
      // 無条件で最初の候補とする
      if (min_free_slot == NULL) {
        min_free_slot = metadata;
        prev = prev_metadata; // この候補の直前のスロットを保存
      } 
      // 既に候補があった時
      else {
        // より余りが小さい(sizeが小さい)なら最良候補を入れ替える
        if (metadata->size < min_free_slot->size) {
          min_free_slot = metadata;
          prev = prev_metadata; // 入れ替えた候補の直前のスロットを保存
        }

      }
    }
    prev_metadata = metadata; // 次のスロットへ進む前に直前のスロットを更新する
    metadata = metadata->next; // 次のスロットへ進む
  }

  // 後段はFirst-fitと同じ変数を使うので、
  // 選んだ最良スロットをmetadataに渡す
  metadata = min_free_slot;
```

