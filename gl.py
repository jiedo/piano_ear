#encoding: utf8

import math
import pyglet
import time
from pyglet.gl import *
from pyglet.window import key # 键盘常量，事件


class Window(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        # *args,化序列为位置参数：(1,2) -> func(1,2)
        # **kwargs,化字典为关键字参数：{'a':1,'b':2} -> func(a=1,b=2)
        super(Window, self).__init__(*args, **kwargs)
        self.batch = pyglet.graphics.Batch()
        self.rotation = (0, 0)
        self.position = (0, 0, 0) # 开始位置在地图中间
        self.reticle = None

        # 游戏窗口左上角的label参数设置
        self.label = pyglet.text.Label('', font_name='Arial', font_size=18,
            x=10, y=self.height - 10, anchor_x='left', anchor_y='top',
            color=(255, 0, 0, 255))

        vertex_data = (34, 53, 44, 22, 422, 64, 42, 44)
        self.batch.add(4, GL_LINES, None,
                       ('v2i/static', vertex_data),
                       ('c4B', (0, 255, 255, 255) * 4))


        # GL_LINE_LOOP
        # GL_QUADS
        vertex_data = (134, 153, 204, 122, 202, 204, 102, 204, 234, 253, 304, 222, 302, 304, 202, 304)
        self.batch.add(8, GL_TRIANGLE_FAN, None,
                       ('v2i/static', vertex_data),
                       ('c4B', (0, 255, 255, 0) * 8))


        self.n = 0

        pyglet.clock.schedule_interval(self.update, 1.0 / 100)# 每秒刷新60次


    # 每1/60秒调用一次进行更新
    def update(self, dt):
        print "update", dt
        self.n = 0
        time.sleep(0.1)
        print "n is", self.n
        pass

    # 重写Window的on_draw函数
    # 当窗口需要被重绘时，事件循环(EventLoop)就会调度该事件
    def on_draw(self):
        # # Clear buffers
        # glClear(GL_COLOR_BUFFER_BIT)

        # # Draw some stuff
        # #glBegin(GL_POINTS)
        # #glBegin(GL_LINES)
        # #glBegin(GL_LINE_STRIP)
        # glBegin(GL_LINE_LOOP)
        # glVertex2i(0, 0)
        # glVertex2i(35, 100)
        # glVertex2i(100, 150)
        # glVertex2i(200, 350)
        # glEnd()


        # # Draw outlines only
        # glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # # Draw some stuff
        # glBegin(GL_TRIANGLES)
        # glVertex2i(50, 50)
        # glVertex2i(75, 100)
        # glVertex2i(200, 200)
        # glEnd()
        print "drawing"
        self.clear()
        # self.set_3d() # 进入3d模式
        # glColor3d(0, 1, 0)

        self.set_2d() # 进入2d模式
        self.batch.draw() # 将batch中保存的顶点列表绘制出来
        self.draw_label() # 绘制label
        self.draw_reticle() # 绘制窗口中间的十字


    # 窗口大小变化响应事件
    def on_resize(self, width, height):
        # label的纵坐标
        self.label.y = height - 10
        # reticle更新，包含四个点，绘制成两条直线
        if self.reticle:
            self.reticle.delete()
        x, y = self.width / 2, self.height / 2
        n = 10
        self.reticle = pyglet.graphics.vertex_list(4,
            ('v2i', (x - n, y, x + n, y, x, y - n, x, y + n))
        )


    # 绘制游戏窗口中间的十字，一条横线加一条竖线
    def draw_reticle(self):
        glColor3d(0, 0, 1)
        self.reticle.draw(GL_LINES)


    def draw_label(self): # 显示帧率，当前位置坐标，显示的方块数及总共的方块数
        x, y, z = self.position
        text = '%02d (%.2f, %.2f, %.2f)' % (
            pyglet.clock.get_fps(), x, y, z)
        #print text
        self.label.text = text
        #print self.label
        self.label.draw() # 绘制label的text


    # 按下键盘事件，长按W，S，A，D键将不断改变坐标
    def on_key_press(self, symbol, modifiers):
        self.n += 3

        # Draw some stuff
        glBegin(GL_TRIANGLES)
        glVertex2i(10+self.n, 20)
        glVertex2i(15+self.n, 30)
        glVertex2i(10+self.n, 40)
        glEnd()

        time.sleep(0.1)
        print symbol, modifiers
        if symbol == key.W: # opengl坐标系：z轴垂直平面向外，x轴向右，y轴向上
            pass


    # 释放按键事件
    def on_key_release(self, symbol, modifiers):
        print symbol, modifiers
        if symbol == key.W: # 按键释放时，各方向退回一个单位
            pass



    def set_2d(self):
        width, height = self.get_size()
        glDisable(GL_DEPTH_TEST)
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, width, 0, height, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()


    def set_3d(self):
        width, height = self.get_size()
        glEnable(GL_DEPTH_TEST)
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(65.0, width / float(height), 0.1, 60.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        x, y = self.rotation
        glRotatef(x, 0, 1, 0)
        glRotatef(-y, math.cos(math.radians(x)), 0, math.sin(math.radians(x)))
        x, y, z = self.position
        glTranslatef(-x, -y, -z)



def main():
    window = Window(width=800, height=600, caption='Pyglet', resizable=False) # 创建游戏窗口
    window.set_exclusive_mouse(True) # 隐藏鼠标光标，将所有的鼠标事件都绑定到此窗口
    pyglet.app.run()


if __name__ == '__main__':
    main()
