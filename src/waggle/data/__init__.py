# Maintaining backwards compatibility by providing waggle.data.open_data_source.
# NOTE We wrap this instead of directly importing it to avoid additional large imports in .data_shim.
def open_data_source(*args, **kwargs):
    from .data_shim import open_data_source as data_shim_open_data_source
    return data_shim_open_data_source(*args, **kwargs)
