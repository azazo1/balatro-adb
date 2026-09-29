# 读图方法

截图分辨率很高 (2400x1080), 直接读原图既浪费上下文又看不清细节. 固定流程是: 先缩放看全局, 再裁剪放大看局部, 需要坐标时叠加网格.

## 截图

```shell
adb -s <serial> exec-out screencap -p > shot.png
```

必须用 `exec-out`; 用 `adb shell screencap -p > file` 会被换行符转换破坏 PNG (尤其在 macOS 上).

## 缩放

macOS 自带 `sips`:

```shell
sips -Z 900 shot.png --out shot-small.png      # 长边缩到 900 px
```

用 Pillow 更灵活:

```python
from PIL import Image
im = Image.open('shot.png')
im.resize((1300, 585), Image.LANCZOS).save('view.png')
```

经验值: 全局看用 1200-1400 px 宽, 单看一处细节用裁剪 + 2-3 倍放大.

## 裁剪放大

```python
from PIL import Image
im = Image.open('shot.png')
im.crop((300, 400, 760, 700)).resize((690, 450), Image.LANCZOS).save('panel.png')
```

裁剪框是原图坐标, 之后按原图坐标比例换算回点击坐标, 不要拿放大后的像素当坐标用.

## 叠加坐标网格 (定位元素位置的关键手法)

看不清某个元素的确切坐标时, 画网格再读:

```python
from PIL import Image, ImageDraw
im = Image.open('shot.png').convert('RGB')
d = ImageDraw.Draw(im)
for x in range(0, im.width, 100):
    d.line([(x, 0), (x, im.height)], fill=(255, 0, 255), width=2)
    d.text((x + 4, 6), str(x), fill=(255, 0, 255))
for y in range(0, im.height, 100):
    d.line([(0, y), (im.width, y)], fill=(0, 255, 255), width=2)
    d.text((6, y + 4), str(y), fill=(0, 255, 255))
im.save('grid.png')
```

- 网格间距按目标精度选: 全局 100 px, 局部 50 px.
- 标注文字要画在缩放后仍可读的位置 (图左上角每 100 px 一个数字).
- 读图时把网格图缩到 1000-1200 px 宽, 既能看清数字也能对齐位置.

## 验证坐标是否落在目标上

定位完成后, 先把打算点击的点画在图上再确认一遍, 避免点错:

```python
from PIL import Image, ImageDraw
im = Image.open('shot.png').convert('RGB')
d = ImageDraw.Draw(im)
for x, y in [(773, 690), (898, 690), (1031, 690)]:
    d.ellipse((x - 14, y - 14, x + 14, y + 14), outline=(255, 0, 255), width=4)
im.save('verify.png')
```

这一步几乎零成本, 但能挡掉 "点错牌" 这类代价很大的错误.

## 判断元素是否被选中 (状态检测)

对无法读文字的图形元素, 用像素特征判断状态. 例如判断卡牌是否被点起:

```python
import numpy as np
from PIL import Image

def top_edge(path, x):
    a = np.asarray(Image.open(path).convert('RGB')).astype(int)
    col = a[520:900, x]
    light = (col[:, 0] > 170) & (col[:, 1] > 165) & (col[:, 2] > 150)
    idx = np.flatnonzero(light)
    return int(idx[0] + 520) if idx else None
```

比较操作前后同一列的顶边 y 值, 差值约等于选中位移量即为已选中.

注意事项:

- 界面上的浮层 (提示框, 弹窗) 也是浅色, 会干扰这类检测; 检测窗口要避开它们, 或先裁掉浮层区域.
- 换个采样列 (例如取卡牌左侧) 往往就能避开浮层.
