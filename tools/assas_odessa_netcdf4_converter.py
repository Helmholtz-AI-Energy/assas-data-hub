#!/usr/bin/env python

import os
import sys
import netCDF4
import time
import argparse
import logging
import logging.handlers
import numpy as np
import pandas as pd

from datetime import datetime
from typing import List, Union
from os.path import join, dirname, abspath, basename
from pathlib import Path

from tools.assas_utils import get_duration

logger = logging.getLogger("assas." + __name__)

class AssasOdessaNetCDF4Converter:
    
    def __init__(
        self,
        input_path: str,
        output_path: Union[str, Path],
        time_points: List[float],
        astec_variable_index_file: str = 'astec_vessel_ther_variables_inr.csv',
    ) -> None:
        '''
        Initialize AssasOdessaNetCDF4Converter class.
        
        Parameters
        ----------
        input_path: str
            Input path of ASTEC binary archive to convert.
        output_path: str
            Output path of resulting netCDF4 dataset.
        time_points: List[float]
            List of time points to convert.
        astec_variable_index_file: str, optional
            CSV file containing hte information about the ASTEc varibales to extract.
        
        Returns
        ----------
        None
        '''

        self.input_path = input_path
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents = True, exist_ok = True)
        
        self.time_points = time_points
        self.variable_index = AssasOdessaNetCDF4Converter.read_astec_variable_index(
            filename = astec_variable_index_file
        )
        self.variable_strategy_mapping = { # TODO: Implement all other types
            'vessel': AssasOdessaNetCDF4Converter.parse_variable_from_odessa_in_vessel,
            'other': AssasOdessaNetCDF4Converter.parse_variable_from_odessa_in_other,
        }

    @staticmethod
    def read_astec_variable_index(
        filename: str = 'astec_variables.csv'
    )-> pd.DataFrame:
        '''
        Read names of the ASTEC variables into a dataframe.
        
        Parameters
        ----------
        filename: str
            Name of the csv file containing the ASTEC variable names.
        
        Returns
        ----------
        List[str] 
            List of strings representing the ASTEC variable names.
        '''

        csv_path = dirname(abspath(__file__))
        csv_path = join(csv_path, filename)

        dataframe = pd.read_csv(csv_path)

        logger.debug(f'Read ASTEC variables to process from file {filename}.')
        logger.debug(f'{dataframe}')

        return dataframe

    @staticmethod
    def parse_variable_from_odessa_in_vessel(
        odessa_base,# TODO: fix type hint
        variable_name: str,
    )-> np.ndarray:
        '''
        Parse the data for a ASTEC variable out of the odessa base.
        
        Parameters
        ----------
        odessa_base: pyod.lib.od_base
            Odessa base object considered for extraction.
        variable_name: str
            Name of the ASTEC variable.
        
        Returns
        ----------
        np.ndarray 
            Numpy array which contains the data for the ASTEC variable.
        '''

        logger.info(f'Parse data for ASTEC variable {variable_name}.')

        vessel = odessa_base.get('VESSEL')
        number_of_channels = vessel.len('CHANNEL')
        channel = vessel.get(f'CHANNEL 0') # Take first channel to get dimensions
        number_of_meshes = channel.len('MESH')

        array = np.zeros((number_of_channels, number_of_meshes))
        logger.debug(f'Initialized array with shape {array.shape}.')

        for channel_number in range(vessel.len('CHANNEL')):

            channel = vessel.get(f'CHANNEL {channel_number}')

            for mesh_number in range(channel.len('MESH')):

                logger.debug(f'Channel number {channel_number}, Mesh number {mesh_number}.')
                mesh_identifier = channel.get(f'MESH {mesh_number}')
                logger.debug(f'Read mesh identifier {mesh_identifier}.')

                mesh_object = vessel.get(f'MESH {mesh_identifier}')
                ther_object = mesh_object.get(f'THER')
                variable_structure = ther_object.get(f'{variable_name}')

                logger.debug(f'Collect variable structure {variable_structure}, extract data point: {variable_structure[2]}.')
                array[channel_number][mesh_number] = variable_structure[2]

        return array
    
    @staticmethod
    def parse_variable_from_odessa_in_other(
        odessa_base,# TODO: fix type hint
        variable_name: str,
    )-> np.ndarray:
        
        logger.warning(f'Not implemented yet')
        
        return np.zeros((2, 5))

    def convert_astec_variables_to_netcdf4(
        self,
        output_file: str = 'dataset.h5'
    ) -> None:
        '''
        Convert the data for given ASTEC variables from odessa into hdf5.
        
        Parameters
        ----------
        output_file : str, optional
            Name of hdf5 file. Default name is dataset.h5.
        Returns
        ----------
        None
        '''
    
        logger.info(f'Parse ASTEC data from binary with path {self.input_path}.')
        logger.info(f'Read following time_points from ASTEC archive: {self.time_points}.')

        with netCDF4.Dataset(f'{self.output_path}/{output_file}', 'w', format='NETCDF4') as ncfile:

            variable_datasets = {}
            
            ncfile.createDimension('time', len(self.time_points))
            ncfile.createDimension('channel', None)
            ncfile.createDimension('mesh', None)

            for idx, variable in self.variable_index.iterrows():
                
                variable_datasets[variable['name']] = ncfile.createVariable(
                    varname = variable['name'],
                    datatype = np.float32,
                    dimensions = ('time', 'channel', 'mesh'),
                )
                variable_datasets[variable['name']].units = variable['unit']
            
            for idx, time_point in enumerate(self.time_points):

                logger.info(f'Restore odessa base for time point {time_point}.')
                odessa_base = pyod.restore(self.input_path, time_point)

                for _, variable in self.variable_index.iterrows():
                    
                    strategy_function = self.variable_strategy_mapping[variable['type']]
                    
                    data_per_timestep = strategy_function(
                        odessa_base = odessa_base,
                        variable_name = variable['name']
                    )

                    logger.debug(f"Read data for {variable['name']} with shape {data_per_timestep.shape}.")
                    logger.debug(f'Resize dataset to ({len(self.time_points)},{data_per_timestep.shape[0]},{data_per_timestep.shape[1]}).')

                    variable_datasets[variable['name']][idx,:,:] = data_per_timestep

def parse_timepoint_argument(
        argument_string: str
    )-> List[int]:
        '''
        Parse the commandline argument --time into a list of two integers
        containing the first and the last indices of the timepoints.
        
        Parameters
        ----------
        argument_string : str
            String of commandline argument in format 'first index':'last index',
            e.g. 0:1 means just the first timepoint.
        
        Returns
        ----------
        str 
            List containing first and last indices of the timepoints.
        '''
        
        result_list = argument_string.split(':')
        
        return [int(result_list[0]), int(result_list[1])]

if __name__ == '__main__':

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        '-i',
        '--input',
        type = str,
        help = 'input path of ASTEC binary archive',
        required = True,
    )
    argparser.add_argument(
        '-o',
        '--output',
        type = str,
        help = 'output path of hdf5 file',
        required = True,
    )
    argparser.add_argument(
        '-t',
        '--times',
        type = parse_timepoint_argument,
        help = 'timepoints which will be considered for conversion',
        required = False,
    )
    argparser.add_argument(
        '-r',
        '--root',
        type = str,
        help = 'root path of ASTEC V3.1.2 installation directory',
        required = False,
        default = '/hkfs/work/workspace/scratch/ke4920-assas-hdf5/astec/astecV3.1.2'
    )
    argparser.add_argument(
        '-c',
        '--computer',
        type = str,
        help = 'type of astec computer (options: linux_64, windows_64)',
        required = False,
        default = 'linux_64'
    )
    argparser.add_argument(
        '-d',
        '--debug',
        help = 'enable debug logging for conversion',
        required = False,
        action = 'store_true'
    )
    args = argparser.parse_args()
    
    if args.debug:
        custom_level = logging.DEBUG
    else:
        custom_level = logging.INFO

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    start_time = time.time()

    logging.basicConfig(
        level = custom_level,
        format = '%(asctime)s %(process)d %(module)s %(levelname)s: %(message)s',
        handlers = [
            logging.StreamHandler(),
            logging.FileHandler(f'{args.output}/{timestamp}_{Path(__file__).stem}.log', 'w')
        ]
    )

    astec_python_location = os.path.join(args.root, "odessa","bin", args.computer + "-release", "wrap_python")
    if astec_python_location not in sys.path:
        sys.path.append(astec_python_location)

    import pyodessa as pyod
    
    time_points = pyod.get_saving_times(args.input)
    if args.times is not None:
        time_points = time_points[args.times[0]:args.times[1]]

    AssasOdessaNetCDF4Converter(
        input_path = args.input,
        output_path = args.output,
        time_points = time_points
    ).convert_astec_variables_to_netcdf4()
    
    end_time = time.time()
    duration_in_seconds = end_time - start_time
    duration_string = get_duration(duration_in_seconds)
    logger.info(f'Conversion from odessa to hdf5 took {duration_string}.')