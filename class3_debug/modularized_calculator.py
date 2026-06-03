#! /usr/bin/python3

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

# 文字列を分割し、トークンのリストに変換する関数
# line: 入力された数式の文字全体
# 戻り値: 作成したトークンの文字列全体分のリスト
def tokenize(line):
    tokens = [] # 読み取ったトークンを順番に貯めるリスト
    index = 0 # 文字列のどこを読んでいるかを示す位置

    # 文字列を最後まで一つずつ見ていき、
    # 文字の種類に応じて呼び出す関数を切り替えてトークン作成
    while index < len(line):
        if line[index].isdigit(): # '0'〜'9' なら数値
            (token, index) = read_number(line, index)
        elif line[index] == '+': # '+' なら加算
            (token, index) = read_plus(line, index)
        elif line[index] == '-': # '-' なら減算
            (token, index) = read_minus(line, index)
        elif line[index] == '*': # '*' なら乗算
            (token, index) = read_times(line, index)
        elif line[index] == '/': # '/' なら除算
            (token, index) = read_divide(line, index)
        elif line[index] == '(': # '('なら左括弧
            (token, index) = read_left_brackets(line, index)
        elif line[index] == ')': # ')'なら右括弧
            (token, index) = read_right_brackets(line, index)
        # "abs"という3文字が並んでいたらabs関数
        elif index < len(line)-3 and line[index] == 'a' and line[index+1] == 'b' and line[index+2] == 's':
            (token, index) = read_abs(line, index)
        # "int"という3文字が並んでいたらint関数
        elif index < len(line)-3 and line[index] == 'i' and line[index+1] == 'n' and line[index+2] == 't':
            (token, index) = read_int(line, index)
        # "round"という3文字が並んでいたらround関数
        elif index < len(line)-5 and line[index] == 'r' and line[index+1] == 'o' and line[index+2] == 'u' and line[index+3] == 'n' and line[index+4] == 'd':
            (token, index) = read_round(line, index)
        # それ以外は未対応の文字なのでエラー終了
        else:
            print('Invalid character found: ' + line[index])
            exit(1)
        # 読み取ったトークンをリストに追加
        tokens.append(token)
    return tokens

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

# 足し算・引き算を計算する関数
# tokens: トークンの文字列全部のリスト
# 戻り値: 計算結果
def evaluate_plus_and_minus(tokens):
    # まず掛け算・割り算を先にしておく（足し引きだけのリストになる）
    tokens = evaluate_times_and_divide(tokens)

    answer = 0 # 計算結果を入れる変数
    tokens.insert(0, {'type': 'PLUS'}) # Insert a dummy '+' token
    index = 1 # ダミーの次から見ていく
    while index < len(tokens):
        # 数値トークンを見つけたら
        if tokens[index]['type'] == 'NUMBER':
            # 一つ前が'+'なら足す
            if tokens[index - 1]['type'] == 'PLUS':
                answer += tokens[index]['number']
            # 一つ前が'-'なら引く
            elif tokens[index - 1]['type'] == 'MINUS':
                answer -= tokens[index]['number']
            # 数値の前が演算子でない場合は文法エラー
            else:
                print('Invalid syntax')
                exit(1)
        index += 1

    return answer

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

def test(line):
    tokens = tokenize(line)
    actual_answer = evaluate(tokens)
    expected_answer = eval(line)
    if abs(actual_answer - expected_answer) < 1e-8:
        print("PASS! (%s = %f)" % (line, expected_answer))
    else:
        print("FAIL! (%s should be %f but was %f)" % (line, expected_answer, actual_answer))


# Add more tests to this function :)
def run_test():
    print("==== Test started! ====")
    test("1+2")
    test("1+2+3+4")
    test("0+0")
    test("0+5")
    test("0.001+0.01")
    test("4.5392+2.285+6.193+2+2.681")
    test("18358198358+139875439+217843958347818+193840820138+34718749")
    test("1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1")
    test("2.2+1.5+3.6+11+3.5151+33+7.326+33+11+1.462+44+62+16.263+4+3.5")
    test("2-1")
    test("1-2")
    test("1-3.6")
    test("2.5-3.6")
    test("100-20-30-40")
    test("0-0")
    test("0-2")
    test("0-5.6")
    test("1.0+2.1-3")
    test("5-55+290-390")
    test("3.5-6.6+9.1-100+3.55")
    test("1*2")
    test("0*0")
    test("1.2*0")
    test("0*0*0*0*0")
    test("15.352*3.2351*3.523*64.4592")
    test("1+2*3*4")
    test("99999.999*99999999999999999999.999999999999999999")
    test("3.2*4.3-42.3*1.2+11.32*3.2*35.1")
    test("1/2")
    test("0/1593.2")
    test("391.84/3.1593")
    test("1.329/4.19/39.1/2.3")
    test("20.35*15.3/8.189/2.153")
    test("1*2/3-4/5*6+5")
    test("30.10+103.1*0.3185/39.1-3.35+159.4/19+3.5190*23.983")
    test("(1+2)*3")
    test("(1+2)/(3-4)")
    test("((1+2)*3)")
    test("((1+2)*3)+1")
    test("(1+2)*(3+4)")
    test("100/(5*(1+1))")
    test("((1))")
    test("((1+2)*(3+4))")
    test("((1+2)*(3+(4-5)))")
    test("(1.5+2.5)*(3.5-1.5)")
    test("0.5*(2+4)/(3-1)")
    test("abs(1.5-4.5)")
    test("abs(1-2)+abs(3-7)")
    test("abs(-3)")
    test("int(10/3)")
    test("int(2.9+1.5)")
    test("int(7/2)*2")
    test("round(3.14159)")
    test("round(2.5)+round(3.5)")
    test("abs(round(-2.5))")
    test("int(round(7.8))")
    test("abs(int(round(1.55)+abs(int(2.3+4))))")
    test("int(10/3)+round(7/2)+abs(2-9)")
    test("abs((1+2)*(3-7))")
    test("2*abs(3-8)+int(9.9)")
    test("abs(int(round(1.55)+abs(int(2.3+4))))")
    print("==== Test finished! ====\n")

run_test()

while True:
    print('> ', end="")
    line = input()
    tokens = tokenize(line)
    answer = evaluate(tokens)
    print("answer = %f\n" % answer)