import yaml

def get_spec():
    spec_str = ''
    with open('waggleprotocol_spec.yml', 'r') as file:
        spec_str = file.read()

    spec = {}
    contents = yaml.load(spec_str)
    for packet in contents:
        params = packet['params']
        for param in params:
            assert 'name' in param
            assert 'length' in param
            assert 'format' in param
            assert 'conversion' in param
        spec[packet['id']] = packet['params']
    return spec

spec = get_spec()