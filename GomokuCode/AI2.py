import re
import time
from copy import deepcopy
    
class Node:

    def __init__(self, now_gmap, enemy_symbol, father_node, what_turn, need_value=False):
        
        """
        enemy_sybol 敌方的用子
        """
        init_alpha = -999999999999  # 用来初始化的alpha值
        init_beta  = 999999999999   # 用来初始化的beta值
        symbol1 = 1
        symbol2 = 2
        self.enemy_symbol = enemy_symbol
        if enemy_symbol == symbol2:
            self.own_symbol = symbol1
        else:
            self.own_symbol = symbol2
        self.beta = init_beta       # 初始的beta指定为无限大 
        self.alpha = init_alpha     # 初始的alpha指定为无限小，
        self.father = father_node   # 指定父节点
        self.childs = []            # 子节点，是一个列表，初始状态为空列表
        self.gmap = now_gmap
        self.pos = self.get_pos(father_node)
        self.what_turn = what_turn # 在什么层
        self.wall = 9              # 墙
        self.value = 0
        if need_value:
            self.value = self.cal_culate()
        # 地形得分
        
    def get_lines(self, x, y, sign_map):
        # 获取四个方向线段的数组
        
        v_line = []     # 竖直线
        l_line = []     # 水平线
        lu_rd  = []     # 左上到右下
        ld_ru  = []     # 左下到右上 
        # 横向  左到右
        for offset_x in range(9):
            pos_x = x - 4 + offset_x
            if pos_x < 0 or pos_x >= 15:
                l_line.append(self.wall)
            else:
                sign_map[pos_x][y] = 1      # 标记
                l_line.append(self.gmap[pos_x][y])
        
        # 纵向 上到下
        for offset_y in range(9):
            pos_y = y - 4 + offset_y
            if pos_y < 0 or pos_y >= 15:
                v_line.append(self.wall)
            else:
                sign_map[x][pos_y] = 1
                v_line.append(self.gmap[x][pos_y])
        
        # 左上到右下
        for offset_xy in range(9):
            pos_x = x - 4 + offset_xy
            pos_y = y - 4 + offset_xy
            if pos_y < 0 or pos_y >= 15 or pos_x < 0 or pos_x >= 15:
                lu_rd.append(self.wall)
            else:
                sign_map[pos_x][pos_y] = 1
                lu_rd.append(self.gmap[pos_x][pos_y])

        # 左下到右上
        for offset_xy in range(9):
            pos_x = x - 4 + offset_xy
            pos_y = y + 4 - offset_xy
            if pos_y < 0 or pos_y >= 15 or pos_x < 0 or pos_x >= 15:
                ld_ru.append(self.wall)
            else:
                sign_map[pos_x][pos_y] = 1
                ld_ru.append(self.gmap[pos_x][pos_y])        

        return l_line, v_line, lu_rd, ld_ru

    def lines_score(self, lines):
        # 根据传入的边线给出分数
        own_five        = re.compile(r'{}{{5}}'.format(self.own_symbol))      # 含有五个连一起的
        enemy_five      = re.compile(r'{}{{5}}'.format(self.enemy_symbol))    # 敌方五连
        own_live_four   = re.compile(r'0{}{{4}}0'.format(self.own_symbol))    # 友方活四
        enemy_live_four = re.compile(r'0{}{{4}}0'.format(self.enemy_symbol))  # 敌方活四
        # 冲四
        own_cr_four     = [
            re.compile(r'(?:{}|{}){}{{4}}0'.format(self.wall, self.enemy_symbol, self.own_symbol)),
            re.compile(r'0{}{{4}}(?:{}|{})'.format(self.own_symbol, self.enemy_symbol, self.wall)),
            re.compile(r'{}{{3}}0{}'.format(self.own_symbol, self.own_symbol)), 
            re.compile(r'{}0{}{{3}}'.format(self.own_symbol, self.own_symbol)),
            re.compile(r'{}{{2}}0{}{{2}}'.format(self.own_symbol, self.own_symbol)) 
        ]   # 友方
        enemy_cr_four   = [
            re.compile(r'(?:{}|{}){}{{4}}0'.format(self.wall, self.own_symbol, self.enemy_symbol)),
            re.compile(r'0{}{{4}}(?:{}|{})'.format(self.enemy_symbol, self.own_symbol, self.wall)),
            re.compile(r'{}{{3}}0{}'.format(self.enemy_symbol, self.enemy_symbol)), 
            re.compile(r'{}0{}{{3}}'.format(self.enemy_symbol, self.enemy_symbol)),
            re.compile(r'{}{{2}}0{}{{2}}'.format(self.enemy_symbol, self.enemy_symbol)),
        ]   # 敌方
        # 活三
        own_live_three   = [
            re.compile(r'00{}{{3}}0'.format(self.own_symbol)), 
            re.compile(r'0{}{{3}}00'.format(self.own_symbol)),
            re.compile(r'0{}{{2}}0{}0'.format(self.own_symbol, self.own_symbol))
        ]
        enemy_live_three = [
            re.compile(r'0{}{{3}}00'.format(self.enemy_symbol)),
            re.compile(r'00{}{{3}}0'.format(self.enemy_symbol)),
            re.compile(r'0{}{{2}}0{}0'.format(self.enemy_symbol, self.enemy_symbol))
        ]
        # 眠三
        own_cr_three   = [
            re.compile(r'(?:{}|{}){}{{3}}00'.format(self.wall, self.enemy_symbol, self.own_symbol)), 
            re.compile(r'00{}{{3}}(?:{}|{})'.format(self.own_symbol, self.enemy_symbol, self.wall)), 
            re.compile(r'{}{{2}}0{}'.format(self.own_symbol, self.own_symbol)), 
            re.compile(r'{}0{}{{2}}'.format(self.own_symbol, self.own_symbol)) 
        ]   # TODO: 这里对眠三的定义实际上并不准确，希望能通过良好的分值规划来规避吧

        enemy_cr_three = [
            re.compile(r'(?:{}|{}){}{{3}}00'.format(self.wall, self.own_symbol, self.enemy_symbol)), 
            re.compile(r'00{}{{3}}(?:{}|{})'.format(self.enemy_symbol, self.own_symbol, self.wall)),
            re.compile(r'{}{{2}}0{}'.format(self.enemy_symbol, self.enemy_symbol)), 
            re.compile(r'{}0{}{{2}}'.format(self.enemy_symbol, self.enemy_symbol)) 
        ]

        # 活二
        own_live_two  = re.compile(r'00{}{{2}}00'.format(self.own_symbol))
        enemy_live_two  = re.compile(r'00{}{{2}}00'.format(self.enemy_symbol))
        # 半活二
        own_halive_two = [
            re.compile(r'0{}{{2}}00'.format(self.own_symbol)),
            re.compile(r'00{}{{2}}0'.format(self.own_symbol))
        ]
        enemy_halive_two = [
            re.compile(r'0{}{{2}}00'.format(self.enemy_symbol)),
            re.compile(r'00{}{{2}}0'.format(self.enemy_symbol))
        ]
        # 半死不活二
        own_cr_two = [
            re.compile(r'(?:{}|{}){}{{2}}0'.format(self.wall, self.enemy_symbol, self.own_symbol)),
            re.compile(r'0{}{{2}}(?:{}|{})'.format(self.own_symbol, self.wall, self.enemy_symbol))
        ]
        enemy_cr_two = [
            re.compile(r'(?:{}|{}){}{{2}}0'.format(self.wall, self.own_symbol, self.enemy_symbol)),
            re.compile(r'0{}{{2}}(?:{}|{})'.format(self.enemy_symbol, self.wall, self.own_symbol))
        ]

        # 活1
        own_live_one   = re.compile(r'0{}0'.format(self.own_symbol))
        enemy_live_one = re.compile(r'0{}0'.format(self.enemy_symbol))
        # 死1
        own_cr_one   = re.compile(r'{}'.format(self.own_symbol))
        enemy_cr_one = re.compile(r'{}'.format(self.enemy_symbol))
        
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
        if self.what_turn == 1:
            # 极大层，后手
            own_prob = 1
            enemy_prob = 1.3
        else:
            # 极小层，先手
            own_prob = 1.3
            enemy_prob = 1
        own_score   = 0
        enemy_score = 0        
        for line in lines:
            str_line = ''.join([str(i) for i in line])  # 将列表转换成正则表达式可以处理的形式
            # 己方得分
            # 五
            re1 = own_five.findall(str_line)
            own_score += len(re1) * 1000001
            if len(re1) != 0:
                print('检测到友方五')
            # 活四
            re2 = own_live_four.findall(str_line)
            own_score += len(re2) * 50000
            if len(re2) != 0:
                print('检测到友方活四')
            # 冲四
            for compile_ in own_cr_four:
                re3 = compile_.findall(str_line)
                own_score += len(re3) * 26000
                if len(re3) != 0:
                    print('检测到友方冲四')
            # 活三
            for compile_ in own_live_three:
                re4 = compile_.findall(str_line)
                own_score += len(re4) * 13010
                if len(re4) != 0:
                    print('检测到友方活三')
            # 眠三
            for compile_ in own_cr_three:
                re5 = compile_.findall(str_line)
                own_score += len(re5) * 2600
                if len(re5) != 0:
                    print('检测到友方眠三')
            # 活二
            re6 = own_live_two.findall(str_line)
            own_score += len(re6) * 260
            if len(re6) != 0:
                print('检测到友方活二')
            # 半活二
            for compile_ in own_halive_two:
                re7 = compile_.findall(str_line)
                own_score += len(re7) * 50
                if len(re7) != 0:
                    print('检测到友方半活二')
            # 半死不活二
            for compile_ in own_cr_two:
                re8 = compile_.findall(str_line)
                own_score += len(re8) * 20
                if len(re8) != 0:
                    print('检测到友方半死不活二')
            # 一
            re9 = own_live_one.findall(str_line)
            own_score += len(re9) * 10
            if len(re9) != 0:
                print('检测到友方活一')
            re10 = own_cr_one.findall(str_line)
            own_score += len(re10) * 5
            if len(re10) != 0:
                print('检测到友方死一')
            # 敌方得分
            # 五
            re1 = enemy_five.findall(str_line)
            enemy_score += len(re1) * 1000001
            if len(re1) != 0:
                print('检测到敌方五')
            # 活四
            re2 = enemy_live_four.findall(str_line)
            enemy_score += len(re2) * 50000
            if len(re2) != 0:
                print('检测到敌方活四')
            # 冲四
            for compile_ in enemy_cr_four:
                re3 = compile_.findall(str_line)
                enemy_score += len(re3) * 26000
                if len(re3) != 0:
                    print('检测到敌方冲四')
            # 活三
            for compile_ in enemy_live_three:
                re4 = compile_.findall(str_line)
                enemy_score += len(re4) * 13010
                if len(re4) != 0:
                    print('检测到敌方活三')
            # 眠三
            for compile_ in enemy_cr_three:
                re5 = compile_.findall(str_line)
                enemy_score += len(re5) * 2600
                if len(re5) != 0:
                    print('检测到敌方眠三')
            # 活二
            re6 = enemy_live_two.findall(str_line)
            enemy_score += len(re6) * 260
            if len(re6) != 0:
                print('检测到敌方活二')
            # 半活二
            for compile_ in enemy_halive_two:
                re7 = compile_.findall(str_line)
                enemy_score += len(re7) * 50
                if len(re7) != 0:
                    print('检测到敌方半活二')
            # 半死不活二
            for compile_ in enemy_cr_two:
                re8 = compile_.findall(str_line)
                enemy_score += len(re8) * 20
                if len(re8) != 0:
                    print('检测到敌方半死不活二')
            re9 = enemy_live_one.findall(str_line)
            enemy_score += len(re9) * 10
            if len(re9) != 0:
                print('检测到敌方活一')
            re10 = enemy_cr_one.findall(str_line)
            enemy_score += len(re10) * 5
            if len(re10) != 0:
                print('检测到敌方死一')
        return own_score * own_prob - enemy_score * enemy_prob
                       

    def cal_culate(self):
        """计算这个节点的分数。对AI越有利则分数越高，反之分数越低"""
        # 地形分
        map_score = [[0 for y in range(15)] for x in range(15)]
        for y in range(15):
            for x in range(15):
                map_score[x][y] = - (0 - abs(14 - 2 * x) - abs(14 - 2 * y))

         
        sign_map = [[0 for y in range(15)] for x in range(15)]  # 标记数组，0为未标记，1为标记
        total_score = 0
        for y in range(15):
            for x in range(15):
                if sign_map[x][y] == 0:
                    # 未被访问
                    if self.gmap[x][y] == self.own_symbol or self.gmap[x][y] == self.enemy_symbol:
                        # 已经被落子，得出周围的曲线
                        lines = self.get_lines(x, y, sign_map)
                        total_score += self.lines_score(lines)
        total_score += map_score[self.pos[0]][self.pos[1]]

        return total_score

    def get_pos(self, input_node):
        # 通过前后地图的比较得出下的棋子的位置
        pos = (-1, -1)      # 是否为空棋盘，是的话会被置为(-1, -1)
        if input_node == None:  # 假如父节点是空，即AI下第一子
            for y in range(15):
                for x in range(15):
                    if self.gmap[x][y] != 0:
                        pos = (x, y)
                        break 
        else:
            # 否则 比对，得出
            for y in range(15):
                for x in range(15):
                    if input_node.gmap[x][y] != self.gmap[x][y]:
                        pos = (x, y)
                        break
        return pos

    def is_leaves(self):
        """判断是否是叶节点"""
        if len(self.childs) == 0:
            return True
        else:
            return False
    

"""
node 节点结构
"""

class GT_Tree:
    def __init__(self, init_gmap, enemy_symbol):
        """
        init_gmap: 传入树的地图
        
        """
        symbol1 = 1
        symbol2 = 2
        self.init_alpha = -999999999999  # 用来初始化的alpha值
        self.init_beta  = 999999999999   # 用来初始化的beta值
        self.choose_node = None
        self.enemy_symbol = enemy_symbol
        self.node_count = 0
        if enemy_symbol == symbol2:
            self.own_symbol = symbol1
        else:
            self.own_symbol = symbol2
        self.root = Node(deepcopy(init_gmap), enemy_symbol, None, 1)     # 首个节点没有父节点
        
                
                
        self.max_deepth = 2             # 最大搜索深度
        self.Tree_body = {0:[self.root], 1:[], 2:[], 3:[], 4:[]}    # 树体


    def search_best(self, input_map):
        # 寻找最佳落点
        start_time = 0
        if input_map == [[0 for y in range(15)] for x in range(15)]:
            # 首次开启ai而且是ai先手
            self.node_count = 1
            self.extend_node(self.root, 1, self.max_deepth, 1)   # 直接开始扩展，由于是第一层，即最大层, what_turn=1
        else:
            # 比对棋局
            exit_flag = False
            if self.choose_node != None:                # 假如上次落子不为空。换言之假如不是电脑第一次落子
                for factor in self.choose_node.childs:  # 从上次落子的子节点当中
                    if factor.gmap == input_map:        # 从下一项中找到对应的棋谱
                        self.root = factor              # 假如预测到了，将预测到的节点设为新的树节点
                        exit_flag = True    
                        break
            if not exit_flag:
                # 假如没有预测到，重新生成一颗博弈树
                self.node_count = 1
                self.root = Node(deepcopy(input_map), self.enemy_symbol, self.choose_node, 1)
                self.root.father = None # 将父节点置None防止无限递归    
                self.Tree_body = {0:[self.root]}
                self.extend_node(self.root, 1, self.max_deepth, 1) 
            else:
                # 假如预测到了，将预测到的节点作为新的树节点，从现有的树进行扩展
                self.root.facher = None         # 根节点的父节点置为空，避免无限递归
                # 处理树体
                self.node_count = 1
                """
                for key in self.Tree_body.keys():
                    if key >= 3:
                        self.Tree_body[key - 2] = self.Tree_body[key]       # 后赋值前面
                        self.node_count - len(self.Tree_body[key])
                        self.Tree_body[key] = []        # 置为空列表
                """
                self.Tree_body = {0:[self.root]}         # 置根节点
                self.extend_node(self.root, 1, self.max_deepth, 1)
            

        
        # 上面的过程将博弈树扩展完毕，下面选择最优节点
        if self.root.is_leaves():
            # 假如根节点经过扩展后不是叶节点
            self.Tree_body[1].sort(key=lambda x:x.alpha, reverse=True) # 由于是从极大层当中取点，所以要从大到小排
            self.choose_node = self.Tree_body[1][0]         # 最佳节点
            print('产生%d个节点，运行时间%f' % (self.node_count, time.time() - start_time))
            return self.choose_node.pos                # 返回落子的坐标
        else:
            print('产生%d个节点，运行时间%f' % (self.node_count, time.time() - start_time))
            return self.root.pos

    def caculate_alpha_beta(self, input_node, what_turn):
        """
        矫正博弈树上的alpha和beta值
        input_node   :传入节点
        what_turn  :什么层
        """
        father_node = input_node.father
        if father_node == None:     # 假如父节点为空则返回
            return

        if what_turn == 1:
            # 极大层，则上一层是极小层
            if input_node.is_leaves():
                # 假如是叶节点
                father_node.beta = input_node.value   
            else:
                # 不是叶节点, 则需要遍历父节点所有的子节点，选出其中alpha值最小的值
                min_num = father_node.childs[0].alpha
                for factor in father_node.childs:                                                
                    if factor.alpha < min_num:
                        min_num = factor.alpha
                father_node.beta = min_num
        if what_turn == 0:
            # 极小层，则上一层是极大层
           if input_node.is_leaves():
                # 假如是叶节点
                father_node.alpha = input_node.value   
           else:
                # 不是叶节点, 则需要遍历父节点所有的子节点，选出其中beta值最大的值
                max_num = father_node.childs[0].beta
                for factor in father_node.childs:                                                
                    if factor.beta > max_num:
                        max_num = factor.beta
                father_node.alpha = max_num 
        if what_turn == 0:
            new_turn = 1
        else:
            new_turn = 0
        # 递归
        self.caculate_alpha_beta(father_node, new_turn)

        

    def extend_node(self, input_node, deepth, max_deepth, what_turn):
        # 根据节点扩展博弈树，
        """
        input_node  输入的节点
        deepth:     当前的深度
        max_deepth: 最大扩展的深度
        what_turn   当前属哪次
        """
        overflow_flag = True    # 棋盘是否已经满了
        if what_turn == 1:
            # MAX层
            new_turn = 0
            now_symbol = self.own_symbol
        else:
            # Min层
            now_symbol = self.enemy_symbol
            new_turn = 1
        tmp_list = []       # 临时的排序列表
        if not input_node.is_leaves():
            # 假如不是叶节点，则传递扩展，只有叶节点才扩展
            self.node_count += len(input_node.childs)
            for child in input_node.childs:
                self.extend_node(child, deepth + 1, max_deepth, new_turn)                            
            return
        grand_parent = input_node.father       
        prue_flag = False   # 剪枝标记
        for y in range(15):
            for x in range(15):
                if input_node.gmap[x][y] == 0:
                    # 是一个空节点
                    # 将其加入这个节点的子节点当中
                    overflow_flag = False   # 因为可以落子所以棋盘还没满
                    new_map = deepcopy(input_node.gmap)
                    new_map[x][y] = now_symbol
                    if deepth == max_deepth:
                        new_node = Node(new_map, self.enemy_symbol, input_node, what_turn, True)   # 最后一层需要计算棋盘的价值
                        tmp_list.append(new_node)
                        self.node_count += 1
                        # alpha_beta剪枝，在最后一层发生
                        if grand_parent != None:    # 爷爷节点不为空
                            if what_turn == 1:
                                # 极大层
                                if grand_parent.alpha > new_node.value:
                                    # 爷爷节点的alpha值大于new_node的值 发生剪枝
                                    input_node.beta = new_node.value    # 父节点的beta值即等于新值
                                    prue_flag = True    # 发生了剪枝
                                    break
                            else:
                                # 极小层
                                if grand_parent.beta < new_node.value:
                                    input_node.alpha = new_node.value
                                    prue_flag = True
                                    break
                    else:
                        # 不是最后一层，不需要计算价值
                        self.node_count += 1
                        new_node = Node(new_map, self.enemy_symbol, input_node, what_turn)
                        tmp_list.append(new_node)

        if overflow_flag:
            # 当棋盘已经满的时候
            return 2 # 指令码2，棋盘已满

        
        self.Tree_body[deepth] = tmp_list       # 将节点加入树体当中便于访问


        if not prue_flag and deepth == max_deepth:
            # 假如没有发生剪枝，且已经扩展到了最大深度，则回算树的alpha_beta值
            tmp_list.sort(key=lambda x:x.value, reverse = (what_turn != 0)) # 加入what_turn != 0 则代表要逆序即MAX层
            self.caculate_alpha_beta(tmp_list[-1], what_turn)

        if deepth < max_deepth: 
            # 假如未到达最大深度       
            for factor in tmp_list:
                #  对于依然存在的节点进行继续的扩展
                result = self.extend_node(factor, deepth + 1, max_deepth, new_turn)
                # result 存储扩展的结果
                if result == 2:     # 即下一层棋盘已满
                    # 直接在这层做完所有的处理
                    for factor in tmp_list:
                        factor.value = factor.cal_culate()  # 计算价值
                    tmp_list.sort(key=lambda x:x.value, reverse = (what_turn != 0))
                    self.caculate_alpha_beta(tmp_list[-1], what_turn)   # 回算alpha_beta值
                    break # 中断循环   
        else:
            return 1    # 指令码1，已扩展到最大深度


        # 将所有的点都以加入完毕
        


        