import h5py
from numpy import asarray, zeros, allclose, where
import datetime



def get_madrigal_column_names(filepath):
    '''
    Return list of column name strings for madrigal HDF5 file
    
    filepath -- filepath to madrigal HDF5 file
    '''
    with h5py.File(filepath, 'r') as f:
        metadata = f['Metadata']
        data_parameters = metadata['Data Parameters']
        column_names = [column[0].decode('utf-8') for column in data_parameters.value]
        return column_names


def parse_madrigal_hdf5(filepath):  
    '''
    filepath -- path to madrigal HDF5 file
    '''  
    data = {}
    column_names = get_madrigal_column_names(filepath)
    with h5py.File(filepath, 'r') as f:
        table = f['Data']['Table Layout']
        N = len(table)
        # collect column names
        for column_name in column_names:
            data[column_name] = zeros((N,))
        # put data into table
        for i, row in enumerate(table):
            for j, column_name in enumerate(column_names):
                data[column_name][i] = row[j]
    return data
 
 
def create_2d_image(data, dtype='VIPN2'):
    '''
    Creates image of observable from parsed Madrigal HDF5 data

    data -- the data parsed from `parse_madrigal_hdf5`
    dtype -- the image data type ('VIPN2', 'DVIPN2', 'VIPE1', 'DVIPE1', 'VI72', 'DVI72', 'VI82', 'DVI82', 'PAIWL', 'PACWL', 'PBIWL', 'PBCWL', 'PCIEL', 'PCCEL', 'PDIEL', 'PDCEL')
    '''
    image = []
    recnos = data['RECNO']
    for recno in recnos:
        image.append(data[dtype][recnos == recno])
    return asarray(image).T


def get_record_altitudes(data, dtype='GDALT', validate=False):
    '''
    Creates y-axis altitude array from parsed Madrigal HDF5 data

    data -- the data parsed from `parse_madrigal_hdf5`
    dtype -- the data to use for the y axis
    validate -- whether or not to go through the data to check consistency across records
    '''
    altitudes = []
    recnos = data['RECNO']
    indices = recnos == recnos
    altitudes = data[dtype][indices]
    if validate:
        for recno in recnos[1:]:
            indices = recnos == recno
            assert(allclose(data[dtype][indices] - altitudes))
    return altitudes


def get_record_datetimes(data, tzinfo=datetime.timezone.utc):
    '''
    Creates x-axis datetime list from parsed Madrigal HDF5 data

    data -- the data parsed from `parse_madrigal_hdf5`
    '''
    datetimes = []
    recnos = data['RECNO']
    for recno in recnos:
        i = where(recnos == recno)[0][0]
        year = int(data['YEAR'][i])
        month = int(data['MONTH'][i])
        day = int(data['DAY'][i])
        hour = int(data['HOUR'][i])
        minute = int(data['MIN'][i])
        second = int(data['SEC'][i])
        datetimes.append(datetime.datetime(year, month, day, hour, minute, second, tzinfo=tzinfo))
    return datetimes
