# TODO

1. bug: update key press when keyup
1. play时在infobar上显示音名、音程关系、和弦

    当前单音、与上一个单音的音程、当前和声（双音、三音、四音）

2. 锁定hightlight notes为当前正play的音

3. 完善staff的beam
3. use pdf staff, do not draw staff by self

## Done

2. while playing, page auto scroll
4. draw multi staff. use touchpad to scroll screen
5. bug: hide the left note after it's completely out

拟用pyglet，经测试，mac上直接用sprite绘制所有元素性能不足。用batch绘制所有元素性能也不足，并需要对绘图过程做较多改动。

已测试方案：
1. 预先绘出单行所有五线谱图，用此图创建n行重复sprite。每一周期更新sprite。这样能将sprite减少到10个以下。（放弃pyglet）
2. 依然用pygame.Surface绘制每周期图片，用opengl模式更新到屏幕。FPS可升到60。（采用）


# DOC

see:
http://lists.gnu.org/archive/html/lilypond-user/2014-10/msg00799.html

/Applications/LilyPond.app/Contents/Resources/bin/midi2ly
/Applications/LilyPond.app/Contents/Resources/bin/lilypond
