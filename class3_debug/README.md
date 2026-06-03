## 問題

- モジュール化された計算機プログラムを作成する
  - 宿題1: 「+」「-」「*」「/」 に対応
  - 宿題2: テストケースを追加する
  - 宿題3: 括弧に対応
  - 宿題4: abs(), int(), round()に対応
  
## 考えたこと

- **乗算・除算の処理**
  - 乗算・除算を先に処理する
  - 乗算・除算のトークンと元の数値トークンを、計算結果の数値トークンと入れ替える
- **括弧の処理**
  - 右括弧')'を見つけたら、左に戻って対応する'('を探す
  - 見つけた右括弧を順番に処理していくことで、括弧を内側から処理する
- **`abs/int/round`の処理**
  - 括弧の中身を計算した後に、括弧の直前に`abs/int/round`のトークンがあれば適用する。
  
## コード説明

### read_number関数（変更なし）

```python
# 数字を読み込む関数
# line: 入力された数式の文字全体
# index: 今文字列の何文字目を読んでいるのかの位置
# 戻り値: (作ったNUMBERトークン、次に読むべき位置)
def read_number(line, index):
    # 数字の合計を表す変数
    number = 0

    # 上の桁から一つずつ読む。10倍して桁をずらしていく。
    while index < len(line) and line[index].isdigit():
        number = number * 10 + int(line[index])
        index += 1

    # 小数点以下の数値を読み取る 
    if index < len(line) and line[index] == '.':
        index += 1
        decimal = 0.1
        # 読むたびに割る数を10倍していく
        while index < len(line) and line[index].isdigit():
            number += int(line[index]) * decimal
            decimal /= 10
            index += 1

    token = {'type': 'NUMBER', 'number': number}
    return token, index
```

### トークンを作成する関数

- `read_times`・`read_divide`・`read_left_brackets`・`read_right_brackets`・`read_abs`・`read_int`・`read_round`関数を追加
- `read_abs`・`read_int`・`read_round`関数は、それぞれの文字数分indexを進めて返す
  - 次の文字列から読み始めるため

```python
# '+'トークンを生成して返す関数
def read_plus(line, index):
    token = {'type': 'PLUS'}
    return token, index + 1

# '-'トークンを生成して返す関数
def read_minus(line, index):
    token = {'type': 'MINUS'}
    return token, index + 1

# '*'トークンを生成して返す関数
def read_times(line, index):
    token = {'type': 'TIMES'}
    return token, index + 1

# '/'トークンを生成して返す関数
def read_divide(line, index):
    token = {'type': 'DIVIDE'}
    return token, index + 1

# '('トークンを生成して返す関数
def read_left_brackets(line, index):
    token = {'type': 'LEFT_BRACKETS'}
    return token, index + 1

# ')'トークンを生成して返す関数
def read_right_brackets(line, index):
    token = {'type': 'RIGHT_BRACKETS'}
    return token, index + 1

# 'abs'トークンを生成して返す関数
def read_abs(line, index):
    token = {'type': 'ABS'}
    return token, index + 3

# 'int'トークンを生成して返す関数
def read_int(line, index):
    token = {'type': 'INT'}
    return token, index + 3

# 'round'トークンを生成して返す関数
def read_round(line, index):
    token = {'type': 'ROUND'}
    return token, index + 5
```

### evaluate_brackets関数（括弧の処理）

- 右括弧')'を見つけ次第処理開始
- 順に左を見ていき一番最初に出てくる左括弧'（'を探す
- 括弧の中身を計算し、結果を出す。
- `evaluate_abs_int_round`関数に結果を渡し、必要であれば`abs/int/round`の処理を行う。

```python
# 括弧()を処理する関数
# tokens: トークンのリスト
# 戻り値: 括弧の中身とそれに付随する関数を処理後のトークンのリスト
def evaluate_brackets(tokens):
    index = 0
    while index < len(tokens):
        # 右括弧')'を見つけたら、その内側の括弧を処理する
        if tokens[index]['type'] == 'RIGHT_BRACKETS':

            # 対応する左括弧'('を左方向に探していく
            # 右括弧')'から最初に見つかる'('が、必ずペアになる
            current_left_index = index-1
            while tokens[current_left_index]['type'] != 'LEFT_BRACKETS':
                current_left_index -= 1 # もう1つ左を探す

            # '('と')'の間（括弧の中身）だけを取り出す
            brackets_tokens = tokens[current_left_index+1:index]

            # 括弧部分（括弧の中身と右括弧')' ）をトークン列から取り除く
            # 左括弧'('は後に括弧内の計算結果を入れるために残しておく（current_left_index+1まで含める）
            tokens = tokens[:current_left_index+1]+tokens[index+1:]

            # 括弧の中身を計算（'+' '-' '*' '/' を処理）
            ans_num = evaluate_plus_and_minus(brackets_tokens)

            # 計算結果に、必要なら関数（abs/int/round）を適用してトークンに反映
            tokens = evaluate_abs_int_round(tokens, current_left_index, ans_num)

            # トークンを削除した分、手前の位置から見直す
            index = current_left_index-1
        index += 1
    return tokens
```

### evaluate_abs_int_round関数（abs/int/roundの処理）

- 括弧の中身を計算した結果に、関数（abs/int/round）を適用する。
- 左括弧の直前が関数名（ABS/INT/ROUND）トークンかどうかで分岐する。
  - 直前に関数名（ABS/INT/ROUND）トークンがあるとき：計算結果の数値トークンを、関数名トークンと入れ替える
  - 直前に関数名トークンがないとき：左括弧の関数名トークンを、計算結果の数値トークンと入れ替える

```python
# 括弧の中身を計算した結果に、関数(abs/int/round)を適用する関数
# tokens: トークンのリスト
# current_left_index: 左括弧'('があった位置。ここに(abs/int/round)適用後の結果を入れる。
# ans_num: 括弧の中身を計算した結果
# 戻り値: トークンのリスト
def evaluate_abs_int_round(tokens, current_left_index, ans_num):
    # 括弧の直前（current_left_index）が'abs'だったらその関数を適用する
    if tokens[current_left_index-1]['type'] == 'ABS':
        # ABSトークンを、結果のNUMBERトークンで上書き
        tokens[current_left_index-1] = {'type': 'NUMBER', 'number': abs(ans_num)}
        # 残っている'('トークンを削除
        tokens.pop(current_left_index)
        return tokens
    # 括弧の直前が'int'だったらint関数を適用
    elif tokens[current_left_index-1]['type'] == 'INT':
        # INTトークンを、結果のNUMBERトークンで上書き
        tokens[current_left_index-1] = {'type': 'NUMBER', 'number': int(ans_num)}
        # 残っている'('トークンを削除
        tokens.pop(current_left_index)
        return tokens
    # 括弧の直前が'round'だったらround関数を適用
    elif tokens[current_left_index-1]['type'] == 'ROUND':
        # ROUNDトークンを、結果のNUMBERトークンで上書き
        tokens[current_left_index-1] = {'type': 'NUMBER', 'number': round(ans_num)}
        # 残っている'('トークンを削除
        tokens.pop(current_left_index)
        return tokens
    # '('の直前が関数(abs/int/round)でなければ、'('の位置に括弧の計算結果をそのまま置く
    else:
        tokens[current_left_index] = {'type': 'NUMBER', 'number': ans_num}
        return tokens
```

### evaluate_times_and_divide関数（乗算・除算の処理）

- 乗算・除算を先に処理し、トークンを減らす（掛け割り>足し引きの優先順位）
- 乗算・除算の計算をしたら、式の左側の数値トークンを、結果の数値トークンに置き換える。乗算・除算のトークンと、元の式の右側の数値トークンをpopで除く。
  - 例：3*5
    - 処理前のトークンリスト：{'type': 'NUMBER', 'number': 3}, {'type': 'PLUS'}, {'type': 'NUMBER', 'number': 5}
    - 処理後のトークンリスト：{'type': 'NUMBER', 'number': 15}
  
```python
# 掛け算・割り算を先に計算する関数
# 先に'*','/'を計算してトークンリストから減らす
# tokens: 作成したトークンの文字列分のリスト
# 戻り値: '*' '/'を計算してトークンリストから抜いたもの。
#        足し算・引き算・数字のトークンが残っている。
def evaluate_times_and_divide(tokens):
    index = 0

    # トークンリストを最後まで順に見ていく
    while index < len(tokens):
        # 数値トークンを見つけた場合
        if tokens[index]['type'] == 'NUMBER':

            # そのひとつ前が'*'なら乗算して結果をトークンに上書き
            if tokens[index - 1]['type'] == 'TIMES':
                times_ans = tokens[index-2]['number'] * tokens[index]['number'] # 「2つ前の数値」*「今の数値」で乗算
                tokens[index-2]['number'] = times_ans
                tokens.pop(index) # 今の位置の数値トークンを削除
                tokens.pop(index-1) # 1つ前の'*'トークンを削除
                index -= 2 # 削除した分、見る位置を戻す
            
            # そのひとつ前が'/'なら割算して結果をトークンに上書き
            elif tokens[index - 1]['type'] == 'DIVIDE':
                divide_ans = tokens[index-2]['number'] / tokens[index]['number'] # 「2つ前の数値」*「今の数値」で減算
                tokens[index-2]['number'] = divide_ans # 減算の結果を2つ前の数値トークンに上書き
                tokens.pop(index) # 今の位置の数値トークンを削除
                tokens.pop(index-1) # 1つ前の'*'トークンを削除
                index -= 2 # 削除した分、見る位置を戻す

        index += 1 # 次の位置のトークンを見にいく
    return tokens
```

### evaluate関数（全体をまとめる）

- まず`evaluate_brackets`で括弧を処理する
- 残った式を`evaluate_plus_and_minus`で計算する

```python
# 全体の計算を行う関数
# 括弧を先に処理し、残った式の足し引き・掛け割りを計算する
# tokens: トークンのリスト
# answer: 式全体の計算結果
def evaluate(tokens):
    # まず括弧の内側と、それに付随する組み込み関数を計算する
    tokens = evaluate_brackets(tokens)
    # 括弧を処理した後に、残った式を計算する
    answer = evaluate_plus_and_minus(tokens)
    return answer
```

## テスト作成（考えたこと）

- まず`1+2`のような、基本的で小さいテストの作成
- 足し算・引き算：
  - `0+0``0-0`のゼロ同士の計算
  - `1-2`のように結果が負になるケース
  - `100-20-30-40`のような連続の計算
- 小数：
  - `0.001+0.01`のように桁が違うもの
- 極端な例：
  - `99999.999*9999…999`の大きな桁同士の乗算
- 優先順位の確認：
  - `1*2/3-4/5*6+5`のように四則が入り混じった式
- 括弧：
  - `100/(5*(1+1))`のように演算の中にカッコが入る形
  - `((1+2)*(3+(4-5)))`の深い入れ子になった形
- 関数
  - `abs(round(-2.5))`のような関数の入れ子
  - `abs((1+2)*(3-7))`のような関数と式が混ざったもの