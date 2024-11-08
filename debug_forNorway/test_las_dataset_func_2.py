import yaml

from torch_points3d.datasets.base_dataset import BaseDataset
from torch_points3d.datasets.instance import las_dataset as ls

with open('/home/nibio/DPCR-AGB/torch-points3d/conf/data/instance/NFI/default.yaml') as file:
    dataset_opt = yaml.safe_load(file)

class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

dataset_opt2 = AttrDict(**dataset_opt)

print(dataset_opt2['dataroot'])
print(dataset_opt2.dataroot)

dataset = ls.LasDataset(dataset_opt2)