from geoplotlib.layers import BaseLayer
from geoplotlib.core import BatchPainter
import geoplotlib
from geoplotlib.colors import colorbrewer
from geoplotlib.utils import epoch_to_str, BoundingBox, read_csv

class TrailsLayer(BaseLayer):

    def __init__(self):
        self.data = read_csv('alex.csv')
        self.cmap = colorbrewer(self.data['runner_id'], alpha=220)
        self.t = self.data['timestamp'].min()
        self.painter = BatchPainter()


    def draw(self, proj, mouse_x, mouse_y, ui_manager):
        self.painter = BatchPainter()
        df = self.data.where((self.data['timestamp'] > self.t) & (self.data['timestamp'] <= self.t + 15*60))

        for taxi_id in set(df['runner_id']):
            grp = df.where(df['runner_id'] == taxi_id)
            self.painter.set_color(self.cmap[taxi_id])
            x, y = proj.lonlat_to_screen(grp['lon'], grp['lat'])
            self.painter.points(x, y, 10)

        self.t += 2*60

        if self.t > self.data['timestamp'].max():
            self.t = self.data['timestamp'].min()

        self.painter.batch_draw()
        ui_manager.info(epoch_to_str(self.t))

    # this should get modified as well moving forward
    def bbox(self):
        return BoundingBox(north=37.801421, west=-122.517339, south=37.730097, east=-122.424474)

geoplotlib.add_layer(TrailsLayer())
geoplotlib.show()