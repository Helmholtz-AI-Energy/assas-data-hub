import unittest
import subprocess
import os

from typing import List

def execute_command(
    command_list: List[str]
)-> bool:
        
    try:
        with subprocess.Popen(command_list) as process: process.wait()
    except:
        return False
        
    return True

class AssasDataUploaderTest(unittest.TestCase):
    
    def setUp(self):
        
        self.application_path = '/root/assas-data-hub/tools/assas_data_uploader.py'
        self.user = 'ke4920'
        self.name = 'LOCA test'
        self.description = 'LOCA test archive'
            
    def test_upload_single_archive(self):
        
        source = '/root/assas-data-hub/assas_database/test/data/archive/.'
        archive = '/LOCA_12P_CL_1300_LIKE.bin'
        
        command_list = ['python', f'{self.application_path}', '-u', f'{self.user}', '-n', f'{self.name}', '-d', f'{self.description}', '-s', f'{source}', '-a', f'{archive}']
        
        self.assertTrue(execute_command(command_list))
        
    def test_upload_single_archive_debug(self):
        
        source = '/root/assas-data-hub/assas_database/test/data/archive/.'
        archive = '/LOCA_12P_CL_1300_LIKE.bin'
        
        command_list = ['python', f'{self.application_path}', '-u', f'{self.user}', '-n', f'{self.name}', '-d', f'{self.description}', '-s', f'{source}', '-a', f'{archive}', '--debug']
        
        self.assertTrue(execute_command(command_list))
        
    def test_upload_single_archive_reload(self):
        
        source = '/root/assas-data-hub/assas_database/test/data/archive/.'
        archive = '/LOCA_12P_CL_1300_LIKE.bin'
        upload_uuid_str = 'a8b70f99-71b9-4bda-9f74-a5d9a74834d0'
        name = self.name + ' resumed'
        description = self.description + ' resumed'
        
        command_list = ['python', f'{self.application_path}', '-u', f'{self.user}', '-n', f'{name}', '-d', f'{description}', '-s', f'{source}', '-a', f'{archive}', '-i', f'{upload_uuid_str}']
        
        self.assertTrue(execute_command(command_list))
        
    def test_upload_multiple_archives_debug(self):
        
        source = '/root/assas-data-hub/assas_database/test/data/archive_tree/.'
        archives = '/sample_1/LOCA_12P_CL_1300_LIKE.bin, /sample_2/LOCA_12P_CL_1300_LIKE.bin, /sample_3/LOCA_12P_CL_1300_LIKE.bin'
        
        command_list = ['python', f'{self.application_path}', '-u', f'{self.user}', '-n', f'{self.name}', '-d', f'{self.description}', '-s', f'{source}', '-a', f'{archives}', '--debug']
        
        self.assertTrue(execute_command(command_list))
    
    def test_upload_multiple_archives(self):
        
        source = '/root/assas-data-hub/assas_database/test/data/archive_tree/.'
        archives = '/sample_1/LOCA_12P_CL_1300_LIKE.bin, /sample_2/LOCA_12P_CL_1300_LIKE.bin, /sample_3/LOCA_12P_CL_1300_LIKE.bin'
        
        command_list = ['python', f'{self.application_path}', '-u', f'{self.user}', '-n', f'{self.name}', '-d', f'{self.description}', '-s', f'{source}', '-a', f'{archives}']
        
        self.assertTrue(execute_command(command_list))
    
    def test_upload_multiple_archives_reload(self):
        
        source = '/root/assas-data-hub/assas_database/test/data/archive_tree/.'
        archives = '/sample_1/LOCA_12P_CL_1300_LIKE.bin, /sample_2/LOCA_12P_CL_1300_LIKE.bin, /sample_3/LOCA_12P_CL_1300_LIKE.bin'
        upload_uuid_str = '54c02d81-25f9-4047-9381-878eedaf2abc'
        name = self.name + ' resumed'
        description = self.description + ' resumed'
        
        command_list = ['python', f'{self.application_path}', '-u', f'{self.user}', '-n', f'{name}', '-d', f'{description}', '-s', f'{source}', '-a', f'{archives}', '-i', f'{upload_uuid_str}']
        
        self.assertTrue(execute_command(command_list))