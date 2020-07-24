import matplotlib.pyplot as plt


class Node(object):
    def __init__(self, x, left=None, right=None, parent=None, color=False):
        """

        :param color: True for red, False for black
        """
        self.label = x
        self.left = left
        self.right = right
        self.parent = parent
        self.color = color

    def __color_flip(self):
        if self.parent:
            self.color = True
        self.left.color = False
        self.right.color = False

    def __rotate_left(self):
        right = self.right
        self.right = right.left
        if self.right:
            self.right.parent = self
        right.left = self
        right.color = self.color
        right.parent = self.parent
        if self.parent:
            if self.__is_left():
                right.parent.left = right
            else:
                right.parent.right = right
        self.parent = right
        self.color = True

    def __rotate_right(self):
        left = self.left
        self.left = left.right
        if self.left:
            self.left.parent = self
        left.right = self
        left.color = self.color
        left.parent = self.parent
        if self.parent:
            if self.__is_left():
                left.parent.left = left
            else:
                left.parent.right = left
        self.parent = left
        self.color = True

    def __is_leaf(self):
        return not self.left and not self.right

    def __swap(self, node):
        if self.parent:
            if self.__is_left():
                self.parent.left = node
            else:
                self.parent.right = node
        if node.parent:
            if node.parent.left == node:
                node.parent.left = self
            else:
                node.parent.right = self
        node.parent, self.parent = self.parent, node.parent
        node.color, self.color = self.color, node.color
        node.left, self.left = self.left, node.left
        if node.left:
            node.left.parent = node
        if self.left:
            self.left.parent = self
        node.right, self.right = self.right, node.right
        if node.right:
            node.right.parent = node
        if self.right:
            self.right.parent = self

    def __is_left(self):
        if self.parent:
            return self.parent.left == self
        else:
            return False

    def __is_right(self):
        if self.parent:
            return self.parent.right == self
        else:
            return False

    def __graft(self, target_node, direction):
        if not target_node:
            self.parent.parent = self
            self.parent = None
            return
        if direction:
            target_node.left = self
        else:
            target_node.right = self
        self.parent = target_node

    def __steal_from_parent(self):
        # 父节点是3-节点且相邻兄弟节点为2-节点
        if self.__is_left() and self.parent.color:
            # 删除左侧的节点
            self.parent = self.parent
            self.parent.right.__graft(self.parent.parent, True)
            if self.left and not self.right:
                # 从__merge运行到这里
                self.parent.right.left.__graft(self.parent, False)
                self.parent.__graft(self.parent.parent.left, True)
                self.parent.left.left.__graft(self.parent, True)
                self.parent.color = True
                return True
            self.parent.right = None
            self.parent.__graft(self.parent.parent.left, True)
            self.parent.left = None
            return True
        elif self.__is_right() and self.parent.color:
            # 删除中间节点
            self.parent.left.color = True
            self.parent.color = False
            if self.left and not self.right:
                self.left.__graft(self.parent, False)
                return True
            self.parent.right = None
            return True
        elif self.__is_right() and self.parent.left.color:
            self.parent.left.__graft(self.parent.parent, self.parent.__is_left())
            self.parent.left.color = False
            if self.left and not self.right:
                # 从__merge运行到这里
                self.parent.left.right.__graft(self.parent, True)
                self.parent.left.color = True
                self.parent.__graft(self.parent.parent, False)
                self.parent.right.left.__graft(self.parent, False)
                return True
            self.parent.__graft(self.parent.left.right, True)
            self.parent.left, self.parent.right = None, None
            self.parent.color = True
            self.parent.__swap(self.parent.parent)
            return True
        return False

    def __steal_from_siblings(self):
        def switch_to_siblings(node: Node, direction):
            node.__swap(node.parent) if direction != 'mr' else node.__swap(node.parent.parent)
            if direction == 'lm' or direction == 'mr':
                node.__swap(node.right.left)
                node.__swap(node.parent)
            elif direction == 'ml':
                node.__swap(node.left)
            elif direction == 'rm':
                node.__swap(node.left.right)
            if node.right:
                # 若存在右子节点，说明是从__swim_up运行到这里
                if node.__is_right():
                    switch_node = node.left.left
                    node.left.__swap(node.parent)
                    node.__swap(node.left)
                    node.right.__graft(node.parent, True)
                    return switch_node, direction
                else:
                    switch_node = node.right
                    node.left.__graft(node.parent, True)
                    node.left.color = False
                    return switch_node, direction
            else:
                node.left.__graft(node.parent, node.__is_left())
                node.left.color = False
            return True

        # 当父节点为2-节点时或父节点为3-节点但不涉及到右侧节点时
        if self.__is_left() and self.parent.right.left and self.parent.right.left.color:
            # 删除左节点且右(中间)节点为3-节点
            return switch_to_siblings(self, 'lm')
        elif self.__is_right() and self.parent.left.left and self.parent.left.left.color:
            # 删除右(中间)节点且左节点为3-节点
            return switch_to_siblings(self, 'ml')
        # 当父节点为3-节点且涉及到右侧节点时
        elif self.__is_right() and self.parent.left.color and self.parent.left.right.left \
                and self.parent.left.right.left.color:
            # 当删除右侧节点，且中间节点为3-节点时
            return switch_to_siblings(self, 'rm')
        elif self.__is_right() and self.parent.color and self.parent.parent.right.left \
                and self.parent.parent.right.left.color:
            # 当删除中间节点，且右节点为3-节点时：
            return switch_to_siblings(self, 'mr')
        return False

    def __swim_up(self):
        def merge_children(node: Node):
            if not node.left and not node.right:
                # 底层合并
                node.right.__graft(node.left, True)
                node.left.left.color = True
                node.right = None
                node.left.__swap(node.left.left)
                return
            else:
                if node.left.left and not node.left.right:
                    # 从左节点上游合并
                    node.right.left.__graft(node.left, False)
                elif node.right.left and not node.right.right:
                    # 从右节点上游合并
                    node.right.left.__graft(node.right, False)
                node.left.__graft(node.right, True)
                node.left.color = True
                node.right.__graft(node, True)
                node.right = None
                return

        self.__swap(self.parent)
        merge_children(self)
        temp = self.left
        if info := self.__steal_from_siblings():
            switch_node, direction = info[0], info[1]
            if direction == 'ml' or direction == 'rm':
                temp.parent.left.__graft(temp.parent, False)
                switch_node.__graft(temp.parent, True)
            else:
                switch_node.__graft(temp.parent, False)
            return True
        elif self.__steal_from_parent():
            return True
        else:
            if not self.parent:
                self.left.__graft(self.parent, False)
                return True
            self.__swim_up()
            return True

    def add(self, x):
        def fix(node):
            if node.color and node.left and node.left.color:
                node.parent.__rotate_right()
                node.__color_flip()
            elif node.left and node.left.color and node.right and node.right.color:
                node.__color_flip()
            elif ((node.left and node.left.color is False) or not node.left) and node.right and node.right.color:
                node.__rotate_left()
                node = node.parent
                if node.color:
                    node.parent.__rotate_right()
                    node.__color_flip()
            else:
                return
            if node.parent:
                node = node.parent
            fix(node)

        if self.__is_leaf():
            if self.color:
                if x == self.label or x == self.parent.label:
                    return False
                if x < self.label:
                    self.left = Node(x, parent=self, color=True)
                elif self.label < x < self.parent.label:
                    self.right = Node(x, parent=self, color=True)
                elif x > self.parent.label:
                    self.parent.right = Node(x, parent=self, color=True)
                fix(self)
            else:
                if x == self.label:
                    return False
                elif x < self.label:
                    self.left = Node(x, parent=self, color=True)
                elif x > self.label:
                    self.right = Node(x, parent=self, color=True)
                    self.__rotate_left()
        else:
            if x == self.label:
                return False
            elif x < self.label:
                if self.left is None:
                    self.left = Node(x, parent=self, color=True)
                    fix(self)
                else:
                    return self.left.add(x)
            elif x > self.label:
                if self.right is None:
                    self.right = Node(x, parent=self, color=True)
                    fix(self)
                else:
                    return self.right.add(x)

    def search(self, x):
        if x == self.label:
            return self
        elif x > self.label:
            if self.right is None:
                return False
            return self.right.search(x)
        elif x < self.label:
            if self.left is None:
                return False
            return self.left.search(x)

    def delete(self, x):
        if (root := self.search(x)) is False:
            return False
        if not root.__is_leaf() and not (root.left and root.left.__is_leaf() and root.left.color):
            # 若root不是叶节点，寻找继承节点并与其交换
            # 若root不是叶节点，则一定同时存在左右两个子节点
            successor = root.right
            while successor.left:
                successor = successor.left
            successor.__swap(root)

        # root已是叶节点
        if root.__is_leaf() and root.color:
            # 若root是3-节点较小键，直接删除
            root.parent.left = None
            return True
        elif root.left and root.left.color:
            # 若root是3-节点较大键，将较小键接到父节点上，并改变颜色。
            root.left.__graft(root.parent, self.__is_left())
            root.left.color = False
            return True
        elif root.__steal_from_siblings() is not False:
            # 若root的兄弟节点存在3-节点
            return True
        elif root.__steal_from_parent():
            # 若root的兄弟节点均为2-节点，父节点为3-节点
            return True
        elif root.__swim_up():
            return True

    def draw(self, x=0, y=0, is_root=False, height=0, is_terminal=False):
        if not is_root and is_terminal:
            assert not self.color
        plt.axis('off')
        node = self
        if not is_root:
            while node.parent:
                node = node.parent
        circle_color = 'black' if not node.color else 'red'
        plt.scatter(x, y, color=circle_color, s=1000)
        text_color = 'white' if circle_color == 'black' else 'black'
        plt.text(x, y, node.label, fontsize='large', color=text_color, horizontalalignment='center',
                 verticalalignment='center')
        delta_x = 0.6 ** (height - 10)
        delta_y = 0.6 ** (height + 10)
        if node.left:
            assert node.left.parent == node
            line_color = 'black' if not node.left.color else 'red'
            plt.plot([x, x - delta_x], [y, y - delta_y], color=line_color)
            node.left.draw(x - delta_x, y - delta_y, is_root=True, height=height + 1)
        if node.right:
            assert node.right.parent == node
            line_color = 'black' if not node.right.color else 'red'
            plt.plot([x, x + delta_x], [y, y - delta_y], color=line_color)
            node.right.draw(x + delta_x, y - delta_y, is_root=True, height=height + 1)
        if not is_root:
            plt.show()


class RBT(object):
    def __init__(self, x):
        self.__root = Node(x)

    def add(self, x):
        result = self.__root.add(x)
        while self.__root.parent:
            self.__root = self.__root.parent
        # self.__root.draw(is_terminal=True)
        return result is not False

    def delete(self, x):
        if not self.__root.left and not self.__root.right:
            print('最后一个节点')
            return
        result = self.__root.delete(x)
        while self.__root.parent:
            self.__root = self.__root.parent
        self.__root.draw(is_terminal=True)
        return result

    def search(self, x):
        return self.__root.search(x)

    def draw(self):
        self.__root.draw()


if __name__ == '__main__':
    items = [7, 7.5, 2, 1, 3, 7.2, 7.1, 7.3, 9, 8, 10]
    rbt = RBT(items[0])
    for item in items[1:]:
        rbt.add(item)

    rbt.delete(7.1)
    # Case A: rbt.delete(3)
    # Case B: rbt.delete(1)
    # Case C-A: rbt.delete(8)
    # Case C-B: rbt.delete(7.1)

    # items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
    # rbt = RBT(items[0])
    # for item in items[1:]:
    #     rbt.add(item)
    # rbt.delete(16)
    # Case C-C: rbt.delete(1)
