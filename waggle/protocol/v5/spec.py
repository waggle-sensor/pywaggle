import yaml

from . import waggleprotocol_spec

def get_spec(spec_str):
    spec = {}
    contents = yaml.load(spec_str)
    for packet in contents:
        assert 'conversion' in packet
        spec[packet['id']] = {}
        spec[packet['id']]['conversion'] = packet['conversion']
        params = packet['params']
        for param in params:
            assert 'name' in param
            assert 'length' in param
            assert 'format' in param
            # assert 'conversion' in param
        spec[packet['id']]['params'] = packet['params']
    return spec

spec = get_spec(waggleprotocol_spec.waggleprotocol_spec)