import random
import copy
import re


class Yichuan:
    def __init__(self, init_map, color):
        self.map = init_map
        self.init_group = 200
        self.max_group = 1000
        self.chorme_len = 12
        self.generations = 50
        self.sel_fixer = 0.3
        self.prab_cro = 0.7
        self.prab_mut = 0.3
        self.mul_fixer = 0.1
        self.max_son = 2
        self.fit_reduction = 0.90
        self.aval_distance = 2
        self.max_value = 0
        for i in range(self.chorme_len):
            self.max_value += 100 * self.fit_reduction ** i
        self.wall = 9
        self.color = color

    def find_available_points(self, map_copy):
        available_point = []
        for i in range(15):
            for j in range(15):
                if map_copy[i][j] != 0:
                    continue
                min_i = (i - self.aval_distance) if i - self.aval_distance >= 0 else 0
                min_j = (j - self.aval_distance) if j - self.aval_distance >= 0 else 0
                max_i = (i + self.aval_distance) if i + self.aval_distance <= 14 else 14
                max_j = (j + self.aval_distance) if j + self.aval_distance <= 14 else 14
                count = 0
                for x in range(min_i, max_i + 1):
                    for y in range(min_j, max_j + 1):
                        count += map_copy[x][y] != 0
                if count == 0:
                    continue
                available_point.append((i, j))

        return available_point

    def random_point(self, available_point):
        return random.choice(available_point)

    def gene_encode(self):
        pop = []
        for i in range(self.init_group):
            chorme = []
            map_copy = copy.deepcopy(self.map)
            for j in range(self.chorme_len):
                available_points = self.find_available_points(map_copy)
                temp = self.random_point(available_points)
                chorme.append(temp)
                if self.color == 2:
                    map_copy[temp[0]][temp[1]] = 2 - j % 2
                else:
                    map_copy[temp[0]][temp[1]] = 1 + j % 2
            pop.append(chorme)
            for x in chorme:
                if chorme.count(x) > 1:
                    raise ValueError("overlap in gene_encode")

        return pop

    def cal_fit(self, chorme):
        count = 0
        map_copy = copy.deepcopy(self.map)
        flag_win = False
        winner = 0
        duizhao = 0
        for i in chorme:
            duizhao += 100 * self.fit_reduction ** chorme.index(i)
            if flag_win:
                count += (1 - winner) * 100 * self.fit_reduction ** chorme.index(i)
            else:
                color = (2 - chorme.index(i) % 2) if self.color == 2 else (1 + chorme.index(i) % 2)
                tmp_val = self.point_value(i, map_copy, color)
                map_copy[i[0]][i[1]] = color
                count += tmp_val * self.fit_reduction ** chorme.index(i)
                if tmp_val == 100:
                    flag_win = True
                    winner = chorme.index(i) % 2
            if count > duizhao:
                raise ValueError("illegal count")

        return count

    def selection(self, pop, fits):  # 仿轮盘赌
        new_pop = copy.deepcopy(pop)
        new_fits = copy.deepcopy(fits)
        for i in range(len(fits)):
            prab_a = fits[i] / self.max_value
            prab_a **= self.sel_fixer
            if random.random() > prab_a:
                new_fits.remove(fits[i])
                new_pop.remove(pop[i])

        return new_pop, new_fits

    def selection2(self, pop, fits):  # 随机竞争选择
        new_pop1 = copy.deepcopy(pop)
        new_fits1 = copy.deepcopy(fits)
        new_pop2 = []
        new_fits2 = []
        new_pop3 = []
        new_fits3 = []

        while len(new_pop1) > len(new_pop2):
            ran_chorme = random.choice(new_pop1)
            new_fits2.append(new_fits1.pop(new_pop1.index(ran_chorme)))
            new_pop2.append(new_pop1.pop(new_pop1.index(ran_chorme)))

        if len(new_pop2) > len(new_pop1):
            new_pop2.pop(new_fits2.index(min(new_fits2)))
            new_fits2.remove(min(new_fits2))

        for i in range(len(new_pop1)):
            if new_fits1[i] > new_fits2[i]:
                new_fits3.append(new_fits1[i])
                new_pop3.append(new_pop1[i])
            else:
                new_fits3.append(new_fits2[i])
                new_pop3.append(new_pop2[i])

        return new_pop3, new_fits3

    def crossover(self, pop):
        for i in range(len(pop)):
            if random.random() < self.prab_cro:
                overlap = False
                while True:
                    chrome_a = random.choice(pop[:i] + pop[i + 1:])
                    chrome_b = pop[i]
                    stand_b, stand_a = copy.deepcopy(chrome_a), copy.deepcopy(chrome_b)

                    same = [x for x in chrome_a if x in chrome_b]
                    fixed_points = []
                    for x in range(min(random.randint(1, 4), len(same))):
                        fixed_points.append(random.choice(same))
                    fixed_points = list(set(fixed_points))
                    for x in fixed_points:
                        stand_b.remove(x)
                        stand_a.remove(x)
                    fixed_points.sort(key=lambda x: chrome_a.index(x))
                    for x in fixed_points:
                        stand_a.insert(chrome_a.index(x), x)
                    fixed_points.sort(key=lambda x: chrome_b.index(x))
                    for x in fixed_points:
                        stand_b.insert(chrome_b.index(x), x)

                    for x in stand_a:
                        if stand_a.count(x) > 1:
                            overlap = True
                    for x in stand_b:
                        if stand_b.count(x) > 1:
                            overlap = True
                    if not overlap:
                        chrome_a, chrome_b = copy.deepcopy(stand_a), copy.deepcopy(
                            stand_b
                        )
                        break
                    else:
                        print("detecting overlap! retrying")

    def mutation(self, pop):
        for i in range(len(pop)):
            if random.random() < self.prab_mut:
                chrome_a = pop[i]
                position_a, position_b = 0, 0
                while position_a == position_b:
                    position_a = random.randint(0, self.chorme_len - 1)
                    position_b = random.randint(0, self.chorme_len - 1)
                chrome_a[position_a], chrome_a[position_b] = (
                    chrome_a[position_b],
                    chrome_a[position_a],
                )

    def multiply(self, pop, fits):
        new_pop = copy.deepcopy(pop)
        new_fits = copy.deepcopy(fits)
        new_fits, new_pop = (list(t) for t in zip(*sorted(zip(new_fits, new_pop))))
        new_fits.reverse()
        new_pop.reverse()
        for i in range(len(fits)):
            prab_a = fits[i] / self.max_value
            prab_a **= self.mul_fixer
            if random.random() <= prab_a:
                sons = random.randint(1, self.max_son)
                for j in range(sons):
                    new_pop.append(pop[i])
                    if len(new_pop) >= self.max_group:
                        return new_pop

        return new_pop

    def play(self):
        print("\nStarting Yichuan algorithm")
        pop = self.gene_encode()
        print("gene_encode finished")
        best_chorme, best_val = (0, 0), 0
        for i in range(self.generations):
            fits = []
            for j in range(len(pop)):
                fits.append(self.cal_fit(pop[j]))
            if max(fits) > best_val:
                best_val = max(fits)
                best_chorme = pop[fits.index(max(fits))]

            pop, fits = self.selection2(pop, fits)
            pop.append(best_chorme)
            fits.append(best_val)  # 保留最佳选择
            self.crossover(pop)
            self.mutation(pop)
            pop = self.multiply(pop, fits)
            if i % 10 == 9:
                print(
                    "第{}代: 最佳点位({}, {}), 权值:{}".format(
                        i + 1,
                        best_chorme[0][0],
                        best_chorme[0][1],
                        best_val / self.max_value,
                    )
                )
                print("预测走向:", end=" ")
                for i in best_chorme:
                    print(i, end=", ")
                print("\n种群规模为{}".format(len(pop)))

        return best_chorme[0]

    def cal_line(self, lines, color):
        if lines[0][4] != 0 or lines[1][4] != 0 or lines[2][4] != 0 or lines[3][4] != 0:
            raise ValueError("lines collected error")
        # 根据传入的边线给出分数
        self.own_symbol = color
        self.enemy_symbol = 3 - color
        own_five = re.compile(r"{}{{5}}".format(self.own_symbol))  # 含有五个连一起的
        enemy_five = re.compile(r"{}{{5}}".format(self.enemy_symbol))  # 敌方五连
        own_live_four = re.compile(r"0{}{{4}}0".format(self.own_symbol))  # 友方活四
        enemy_live_four = re.compile(r"0{}{{4}}0".format(self.enemy_symbol))  # 敌方活四
        # 冲四
        own_cr_four = [
            re.compile(r"(?:{}|{}){}{{4}}0".format(self.wall, self.enemy_symbol, self.own_symbol)),
            re.compile(r"0{}{{4}}(?:{}|{})".format(self.own_symbol, self.enemy_symbol, self.wall)),
            re.compile(r"{}{{3}}0{}".format(self.own_symbol, self.own_symbol)),
            re.compile(r"{}0{}{{3}}".format(self.own_symbol, self.own_symbol)),
            re.compile(r"{}{{2}}0{}{{2}}".format(self.own_symbol, self.own_symbol)),
        ]  # 友方
        enemy_cr_four = [
            re.compile(r"(?:{}|{}){}{{4}}0".format(self.wall, self.own_symbol, self.enemy_symbol)),
            re.compile(r"0{}{{4}}(?:{}|{})".format(self.enemy_symbol, self.own_symbol, self.wall)),
            re.compile(r"{}{{3}}0{}".format(self.enemy_symbol, self.enemy_symbol)),
            re.compile(r"{}0{}{{3}}".format(self.enemy_symbol, self.enemy_symbol)),
            re.compile(r"{}{{2}}0{}{{2}}".format(self.enemy_symbol, self.enemy_symbol)),
        ]  # 敌方
        # 活三
        own_live_three = [
            re.compile(r"00{}{{3}}0".format(self.own_symbol)),
            re.compile(r"0{}{{3}}00".format(self.own_symbol)),
            re.compile(r"0{}{{2}}0{}0".format(self.own_symbol, self.own_symbol)),
        ]
        enemy_live_three = [
            re.compile(r"0{}{{3}}00".format(self.enemy_symbol)),
            re.compile(r"00{}{{3}}0".format(self.enemy_symbol)),
            re.compile(r"0{}{{2}}0{}0".format(self.enemy_symbol, self.enemy_symbol)),
        ]
        # 眠三
        own_cr_three = [
            re.compile(r"(?:{}|{}){}{{3}}00".format(self.wall, self.enemy_symbol, self.own_symbol)),
            re.compile(r"00{}{{3}}(?:{}|{})".format(self.own_symbol, self.enemy_symbol, self.wall)),
            re.compile(r"{}{{2}}0{}".format(self.own_symbol, self.own_symbol)),
            re.compile(r"{}0{}{{2}}".format(self.own_symbol, self.own_symbol)),
        ]   
        enemy_cr_three = [
            re.compile(r"(?:{}|{}){}{{3}}00".format(self.wall, self.own_symbol, self.enemy_symbol)),
            re.compile(r"00{}{{3}}(?:{}|{})".format(self.enemy_symbol, self.own_symbol, self.wall)),
            re.compile(r"{}{{2}}0{}".format(self.enemy_symbol, self.enemy_symbol)),
            re.compile(r"{}0{}{{2}}".format(self.enemy_symbol, self.enemy_symbol)),
        ]

        # 活二
        own_live_two = re.compile(r"00{}{{2}}00".format(self.own_symbol))
        enemy_live_two = re.compile(r"00{}{{2}}00".format(self.enemy_symbol))
        # 半活二
        own_halive_two = [
            re.compile(r"0{}{{2}}00".format(self.own_symbol)),
            re.compile(r"00{}{{2}}0".format(self.own_symbol)),
        ]
        enemy_halive_two = [
            re.compile(r"0{}{{2}}00".format(self.enemy_symbol)),
            re.compile(r"00{}{{2}}0".format(self.enemy_symbol)),
        ]
        # 半死不活二
        own_cr_two = [
            re.compile(r"(?:{}|{}){}{{2}}0".format(self.wall, self.enemy_symbol, self.own_symbol)),
            re.compile(r"0{}{{2}}(?:{}|{})".format(self.own_symbol, self.wall, self.enemy_symbol)),
        ]
        enemy_cr_two = [
            re.compile(r"(?:{}|{}){}{{2}}0".format(self.wall, self.own_symbol, self.enemy_symbol)),
            re.compile(r"0{}{{2}}(?:{}|{})".format(self.enemy_symbol, self.wall, self.own_symbol)),
        ]

        # 活1
        own_live_one = re.compile(r"0{}0".format(self.own_symbol))
        enemy_live_one = re.compile(r"0{}0".format(self.enemy_symbol))
        # 死1
        own_cr_one = re.compile(r"{}".format(self.own_symbol))
        enemy_cr_one = re.compile(r"{}".format(self.enemy_symbol))

        """
        计分规划
        半死2 : 20
        半活2 : 50
        活二  : 260
        眠三  : 2600
        活三  : 13010
        冲四  : 26000
        活四  : 50000
        五    : 1000001

        """
        own_prob = 1
        enemy_prob = 1
        own_score = 0
        enemy_score = 0

        wu = 100
        huosi = 100
        chongsi = 100
        huosan = 49
        miansan = 33
        huoer = 20
        banhuoer = 15
        bansibuhuoer = 13
        yi = 5
        ling = 1

        for line in lines:
            str_line = "".join([str(i) for i in line])  # 将列表转换成正则表达式可以处理的形式
            # 己方得分
            # 五
            re1 = own_five.findall(str_line) != []
            own_score += re1 * wu
            # 活四
            re2 = own_live_four.findall(str_line) != []
            own_score += re2 * huosi
            # 冲四
            for compile_ in own_cr_four:
                re3 = compile_.findall(str_line) != []
                own_score += re3 * chongsi
            # 活三
            for compile_ in own_live_three:
                re4 = compile_.findall(str_line) != []
                own_score += re4 * huosan
            # 眠三
            for compile_ in own_cr_three:
                re5 = compile_.findall(str_line) != []
                own_score += re5 * miansan
            # 活二
            re6 = own_live_two.findall(str_line) != []
            own_score += re6 * huoer
            # 半活二
            for compile_ in own_halive_two:
                re7 = compile_.findall(str_line) != []
                own_score += re7 * banhuoer
            # 半死不活二
            for compile_ in own_cr_two:
                re8 = compile_.findall(str_line) != []
                own_score += re8 * bansibuhuoer
            # 一
            re9 = own_live_one.findall(str_line) != []
            own_score += re9 * yi
            re10 = own_cr_one.findall(str_line) != []
            own_score += re10 * ling
            # 敌方得分
            # 五
            re1 = enemy_five.findall(str_line) != []
            enemy_score += re1 * wu
            # 活四
            re2 = enemy_live_four.findall(str_line) != []
            enemy_score += re2 * huosi
            # 冲四
            for compile_ in enemy_cr_four:
                re3 = compile_.findall(str_line) != []
                enemy_score += re3 * chongsi
            # 活三
            for compile_ in enemy_live_three:
                re4 = compile_.findall(str_line) != []
                enemy_score += re4 * huosan
            # 眠三
            for compile_ in enemy_cr_three:
                re5 = compile_.findall(str_line) != []
                enemy_score += re5 * miansan
            # 活二
            re6 = enemy_live_two.findall(str_line) != []
            enemy_score += re6 * huoer
            # 半活二
            for compile_ in enemy_halive_two:
                re7 = compile_.findall(str_line) != []
                enemy_score += re7 * banhuoer
            # 半死不活二
            for compile_ in enemy_cr_two:
                re8 = compile_.findall(str_line) != []
                enemy_score += re8 * bansibuhuoer
            re9 = enemy_live_one.findall(str_line) != []
            enemy_score += re9 * yi
            re10 = enemy_cr_one.findall(str_line) != []
            enemy_score += re10 * ling
        return own_score * own_prob + enemy_score * enemy_prob

    def point_value(self, point, map_copy, color):
        x = point[0]
        y = point[1]
        values = 0

        # 横向
        line = [[] for i in range(4)]
        for i in range(x - 4, x + 5):
            if i < 0 or i > 14:
                line[0].append(self.wall)
            else:
                line[0].append(map_copy[i][y])

        # 纵向
        for i in range(y - 4, y + 5):
            if i < 0 or i > 14:
                line[1].append(self.wall)
            else:
                line[1].append(map_copy[x][i])

        # x=-y向
        for i in range(-4, 5):
            if x + i < 0 or x + i > 14 or y + i < 0 or y + i > 14:
                line[2].append(self.wall)
            else:
                line[2].append(map_copy[x + i][y + i])

        # x=y向
        for i in range(-4, 5):
            if x - i < 0 or x - i > 14 or y + i < 0 or y + i > 14:
                line[3].append(self.wall)
            else:
                line[3].append(map_copy[x - i][y + i])

        values = self.cal_line(line, color)
        if values > 100:
            values = 100
        return values


if __name__ == "__main__":
    print("testing module")
    map = [[0 for y in range(15)] for x in range(15)]
    map[7][7] = 1
    a = Yichuan(map)
    x, y = a.play()
    print("x: {}, y: {}".format(x, y))
