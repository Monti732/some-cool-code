from PIL import Image
import imageio
import glob

images = [Image.open(img) for img in sorted(glob.glob("*.png"))]  # Загружаем все PNG-файлы по порядку
images[0].save("animation.gif", save_all=True, append_images=images[1:], duration=100, loop=0)


