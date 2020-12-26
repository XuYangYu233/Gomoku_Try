# 用Python制作的五子棋程序（人机对抗）

origin: git@github.com: HaloOrangeWang/PythonGomoku.git

## 接口说明

要使用不同的AI进行控制，只需修改game.py中的ai_play_1step_py_python函数

其中几个重要的属性：

* self.g_map: 二维列表，大小为15*15，表示棋盘，其中没有棋子的位置为0，有玩家棋子的位置为1，有电脑位置的棋子为2

* self.cur_step: int类型，表示从棋局开始到现在的总共走的步数，也就是场上的总棋子数

* self.max_search_steps: int类型，表示最大搜索深度

* self.player_first: bool类型，玩家是否先手，需要注意的是原AI在玩家后手的情况下运行起来似乎有些问题
